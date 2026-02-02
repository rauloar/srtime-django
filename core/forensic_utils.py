"""
Forensic Integrity Layer - Cryptographic Utilities
Utility functions for hash computation, chain verification, and integrity checks.
"""
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional, List, Dict, Union
from uuid import UUID

from django.db import models
from django.utils import timezone


# =============================================================================
# CANONICAL JSON SERIALIZATION
# =============================================================================

class ForensicJSONEncoder(json.JSONEncoder):
    """
    JSON encoder that produces deterministic, canonical output.
    
    Ensures the same input always produces the same JSON string,
    which is required for reproducible hash computation.
    """
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            # Always use ISO format with timezone
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            # Normalize decimals to remove trailing zeros
            return str(obj.normalize())
        elif isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, bytes):
            # Encode bytes as hex
            return obj.hex()
        elif isinstance(obj, models.Model):
            # Django models: use primary key
            return obj.pk
        elif hasattr(obj, '__dict__'):
            # Dataclasses and other objects
            return obj.__dict__
        return super().default(obj)


def canonical_json(data: Any) -> str:
    """
    Produce a canonical JSON string from any data structure.
    
    Canonical means:
    - Keys are sorted alphabetically
    - No extra whitespace
    - Consistent encoding of types
    - Deterministic output for same input
    
    Args:
        data: Any JSON-serializable data structure
        
    Returns:
        Canonical JSON string
    """
    return json.dumps(
        data,
        cls=ForensicJSONEncoder,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False
    )


# =============================================================================
# HASH COMPUTATION
# =============================================================================

def sha256_hex(data: Union[str, bytes]) -> str:
    """
    Compute SHA-256 hash and return as lowercase hex string.
    
    Args:
        data: String or bytes to hash
        
    Returns:
        64-character lowercase hex string
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha256(data).hexdigest()


def compute_chain_hash(content_hash: str, previous_hash: str) -> str:
    """
    Compute the chain hash from content and previous hashes.
    
    The chain hash links this node to the previous node in the chain.
    Any modification to either hash will produce a different chain hash.
    
    Args:
        content_hash: SHA-256 hash of this node's content
        previous_hash: Chain hash of the previous node (or "GENESIS")
        
    Returns:
        64-character lowercase hex string
    """
    combined = content_hash + previous_hash
    return sha256_hex(combined)


def compute_content_hash(data: Any) -> str:
    """
    Compute SHA-256 hash of canonical JSON representation.
    
    Args:
        data: Any JSON-serializable data structure
        
    Returns:
        64-character lowercase hex string
    """
    canonical = canonical_json(data)
    return sha256_hex(canonical)


# =============================================================================
# VERIFICATION DATA STRUCTURES
# =============================================================================

@dataclass
class IntegrityVerificationResult:
    """Result of verifying a single integrity hash record."""
    record_id: int
    entity_type: str
    entity_id: int
    is_valid: bool
    content_matches: bool
    chain_matches: bool
    stored_content_hash: str
    computed_content_hash: str
    stored_chain_hash: str
    expected_previous_hash: Optional[str]
    actual_previous_hash: str
    error: Optional[str] = None


@dataclass
class ChainVerificationResult:
    """Result of verifying an entire chain."""
    case_id: int
    total_nodes: int
    valid_nodes: int
    invalid_nodes: int
    chain_intact: bool
    first_break_at: Optional[int]
    violations: List[IntegrityVerificationResult]
    verified_at: datetime


# =============================================================================
# VERIFICATION FUNCTIONS
# =============================================================================

def verify_integrity_record(record_id: int) -> IntegrityVerificationResult:
    """
    Verify the integrity of a single ForensicIntegrityHash record.
    
    Checks:
    1. Content hash matches stored canonical JSON
    2. Chain hash is correctly computed from content and previous hash
    
    Args:
        record_id: ID of the ForensicIntegrityHash record
        
    Returns:
        IntegrityVerificationResult with verification details
    """
    from core.models_forensic import ForensicIntegrityHash
    
    try:
        record = ForensicIntegrityHash.objects.get(pk=record_id)
    except ForensicIntegrityHash.DoesNotExist:
        return IntegrityVerificationResult(
            record_id=record_id,
            entity_type='UNKNOWN',
            entity_id=0,
            is_valid=False,
            content_matches=False,
            chain_matches=False,
            stored_content_hash='',
            computed_content_hash='',
            stored_chain_hash='',
            expected_previous_hash=None,
            actual_previous_hash='',
            error=f"Record {record_id} not found"
        )
    
    # Recompute content hash from stored canonical JSON
    computed_content_hash = compute_content_hash(record.canonical_json)
    content_matches = (computed_content_hash == record.content_hash)
    
    # Recompute chain hash
    computed_chain_hash = compute_chain_hash(
        record.content_hash,
        record.previous_hash
    )
    chain_matches = (computed_chain_hash == record.chain_hash)
    
    # Get expected previous hash from predecessor
    predecessor = ForensicIntegrityHash.objects.filter(
        case_id=record.case_id,
        created_at__lt=record.created_at
    ).order_by('-created_at').first()
    
    expected_previous_hash = predecessor.chain_hash if predecessor else 'GENESIS'
    previous_matches = (record.previous_hash == expected_previous_hash)
    
    return IntegrityVerificationResult(
        record_id=record_id,
        entity_type=record.entity_type,
        entity_id=record.entity_id,
        is_valid=content_matches and chain_matches and previous_matches,
        content_matches=content_matches,
        chain_matches=chain_matches,
        stored_content_hash=record.content_hash,
        computed_content_hash=computed_content_hash,
        stored_chain_hash=record.chain_hash,
        expected_previous_hash=expected_previous_hash,
        actual_previous_hash=record.previous_hash,
        error=None if (content_matches and chain_matches and previous_matches) else "Integrity violation detected"
    )


def verify_chain_for_case(case_id: int) -> ChainVerificationResult:
    """
    Verify the entire integrity chain for a case.
    
    Checks:
    1. Each node's content hash matches its canonical JSON
    2. Each node's chain hash is correctly computed
    3. Each node's previous_hash points to the predecessor's chain_hash
    4. No gaps in the sequence
    
    Args:
        case_id: The case ID to verify
        
    Returns:
        ChainVerificationResult with full chain verification status
    """
    from core.models_forensic import ForensicIntegrityHash
    
    records = ForensicIntegrityHash.objects.filter(
        case_id=case_id
    ).order_by('created_at')
    
    total_nodes = records.count()
    valid_nodes = 0
    invalid_nodes = 0
    first_break_at = None
    violations = []
    
    expected_previous = 'GENESIS'
    
    for i, record in enumerate(records):
        # Verify content hash
        computed_content = compute_content_hash(record.canonical_json)
        content_matches = (computed_content == record.content_hash)
        
        # Verify chain hash
        computed_chain = compute_chain_hash(record.content_hash, record.previous_hash)
        chain_matches = (computed_chain == record.chain_hash)
        
        # Verify previous hash linkage
        previous_matches = (record.previous_hash == expected_previous)
        
        is_valid = content_matches and chain_matches and previous_matches
        
        if is_valid:
            valid_nodes += 1
        else:
            invalid_nodes += 1
            if first_break_at is None:
                first_break_at = i
            
            violations.append(IntegrityVerificationResult(
                record_id=record.id,
                entity_type=record.entity_type,
                entity_id=record.entity_id,
                is_valid=False,
                content_matches=content_matches,
                chain_matches=chain_matches,
                stored_content_hash=record.content_hash,
                computed_content_hash=computed_content,
                stored_chain_hash=record.chain_hash,
                expected_previous_hash=expected_previous,
                actual_previous_hash=record.previous_hash,
                error="Chain integrity violation"
            ))
        
        # Next node should reference this node's chain hash
        expected_previous = record.chain_hash
    
    return ChainVerificationResult(
        case_id=case_id,
        total_nodes=total_nodes,
        valid_nodes=valid_nodes,
        invalid_nodes=invalid_nodes,
        chain_intact=(invalid_nodes == 0),
        first_break_at=first_break_at,
        violations=violations,
        verified_at=timezone.now()
    )


# =============================================================================
# AUDIT CHAIN VERIFICATION
# =============================================================================

@dataclass
class AuditChainVerificationResult:
    """Result of verifying the audit log chain."""
    total_events: int
    valid_events: int
    invalid_events: int
    chain_intact: bool
    sequence_gaps: List[int]
    first_break_at: Optional[int]
    verified_at: datetime


def verify_audit_chain(
    start_sequence: Optional[int] = None,
    end_sequence: Optional[int] = None
) -> AuditChainVerificationResult:
    """
    Verify the integrity of the forensic audit log chain.
    
    Checks:
    1. Sequence numbers are continuous (no gaps)
    2. Each event's hash chain is correctly computed
    3. Each event links to the previous event's chain hash
    
    Args:
        start_sequence: Optional starting sequence number
        end_sequence: Optional ending sequence number
        
    Returns:
        AuditChainVerificationResult with verification details
    """
    from core.models_forensic import ForensicAuditLog
    
    queryset = ForensicAuditLog.objects.all()
    
    if start_sequence is not None:
        queryset = queryset.filter(sequence_number__gte=start_sequence)
    if end_sequence is not None:
        queryset = queryset.filter(sequence_number__lte=end_sequence)
    
    events = queryset.order_by('sequence_number')
    
    total_events = events.count()
    valid_events = 0
    invalid_events = 0
    sequence_gaps = []
    first_break_at = None
    
    expected_previous = 'GENESIS'
    expected_sequence = None
    
    for event in events:
        # Check sequence continuity
        if expected_sequence is not None and event.sequence_number != expected_sequence:
            gap_size = event.sequence_number - expected_sequence
            sequence_gaps.append(expected_sequence)
            if first_break_at is None:
                first_break_at = event.sequence_number
        
        # Verify event hash (would need to reconstruct event content)
        # For now, verify chain linkage
        previous_matches = (event.previous_hash == expected_previous)
        
        # Verify chain hash computation
        computed_chain = compute_chain_hash(event.event_hash, event.previous_hash)
        chain_matches = (computed_chain == event.chain_hash)
        
        if previous_matches and chain_matches:
            valid_events += 1
        else:
            invalid_events += 1
            if first_break_at is None:
                first_break_at = event.sequence_number
        
        expected_previous = event.chain_hash
        expected_sequence = event.sequence_number + 1
    
    return AuditChainVerificationResult(
        total_events=total_events,
        valid_events=valid_events,
        invalid_events=invalid_events,
        chain_intact=(invalid_events == 0 and len(sequence_gaps) == 0),
        sequence_gaps=sequence_gaps,
        first_break_at=first_break_at,
        verified_at=timezone.now()
    )


# =============================================================================
# HASH CREATION HELPERS
# =============================================================================

def create_integrity_hash(
    entity_type: str,
    entity_id: int,
    case_id: int,
    content_data: Dict[str, Any],
    previous_hash: Optional[str] = None
) -> 'ForensicIntegrityHash':
    """
    Create a new ForensicIntegrityHash record for an entity.
    
    This function automatically:
    - Computes the content hash from canonical JSON
    - Links to the previous hash in the chain
    - Computes the chain hash
    
    Args:
        entity_type: Type of entity (from ForensicEntityType)
        entity_id: ID of the entity
        case_id: Case ID for chain grouping
        content_data: Dictionary of content to hash
        previous_hash: Explicit previous hash, or auto-detect from chain
        
    Returns:
        Created ForensicIntegrityHash instance
    """
    from core.models_forensic import ForensicIntegrityHash
    
    # Auto-detect previous hash if not provided
    if previous_hash is None:
        predecessor = ForensicIntegrityHash.objects.filter(
            case_id=case_id
        ).order_by('-created_at').first()
        
        previous_hash = predecessor.chain_hash if predecessor else 'GENESIS'
    
    # Compute hashes
    canonical = canonical_json(content_data)
    content_hash = sha256_hex(canonical)
    chain_hash = compute_chain_hash(content_hash, previous_hash)
    
    # Create immutable record
    return ForensicIntegrityHash.objects.create(
        entity_type=entity_type,
        entity_id=entity_id,
        case_id=case_id,
        content_hash=content_hash,
        previous_hash=previous_hash,
        chain_hash=chain_hash,
        canonical_json=content_data,
        hash_algorithm='SHA256'
    )


def create_audit_log_entry(
    event_type: str,
    entity_type: str,
    entity_id: Optional[int],
    actor_id: Optional[int],
    event_data: Dict[str, Any],
    actor_ip: Optional[str] = None,
    actor_user_agent: Optional[str] = None
) -> 'ForensicAuditLog':
    """
    Create a new ForensicAuditLog entry with proper chain linkage.
    
    This function automatically:
    - Assigns the next sequence number
    - Computes event and chain hashes
    - Links to the previous audit log entry
    
    Args:
        event_type: Type of event (from AuditEventType)
        entity_type: Type of entity being audited
        entity_id: ID of the entity
        actor_id: User ID who performed the action
        event_data: Additional event metadata
        actor_ip: IP address of the actor
        actor_user_agent: User agent of the actor
        
    Returns:
        Created ForensicAuditLog instance
    """
    from core.models_forensic import ForensicAuditLog
    from django.db import transaction
    
    with transaction.atomic():
        # Get last entry and lock for sequence assignment
        last_entry = ForensicAuditLog.objects.select_for_update().order_by(
            '-sequence_number'
        ).first()
        
        new_sequence = (last_entry.sequence_number + 1) if last_entry else 1
        previous_hash = last_entry.chain_hash if last_entry else 'GENESIS'
        
        # Build event content for hashing
        timestamp_server = timezone.now()
        event_content = {
            'sequence_number': new_sequence,
            'event_type': event_type,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'actor_id': actor_id,
            'event_data': event_data,
            'timestamp': timestamp_server.isoformat()
        }
        
        # Compute hashes
        event_hash = compute_content_hash(event_content)
        chain_hash = compute_chain_hash(event_hash, previous_hash)
        
        # Create immutable record
        return ForensicAuditLog.objects.create(
            sequence_number=new_sequence,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=actor_id,
            actor_ip=actor_ip,
            actor_user_agent=actor_user_agent or '',
            event_data=event_data,
            event_hash=event_hash,
            previous_hash=previous_hash,
            chain_hash=chain_hash,
            timestamp_server=timestamp_server
        )
