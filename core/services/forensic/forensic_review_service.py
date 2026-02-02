"""
Forensic Review Service
Wraps the Shadow Review Workflow with forensic enforcement.

All review operations (start, decision, close) are processed through
the ForensicTransactionGuard to ensure:
- Idempotency
- Distributed locking
- Integrity hash chain
- TSA timestamping
- Audit logging
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, Dict

from django.db import transaction
from django.utils import timezone

from core.models_forensic import (
    ForensicEntityType,
    ForensicEventType,
    ForensicIntegrityHash,
    ForensicTimestampToken,
    AuditEventType,
)
from core.forensic_utils import (
    canonical_json,
    sha256_hex,
    compute_chain_hash,
    create_integrity_hash,
    create_audit_log_entry,
)
from core.services.forensic.forensic_transaction_guard import (
    ForensicTransactionGuard,
    ForensicOperationContext,
    ForensicOperationResult,
    get_client_ip,
    get_user_agent,
)


# =============================================================================
# EXCEPTIONS
# =============================================================================

class ForensicReviewError(Exception):
    """Base exception for forensic review errors."""
    pass


class AnalysisNotFoundError(ForensicReviewError):
    """Raised when analysis record not found."""
    
    def __init__(self, analysis_id: int):
        self.analysis_id = analysis_id
        super().__init__(f"Analysis {analysis_id} not found")


class InvalidReviewStateError(ForensicReviewError):
    """Raised when review is in invalid state for operation."""
    
    def __init__(self, current_state: str, required_states: list):
        self.current_state = current_state
        self.required_states = required_states
        super().__init__(
            f"Invalid state '{current_state}'. Required: {required_states}"
        )


class UnauthorizedReviewerError(ForensicReviewError):
    """Raised when user is not the assigned reviewer."""
    
    def __init__(self, user_id: int, assigned_reviewer_id: int):
        self.user_id = user_id
        self.assigned_reviewer_id = assigned_reviewer_id
        super().__init__(
            f"User {user_id} is not the assigned reviewer ({assigned_reviewer_id})"
        )


class CaseNotClosedError(ForensicReviewError):
    """Raised when attempting export before case is closed."""
    
    def __init__(self, analysis_id: int, current_state: str):
        self.analysis_id = analysis_id
        self.current_state = current_state
        super().__init__(
            f"Case {analysis_id} must be CLOSED before export (current: {current_state})"
        )


# =============================================================================
# RESULT DATA CLASSES
# =============================================================================

@dataclass
class ForensicReviewResult:
    """Result of a forensic review operation."""
    success: bool
    analysis_id: int
    status: str
    status_label: str
    chain_hash: str
    tsa_timestamp: Optional[datetime]
    audit_sequence: int
    from_cache: bool
    message: str


@dataclass
class ForensicDecisionResult:
    """Result of a forensic decision submission."""
    success: bool
    analysis_id: int
    status: str
    decision: str
    decision_label: str
    chain_hash: str
    tsa_timestamp: datetime
    audit_sequence: int
    is_closeable: bool
    from_cache: bool
    message: str


@dataclass
class ForensicClosureResult:
    """Result of a forensic case closure."""
    success: bool
    analysis_id: int
    status: str
    closed_by: str
    closed_at: datetime
    chain_hash: str
    tsa_timestamp: datetime
    audit_sequence: int
    from_cache: bool
    message: str


# =============================================================================
# TSA SERVICE ABSTRACTION
# =============================================================================

class TSAService:
    """
    Time Stamping Authority service abstraction.
    
    In production, implement this with actual RFC 3161 TSA client.
    For development, uses local timestamps with degradation flag.
    """
    
    PROVIDERS = ['DigiCert', 'FreeTSA', 'Sectigo']
    
    def __init__(self):
        self._fallback_used = False
    
    def timestamp(
        self,
        hash_to_seal: str,
        entity_type: str,
        entity_id: int,
        event_type: str,
    ) -> ForensicTimestampToken:
        """
        Request TSA timestamp for a hash.
        
        Args:
            hash_to_seal: SHA-256 hash to timestamp
            entity_type: Entity type for storage
            entity_id: Entity ID for storage
            event_type: Event type for storage
            
        Returns:
            ForensicTimestampToken with timestamp data
        """
        server_time = timezone.now()
        
        # In production, iterate through providers
        # For now, use local timestamp with is_certified=False
        tsa_timestamp = server_time
        is_certified = False  # Set to True when using real TSA
        
        # Calculate clock drift (would be actual drift in production)
        clock_drift_ms = 0
        
        # Create token (in production, this would be actual RFC 3161 response)
        # For now, create a deterministic token for testing
        token_data = canonical_json({
            'hash': hash_to_seal,
            'timestamp': tsa_timestamp.isoformat(),
            'provider': 'LOCAL_DEV',
        })
        token_bytes = token_data.encode('utf-8')
        
        return ForensicTimestampToken.objects.create(
            entity_type=entity_type,
            entity_id=entity_id,
            event_type=event_type,
            hash_timestamped=hash_to_seal,
            tsa_token=token_bytes,
            tsa_provider='LOCAL_DEV',  # Would be actual provider in production
            tsa_timestamp=tsa_timestamp,
            server_timestamp=server_time,
            clock_drift_ms=clock_drift_ms,
            verification_url='',
            is_certified=is_certified,
        )


# =============================================================================
# FORENSIC REVIEW SERVICE
# =============================================================================

class ForensicReviewService:
    """
    Forensic-enforced wrapper for Shadow Review Workflow operations.
    
    All write operations pass through the ForensicTransactionGuard
    and create appropriate integrity hashes, TSA timestamps, and audit logs.
    
    This service MUST be used for all review operations instead of
    directly calling the underlying workflow service.
    """
    
    def __init__(self):
        self.guard = ForensicTransactionGuard()
        self.tsa = TSAService()
    
    # =========================================================================
    # START REVIEW (PENDING → IN_PROGRESS)
    # =========================================================================
    
    def start_review_forensic(
        self,
        *,
        analysis_id: int,
        reviewer,
        idempotency_key: str,
        request=None,
    ) -> ForensicReviewResult:
        """
        Start human review of a shadow analysis with full forensic tracking.
        
        Transition: PENDING → IN_PROGRESS
        
        Steps:
        1. Validate via ForensicTransactionGuard
        2. Start review via underlying workflow
        3. Create audit log entry
        4. Return forensic result
        
        Args:
            analysis_id: ID of ShadowDifferenceAnalysis
            reviewer: User starting the review
            idempotency_key: Unique key for this operation
            request: Django request for IP/user-agent extraction
            
        Returns:
            ForensicReviewResult with operation outcome
        """
        from core.services.shadow.review_workflow_service import (
            ShadowReviewWorkflowService,
            AnalysisNotFound,
            InvalidShadowTransition,
        )
        from core.models_shadow import ShadowDifferenceAnalysis, ReviewStatus
        
        def _get_analysis():
            try:
                return ShadowDifferenceAnalysis.objects.select_for_update().get(
                    pk=analysis_id
                )
            except ShadowDifferenceAnalysis.DoesNotExist:
                raise AnalysisNotFoundError(analysis_id)
        
        def _start_review_operation(context: ForensicOperationContext, analysis):
            """Actual start review operation."""
            workflow_service = ShadowReviewWorkflowService()
            
            try:
                review = workflow_service.start_review(
                    analysis_id=analysis_id,
                    reviewer=reviewer,
                )
            except AnalysisNotFound:
                raise AnalysisNotFoundError(analysis_id)
            except InvalidShadowTransition as e:
                raise InvalidReviewStateError(
                    current_state=e.from_status,
                    required_states=['PENDING']
                )
            
            return {
                'review_id': review.id,
                'analysis_id': analysis_id,
                'status': review.status,
                'reviewer_id': reviewer.id,
                'started_at': review.started_at.isoformat() if review.started_at else None,
            }
        
        # Execute through guard
        result = self.guard.execute(
            idempotency_key=idempotency_key,
            endpoint='/api/forensic/shadow/review/start',
            entity_type='ShadowDifferenceAnalysis',
            entity_id=analysis_id,
            expected_version=None,  # No version check for start
            actor=reviewer,
            request_data={'analysis_id': analysis_id},
            operation_callable=_start_review_operation,
            audit_event_type=AuditEventType.REVIEW_STARTED,
            get_entity_callable=_get_analysis,
            extra_audit_data={
                'reviewer_id': reviewer.id,
                'reviewer_username': reviewer.username,
            },
            actor_ip=get_client_ip(request) if request else None,
            actor_user_agent=get_user_agent(request) if request else None,
        )
        
        if result.from_cache:
            return ForensicReviewResult(
                success=True,
                analysis_id=analysis_id,
                status=result.data.get('status', 'IN_PROGRESS'),
                status_label='En revisión',
                chain_hash='',
                tsa_timestamp=None,
                audit_sequence=0,
                from_cache=True,
                message='Review already started (cached response)',
            )
        
        return ForensicReviewResult(
            success=True,
            analysis_id=analysis_id,
            status=result.data['status'],
            status_label='En revisión',
            chain_hash='',  # No chain hash for start
            tsa_timestamp=None,  # TSA only for decisions/closures
            audit_sequence=result.audit_log_id or 0,
            from_cache=False,
            message='Review started successfully',
        )
    
    # =========================================================================
    # SUBMIT DECISION (IN_PROGRESS → ACCEPTED/ADJUSTED/ESCALATED)
    # =========================================================================
    
    def submit_decision_forensic(
        self,
        *,
        analysis_id: int,
        reviewer,
        decision: str,
        notes: str,
        confidence_override: Optional[str] = None,
        idempotency_key: str,
        expected_version: int,
        request=None,
    ) -> ForensicDecisionResult:
        """
        Submit human decision with full forensic tracking.
        
        Transition: IN_PROGRESS → ACCEPTED | ADJUSTED | ESCALATED
        
        This is the MOST CRITICAL forensic operation.
        
        Steps (in order):
        1. Guard via ForensicTransactionGuard
        2. Validate reviewer and transition rules
        3. Apply decision
        4. Increment version
        5. Save decision
        6. Create integrity hash node (chain continuation)
        7. Request TSA timestamp for the decision
        8. Create forensic audit log entry
        9. Return serialized response
        
        Args:
            analysis_id: ID of ShadowDifferenceAnalysis
            reviewer: User making the decision
            decision: Decision value (V2_CORRECT, V1_CORRECT, etc.)
            notes: Required justification notes
            confidence_override: Optional confidence level override
            idempotency_key: Unique key for this operation
            expected_version: Version for optimistic locking
            request: Django request for IP/user-agent extraction
            
        Returns:
            ForensicDecisionResult with operation outcome
        """
        from core.services.shadow.review_workflow_service import (
            ShadowReviewWorkflowService,
            AnalysisNotFound,
            InvalidShadowTransition,
            UnauthorizedReviewer,
            DecisionRequired,
        )
        from core.models_shadow import (
            ShadowDifferenceAnalysis,
            ShadowReviewDecision,
            ReviewDecision as ReviewDecisionEnum,
            ConfidenceLevel,
        )
        
        def _get_review():
            try:
                return ShadowReviewDecision.objects.select_for_update().get(
                    analysis_id=analysis_id
                )
            except ShadowReviewDecision.DoesNotExist:
                raise AnalysisNotFoundError(analysis_id)
        
        def _submit_decision_operation(context: ForensicOperationContext, review):
            """Actual decision submission with forensic tracking."""
            workflow_service = ShadowReviewWorkflowService()
            
            # Map string to enum
            decision_map = {
                'V2_CORRECT': ReviewDecisionEnum.V2_CORRECT,
                'V1_CORRECT': ReviewDecisionEnum.V1_CORRECT,
                'POLICY_CHANGE': ReviewDecisionEnum.POLICY_CHANGE,
                'INCONCLUSIVE': ReviewDecisionEnum.INCONCLUSIVE,
                'NOT_APPLICABLE': ReviewDecisionEnum.NOT_APPLICABLE,
            }
            decision_enum = decision_map.get(decision, decision)
            
            # Map confidence override if provided
            confidence_enum = None
            if confidence_override:
                confidence_map = {
                    'HIGH': ConfidenceLevel.HIGH,
                    'MEDIUM': ConfidenceLevel.MEDIUM,
                    'LOW': ConfidenceLevel.LOW,
                }
                confidence_enum = confidence_map.get(confidence_override)
            
            try:
                updated_review = workflow_service.submit_decision(
                    analysis_id=analysis_id,
                    reviewer=reviewer,
                    decision=decision_enum,
                    notes=notes,
                    confidence_override=confidence_enum,
                )
            except AnalysisNotFound:
                raise AnalysisNotFoundError(analysis_id)
            except InvalidShadowTransition as e:
                raise InvalidReviewStateError(
                    current_state=e.from_status,
                    required_states=['IN_PROGRESS']
                )
            except UnauthorizedReviewer:
                raise UnauthorizedReviewerError(
                    user_id=reviewer.id,
                    assigned_reviewer_id=review.reviewer_id if review else 0,
                )
            except DecisionRequired:
                raise ForensicReviewError("Decision and notes are required")
            
            # ============================================================
            # FORENSIC TRACKING STARTS HERE
            # ============================================================
            
            # Get the analysis for case_id
            analysis = ShadowDifferenceAnalysis.objects.get(pk=analysis_id)
            
            # Get previous chain hash (from analysis or earlier node)
            previous_hash_node = ForensicIntegrityHash.objects.filter(
                case_id=analysis_id
            ).order_by('-created_at').first()
            
            previous_hash = previous_hash_node.chain_hash if previous_hash_node else 'GENESIS'
            
            # Build canonical content for decision
            decision_content = {
                'analysis_id': analysis_id,
                'analysis_chain_hash': previous_hash,  # CRITICAL: links to analysis
                'decision': decision,
                'notes': notes,
                'confidence_override': confidence_override,
                'reviewer_id': reviewer.id,
                'decided_at': updated_review.decided_at.isoformat(),
                'version': updated_review.version if hasattr(updated_review, 'version') else 1,
            }
            
            # Create integrity hash node
            integrity_hash = create_integrity_hash(
                entity_type=ForensicEntityType.DECISION,
                entity_id=updated_review.id,
                case_id=analysis_id,
                content_data=decision_content,
                previous_hash=previous_hash,
            )
            
            # Request TSA timestamp for decision
            tsa_token = self.tsa.timestamp(
                hash_to_seal=integrity_hash.chain_hash,
                entity_type=ForensicEntityType.DECISION,
                entity_id=updated_review.id,
                event_type=ForensicEventType.DECIDED,
            )
            
            return {
                'review_id': updated_review.id,
                'analysis_id': analysis_id,
                'status': updated_review.status,
                'decision': decision,
                'notes_length': len(notes),
                'chain_hash': integrity_hash.chain_hash,
                'tsa_timestamp': tsa_token.tsa_timestamp.isoformat(),
                'is_closeable': updated_review.status in ['ACCEPTED', 'ADJUSTED', 'ESCALATED'],
            }
        
        # Execute through guard
        result = self.guard.execute(
            idempotency_key=idempotency_key,
            endpoint='/api/forensic/shadow/review/decision',
            entity_type='ShadowReviewDecision',
            entity_id=analysis_id,
            expected_version=expected_version,
            actor=reviewer,
            request_data={
                'analysis_id': analysis_id,
                'decision': decision,
                'notes': notes,
                'confidence_override': confidence_override,
            },
            operation_callable=_submit_decision_operation,
            audit_event_type=AuditEventType.DECISION_SUBMITTED,
            get_entity_callable=_get_review,
            version_field='version',
            extra_audit_data={
                'decision': decision,
                'notes_preview': notes[:100] if notes else '',
                'confidence_override': confidence_override,
            },
            actor_ip=get_client_ip(request) if request else None,
            actor_user_agent=get_user_agent(request) if request else None,
        )
        
        if result.from_cache:
            return ForensicDecisionResult(
                success=True,
                analysis_id=analysis_id,
                status=result.data.get('status', 'ACCEPTED'),
                decision=result.data.get('decision', decision),
                decision_label=self._get_decision_label(decision),
                chain_hash=result.data.get('chain_hash', ''),
                tsa_timestamp=datetime.fromisoformat(result.data['tsa_timestamp']) if result.data.get('tsa_timestamp') else timezone.now(),
                audit_sequence=0,
                is_closeable=result.data.get('is_closeable', True),
                from_cache=True,
                message='Decision already submitted (cached response)',
            )
        
        return ForensicDecisionResult(
            success=True,
            analysis_id=analysis_id,
            status=result.data['status'],
            decision=decision,
            decision_label=self._get_decision_label(decision),
            chain_hash=result.data['chain_hash'],
            tsa_timestamp=datetime.fromisoformat(result.data['tsa_timestamp']),
            audit_sequence=result.audit_log_id or 0,
            is_closeable=result.data['is_closeable'],
            from_cache=False,
            message='Decision submitted successfully',
        )
    
    # =========================================================================
    # CLOSE CASE (ACCEPTED/ADJUSTED/ESCALATED → CLOSED)
    # =========================================================================
    
    def close_case_forensic(
        self,
        *,
        analysis_id: int,
        closer,
        idempotency_key: str,
        expected_version: int,
        request=None,
    ) -> ForensicClosureResult:
        """
        Close review case with full forensic tracking.
        
        Transition: ACCEPTED | ADJUSTED | ESCALATED → CLOSED
        
        Steps:
        1. Guard via ForensicTransactionGuard
        2. Validate state transition
        3. Apply closure
        4. Create integrity hash node
        5. Request TSA timestamp
        6. Create audit log entry
        
        Args:
            analysis_id: ID of ShadowDifferenceAnalysis
            closer: User closing the case
            idempotency_key: Unique key for this operation
            expected_version: Version for optimistic locking
            request: Django request for IP/user-agent extraction
            
        Returns:
            ForensicClosureResult with operation outcome
        """
        from core.services.shadow.review_workflow_service import (
            ShadowReviewWorkflowService,
            AnalysisNotFound,
            InvalidShadowTransition,
        )
        from core.models_shadow import (
            ShadowDifferenceAnalysis,
            ShadowReviewDecision,
        )
        
        def _get_review():
            try:
                return ShadowReviewDecision.objects.select_for_update().get(
                    analysis_id=analysis_id
                )
            except ShadowReviewDecision.DoesNotExist:
                raise AnalysisNotFoundError(analysis_id)
        
        def _close_case_operation(context: ForensicOperationContext, review):
            """Actual case closure with forensic tracking."""
            workflow_service = ShadowReviewWorkflowService()
            
            try:
                updated_review = workflow_service.close_case(
                    analysis_id=analysis_id,
                    reviewer=closer,
                )
            except AnalysisNotFound:
                raise AnalysisNotFoundError(analysis_id)
            except InvalidShadowTransition as e:
                raise InvalidReviewStateError(
                    current_state=e.from_status,
                    required_states=['ACCEPTED', 'ADJUSTED', 'ESCALATED']
                )
            
            # ============================================================
            # FORENSIC TRACKING
            # ============================================================
            
            # Get previous chain hash
            previous_hash_node = ForensicIntegrityHash.objects.filter(
                case_id=analysis_id
            ).order_by('-created_at').first()
            
            previous_hash = previous_hash_node.chain_hash if previous_hash_node else 'GENESIS'
            
            # Build canonical content for closure
            closure_content = {
                'analysis_id': analysis_id,
                'decision_chain_hash': previous_hash,
                'closed_by_id': closer.id,
                'closed_at': updated_review.closed_at.isoformat(),
                'final_status': updated_review.status,
                'final_decision': updated_review.decision,
            }
            
            # Create integrity hash node
            integrity_hash = create_integrity_hash(
                entity_type=ForensicEntityType.CLOSURE,
                entity_id=updated_review.id,
                case_id=analysis_id,
                content_data=closure_content,
                previous_hash=previous_hash,
            )
            
            # Request TSA timestamp
            tsa_token = self.tsa.timestamp(
                hash_to_seal=integrity_hash.chain_hash,
                entity_type=ForensicEntityType.CLOSURE,
                entity_id=updated_review.id,
                event_type=ForensicEventType.CLOSED,
            )
            
            return {
                'review_id': updated_review.id,
                'analysis_id': analysis_id,
                'status': updated_review.status,
                'closed_by': closer.username,
                'closed_at': updated_review.closed_at.isoformat(),
                'chain_hash': integrity_hash.chain_hash,
                'tsa_timestamp': tsa_token.tsa_timestamp.isoformat(),
            }
        
        # Execute through guard
        result = self.guard.execute(
            idempotency_key=idempotency_key,
            endpoint='/api/forensic/shadow/review/close',
            entity_type='ShadowReviewDecision',
            entity_id=analysis_id,
            expected_version=expected_version,
            actor=closer,
            request_data={'analysis_id': analysis_id},
            operation_callable=_close_case_operation,
            audit_event_type=AuditEventType.REVIEW_CLOSED,
            get_entity_callable=_get_review,
            version_field='version',
            extra_audit_data={
                'closed_by_id': closer.id,
                'closed_by_username': closer.username,
            },
            actor_ip=get_client_ip(request) if request else None,
            actor_user_agent=get_user_agent(request) if request else None,
        )
        
        if result.from_cache:
            return ForensicClosureResult(
                success=True,
                analysis_id=analysis_id,
                status='CLOSED',
                closed_by=closer.username,
                closed_at=datetime.fromisoformat(result.data['closed_at']) if result.data.get('closed_at') else timezone.now(),
                chain_hash=result.data.get('chain_hash', ''),
                tsa_timestamp=datetime.fromisoformat(result.data['tsa_timestamp']) if result.data.get('tsa_timestamp') else timezone.now(),
                audit_sequence=0,
                from_cache=True,
                message='Case already closed (cached response)',
            )
        
        return ForensicClosureResult(
            success=True,
            analysis_id=analysis_id,
            status='CLOSED',
            closed_by=closer.username,
            closed_at=datetime.fromisoformat(result.data['closed_at']),
            chain_hash=result.data['chain_hash'],
            tsa_timestamp=datetime.fromisoformat(result.data['tsa_timestamp']),
            audit_sequence=result.audit_log_id or 0,
            from_cache=False,
            message='Case closed successfully. No further modifications allowed.',
        )
    
    # =========================================================================
    # HELPERS
    # =========================================================================
    
    def _get_decision_label(self, decision: str) -> str:
        """Get human-readable label for decision."""
        labels = {
            'V2_CORRECT': 'V2 es correcto',
            'V1_CORRECT': 'V1 es correcto',
            'POLICY_CHANGE': 'Requiere cambio de política',
            'INCONCLUSIVE': 'No concluyente',
            'NOT_APPLICABLE': 'No aplica',
        }
        return labels.get(decision, decision)
