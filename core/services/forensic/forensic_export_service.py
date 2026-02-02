"""
Forensic Export Service
Handles generation and signing of forensic-grade PDF exports.

Ensures:
- Case must be CLOSED before export
- Only one signed document per case
- Digital signature with PAdES
- Integrity hash chain linkage
- TSA timestamping
- Full audit trail
"""
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
import os

from django.conf import settings
from django.utils import timezone

from core.models_forensic import (
    ForensicEntityType,
    ForensicEventType,
    ForensicDocumentType,
    ForensicIntegrityHash,
    ForensicDocumentSignature,
    AuditEventType,
)
from core.forensic_utils import (
    sha256_hex,
    create_integrity_hash,
    create_audit_log_entry,
)
from core.services.forensic.forensic_transaction_guard import (
    get_client_ip,
    get_user_agent,
)
from core.services.forensic.forensic_review_service import TSAService


# =============================================================================
# EXCEPTIONS
# =============================================================================

class ForensicExportError(Exception):
    """Base exception for forensic export errors."""
    pass


class CaseNotClosedError(ForensicExportError):
    """Raised when case is not closed for export."""
    
    def __init__(self, case_id: int, current_status: str):
        self.case_id = case_id
        self.current_status = current_status
        super().__init__(
            f"Case {case_id} must be CLOSED for export (current: {current_status})"
        )


class CaseNotFoundError(ForensicExportError):
    """Raised when case not found."""
    
    def __init__(self, case_id: int):
        self.case_id = case_id
        super().__init__(f"Case {case_id} not found")


class PDFGenerationError(ForensicExportError):
    """Raised when PDF generation fails."""
    pass


class SigningError(ForensicExportError):
    """Raised when document signing fails."""
    pass


# =============================================================================
# RESULT DATA CLASSES
# =============================================================================

@dataclass
class ForensicExportResult:
    """Result of a forensic export operation."""
    success: bool
    case_id: int
    document_type: str
    signed_pdf_path: str
    document_hash: str
    signed_document_hash: str
    chain_hash: str
    tsa_timestamp: datetime
    signature_timestamp: datetime
    certificate_serial: str
    export_count: int
    is_redownload: bool
    message: str


# =============================================================================
# PDF GENERATOR (Abstract)
# =============================================================================

class ForensicPDFGenerator:
    """
    Abstract PDF generator for forensic case exports.
    
    In production, implement with actual PDF library (ReportLab, WeasyPrint, etc.)
    """
    
    def generate_case_pdf(
        self,
        case_id: int,
        case_data: dict,
        closure_chain_hash: str,
    ) -> bytes:
        """
        Generate PDF content for a case.
        
        Args:
            case_id: The case ID
            case_data: Complete case data
            closure_chain_hash: Hash to embed in PDF
            
        Returns:
            PDF file content as bytes
        """
        # In production, generate actual PDF
        # For now, create placeholder content
        content = f"""
FORENSIC CASE EXPORT
====================

Case ID: {case_id}
Generated: {timezone.now().isoformat()}
Closure Chain Hash: {closure_chain_hash}

EMPLOYEE INFORMATION
--------------------
Employee ID: {case_data.get('employee_id', 'N/A')}
Employee Name: {case_data.get('employee_name', 'N/A')}
Date: {case_data.get('date', 'N/A')}

COMPARISON V1 vs V2
-------------------
V1 Net Minutes: {case_data.get('v1_net_minutes', 'N/A')}
V2 Net Minutes: {case_data.get('v2_net_minutes', 'N/A')}
Difference: {case_data.get('difference_minutes', 'N/A')}
Severity: {case_data.get('severity', 'N/A')}

ANALYSIS
--------
Primary Reason: {case_data.get('primary_reason', 'N/A')}
Confidence: {case_data.get('confidence', 'N/A')}
Explanation: {case_data.get('explanation', 'N/A')}

DECISION
--------
Decision: {case_data.get('decision', 'N/A')}
Decision Notes: {case_data.get('decision_notes', 'N/A')}
Decided By: {case_data.get('reviewer_name', 'N/A')}
Decided At: {case_data.get('decided_at', 'N/A')}

CLOSURE
-------
Closed By: {case_data.get('closed_by', 'N/A')}
Closed At: {case_data.get('closed_at', 'N/A')}

FORENSIC METADATA
-----------------
Engine Version: {case_data.get('engine_version', 'N/A')}
Closure Chain Hash: {closure_chain_hash}

---
This document is digitally signed.
Verify at: /api/forensic/export/verify
"""
        return content.encode('utf-8')


# =============================================================================
# DOCUMENT SIGNER (Abstract)
# =============================================================================

class ForensicDocumentSigner:
    """
    Abstract document signer for PAdES signatures.
    
    In production, implement with actual signing library
    (pyHanko, endesive, or external HSM).
    """
    
    def __init__(self):
        # In production, load certificate from secure storage
        self.certificate_serial = "DEV-CERT-001"
        self.certificate_issuer = "Development CA"
        self.certificate_expiry = datetime(2030, 12, 31)
        self.signature_algorithm = "SHA256withRSA"
    
    def sign_document(
        self,
        pdf_content: bytes,
        metadata: dict,
    ) -> bytes:
        """
        Sign PDF document with PAdES signature.
        
        Args:
            pdf_content: Original PDF content
            metadata: Metadata to embed in signature
            
        Returns:
            Signed PDF content
        """
        # In production, apply actual PAdES signature
        # For now, append signature placeholder
        signature_block = f"""

====== DIGITAL SIGNATURE ======
Certificate: {self.certificate_serial}
Issuer: {self.certificate_issuer}
Algorithm: {self.signature_algorithm}
Signed At: {timezone.now().isoformat()}
Document Hash: {sha256_hex(pdf_content)}
Metadata: {metadata}
==============================
"""
        return pdf_content + signature_block.encode('utf-8')
    
    def get_certificate_info(self) -> dict:
        """Get certificate information."""
        return {
            'serial': self.certificate_serial,
            'issuer': self.certificate_issuer,
            'expiry': self.certificate_expiry,
            'algorithm': self.signature_algorithm,
        }


# =============================================================================
# FORENSIC EXPORT SERVICE
# =============================================================================

class ForensicExportService:
    """
    Service for generating forensic-grade signed PDF exports.
    
    Ensures:
    1. Case must be CLOSED
    2. Only one signed export per case (immutable)
    3. Re-downloads return original document
    4. Full chain linkage and TSA timestamping
    5. Complete audit trail
    """
    
    # Default export storage directory
    EXPORT_STORAGE_DIR = getattr(
        settings, 
        'FORENSIC_EXPORT_DIR', 
        Path(settings.BASE_DIR) / 'forensic_exports'
    )
    
    def __init__(self):
        self.pdf_generator = ForensicPDFGenerator()
        self.signer = ForensicDocumentSigner()
        self.tsa = TSAService()
        
        # Ensure storage directory exists
        os.makedirs(self.EXPORT_STORAGE_DIR, exist_ok=True)
    
    def export_case_pdf_forensic(
        self,
        case_id: int,
        actor,
        request=None,
    ) -> ForensicExportResult:
        """
        Export case as signed PDF with forensic tracking.
        
        Rules:
        1. Case MUST be CLOSED
        2. If signed export exists → return original (increment count)
        3. First export:
           - Generate base PDF
           - Embed closure_chain_hash
           - Sign with PAdES
           - Store immutably
           - Create ForensicDocumentSignature
           - Create integrity hash node for EXPORT
           - TSA timestamp for document hash
           - Audit log entry
        
        Args:
            case_id: The case ID to export
            actor: User requesting export
            request: Django request for IP/user-agent
            
        Returns:
            ForensicExportResult with document path and metadata
        """
        from core.models_shadow import ShadowDifferenceAnalysis, ShadowReviewDecision
        
        # 1. Check if signed export already exists
        existing_signature = ForensicDocumentSignature.objects.filter(
            case_id=case_id,
            document_type=ForensicDocumentType.CASE_EXPORT,
        ).first()
        
        if existing_signature:
            return self._handle_redownload(existing_signature, actor, request)
        
        # 2. Load and validate case data
        try:
            analysis = ShadowDifferenceAnalysis.objects.select_related(
                'shadow_calculation'
            ).get(pk=case_id)
        except ShadowDifferenceAnalysis.DoesNotExist:
            raise CaseNotFoundError(case_id)
        
        try:
            review = ShadowReviewDecision.objects.get(analysis_id=case_id)
        except ShadowReviewDecision.DoesNotExist:
            raise ForensicExportError(f"No review found for case {case_id}")
        
        # 3. Verify case is CLOSED
        if review.status != 'CLOSED':
            raise CaseNotClosedError(case_id, review.status)
        
        # 4. Get closure chain hash
        closure_hash_node = ForensicIntegrityHash.objects.filter(
            case_id=case_id,
            entity_type=ForensicEntityType.CLOSURE,
        ).order_by('-created_at').first()
        
        if not closure_hash_node:
            raise ForensicExportError(
                f"No closure hash found for case {case_id}. "
                "Case may not have been closed through forensic service."
            )
        
        closure_chain_hash = closure_hash_node.chain_hash
        
        # 5. Build case data for PDF
        shadow = analysis.shadow_calculation
        case_data = self._build_case_data(analysis, review, shadow)
        
        # 6. Generate base PDF
        pdf_content = self.pdf_generator.generate_case_pdf(
            case_id=case_id,
            case_data=case_data,
            closure_chain_hash=closure_chain_hash,
        )
        
        document_hash = sha256_hex(pdf_content)
        
        # 7. Sign document
        signed_pdf = self.signer.sign_document(
            pdf_content=pdf_content,
            metadata={
                'case_id': case_id,
                'closure_chain_hash': closure_chain_hash,
                'export_timestamp': timezone.now().isoformat(),
            }
        )
        
        signed_document_hash = sha256_hex(signed_pdf)
        
        # 8. Store signed PDF
        pdf_filename = f"case_{case_id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = Path(self.EXPORT_STORAGE_DIR) / pdf_filename
        
        with open(pdf_path, 'wb') as f:
            f.write(signed_pdf)
        
        # 9. Create ForensicDocumentSignature record
        cert_info = self.signer.get_certificate_info()
        signature_timestamp = timezone.now()
        
        signature_record = ForensicDocumentSignature.objects.create(
            case_id=case_id,
            document_type=ForensicDocumentType.CASE_EXPORT,
            document_hash=document_hash,
            signed_document_hash=signed_document_hash,
            signature_timestamp=signature_timestamp,
            certificate_serial=cert_info['serial'],
            certificate_issuer=cert_info['issuer'],
            certificate_expiry=cert_info['expiry'],
            signature_algorithm=cert_info['algorithm'],
            signed_pdf_path=str(pdf_path),
            first_export_at=timezone.now(),
            export_count=1,
        )
        
        # 10. Create integrity hash node for EXPORT
        previous_hash = closure_chain_hash
        
        export_content = {
            'case_id': case_id,
            'closure_chain_hash': closure_chain_hash,
            'document_hash': document_hash,
            'signed_document_hash': signed_document_hash,
            'signature_timestamp': signature_timestamp.isoformat(),
            'certificate_serial': cert_info['serial'],
            'exported_by_id': actor.id,
        }
        
        integrity_hash = create_integrity_hash(
            entity_type=ForensicEntityType.EXPORT,
            entity_id=signature_record.id,
            case_id=case_id,
            content_data=export_content,
            previous_hash=previous_hash,
        )
        
        # Update signature record with integrity hash reference
        signature_record.integrity_hash_id = integrity_hash.id
        ForensicDocumentSignature.objects.filter(pk=signature_record.pk).update(
            integrity_hash_id=integrity_hash.id
        )
        
        # 11. TSA timestamp for export
        tsa_token = self.tsa.timestamp(
            hash_to_seal=signed_document_hash,
            entity_type=ForensicEntityType.EXPORT,
            entity_id=signature_record.id,
            event_type=ForensicEventType.EXPORTED,
        )
        
        # 12. Audit log entry
        create_audit_log_entry(
            event_type=AuditEventType.CASE_EXPORTED,
            entity_type='ForensicDocumentSignature',
            entity_id=signature_record.id,
            actor_id=actor.id,
            event_data={
                'case_id': case_id,
                'document_hash': document_hash,
                'signed_document_hash': signed_document_hash,
                'certificate_serial': cert_info['serial'],
                'is_first_export': True,
            },
            actor_ip=get_client_ip(request) if request else None,
            actor_user_agent=get_user_agent(request) if request else None,
        )
        
        return ForensicExportResult(
            success=True,
            case_id=case_id,
            document_type=ForensicDocumentType.CASE_EXPORT,
            signed_pdf_path=str(pdf_path),
            document_hash=document_hash,
            signed_document_hash=signed_document_hash,
            chain_hash=integrity_hash.chain_hash,
            tsa_timestamp=tsa_token.tsa_timestamp,
            signature_timestamp=signature_timestamp,
            certificate_serial=cert_info['serial'],
            export_count=1,
            is_redownload=False,
            message='Case exported successfully with digital signature',
        )
    
    def _handle_redownload(
        self,
        existing: ForensicDocumentSignature,
        actor,
        request,
    ) -> ForensicExportResult:
        """
        Handle re-download of existing signed document.
        
        - Returns same document
        - Increments export count
        - Creates audit log entry
        """
        # Increment export count
        existing.increment_export_count()
        
        # Audit log for redownload
        create_audit_log_entry(
            event_type=AuditEventType.CASE_EXPORTED,
            entity_type='ForensicDocumentSignature',
            entity_id=existing.id,
            actor_id=actor.id,
            event_data={
                'case_id': existing.case_id,
                'document_hash': existing.document_hash,
                'signed_document_hash': existing.signed_document_hash,
                'is_redownload': True,
                'export_count': existing.export_count,
            },
            actor_ip=get_client_ip(request) if request else None,
            actor_user_agent=get_user_agent(request) if request else None,
        )
        
        # Get integrity hash if exists
        chain_hash = ''
        if existing.integrity_hash_id:
            try:
                hash_node = ForensicIntegrityHash.objects.get(
                    pk=existing.integrity_hash_id
                )
                chain_hash = hash_node.chain_hash
            except ForensicIntegrityHash.DoesNotExist:
                pass
        
        return ForensicExportResult(
            success=True,
            case_id=existing.case_id,
            document_type=existing.document_type,
            signed_pdf_path=existing.signed_pdf_path,
            document_hash=existing.document_hash,
            signed_document_hash=existing.signed_document_hash,
            chain_hash=chain_hash,
            tsa_timestamp=existing.created_at,  # Original timestamp
            signature_timestamp=existing.signature_timestamp,
            certificate_serial=existing.certificate_serial,
            export_count=existing.export_count,
            is_redownload=True,
            message='Returning existing signed document (re-download)',
        )
    
    def _build_case_data(self, analysis, review, shadow) -> dict:
        """Build case data dictionary for PDF generation."""
        return {
            'employee_id': shadow.employee_id if shadow else None,
            'employee_name': '',  # Would be populated from Employee model
            'date': str(shadow.date) if shadow else '',
            'v1_net_minutes': shadow.v1_net_minutes if shadow else None,
            'v2_net_minutes': shadow.v2_net_minutes if shadow else None,
            'difference_minutes': analysis.total_difference_minutes if hasattr(analysis, 'total_difference_minutes') else None,
            'severity': analysis.severity if hasattr(analysis, 'severity') else None,
            'primary_reason': analysis.primary_reason if hasattr(analysis, 'primary_reason') else None,
            'confidence': analysis.confidence_level if hasattr(analysis, 'confidence_level') else None,
            'explanation': analysis.explanation if hasattr(analysis, 'explanation') else '',
            'decision': review.decision if review else None,
            'decision_notes': review.decision_notes if review else '',
            'reviewer_name': review.reviewer.username if review and hasattr(review, 'reviewer') and review.reviewer else '',
            'decided_at': review.decided_at.isoformat() if review and review.decided_at else '',
            'closed_by': review.closed_by.username if review and hasattr(review, 'closed_by') and review.closed_by else '',
            'closed_at': review.closed_at.isoformat() if review and review.closed_at else '',
            'engine_version': shadow.engine_version if shadow else '',
        }
    
    def verify_export(self, case_id: int) -> dict:
        """
        Verify the integrity of an exported document.
        
        Args:
            case_id: The case ID to verify
            
        Returns:
            Verification result with integrity status
        """
        from core.forensic_utils import verify_chain_for_case
        
        signature = ForensicDocumentSignature.objects.filter(
            case_id=case_id,
            document_type=ForensicDocumentType.CASE_EXPORT,
        ).first()
        
        if not signature:
            return {
                'valid': False,
                'error': 'No signed document found for case',
                'case_id': case_id,
            }
        
        # Verify file exists
        if not os.path.exists(signature.signed_pdf_path):
            return {
                'valid': False,
                'error': 'Signed PDF file not found',
                'case_id': case_id,
                'expected_path': signature.signed_pdf_path,
            }
        
        # Verify file hash
        with open(signature.signed_pdf_path, 'rb') as f:
            current_hash = sha256_hex(f.read())
        
        if current_hash != signature.signed_document_hash:
            return {
                'valid': False,
                'error': 'Document hash mismatch - file may have been modified',
                'case_id': case_id,
                'stored_hash': signature.signed_document_hash,
                'current_hash': current_hash,
            }
        
        # Verify chain integrity
        chain_result = verify_chain_for_case(case_id)
        
        if not chain_result.chain_intact:
            return {
                'valid': False,
                'error': 'Integrity chain broken',
                'case_id': case_id,
                'chain_result': {
                    'total_nodes': chain_result.total_nodes,
                    'invalid_nodes': chain_result.invalid_nodes,
                    'first_break_at': chain_result.first_break_at,
                }
            }
        
        return {
            'valid': True,
            'case_id': case_id,
            'document_hash': signature.signed_document_hash,
            'signature_timestamp': signature.signature_timestamp.isoformat(),
            'certificate_serial': signature.certificate_serial,
            'certificate_issuer': signature.certificate_issuer,
            'export_count': signature.export_count,
            'chain_nodes': chain_result.total_nodes,
            'message': 'Document integrity verified',
        }
