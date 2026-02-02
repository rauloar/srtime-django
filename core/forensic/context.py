"""
Forensic Context Management
Thread-safe context for marking operations as forensic-authorized.

This module provides the mechanism to distinguish between:
- Authorized forensic operations (through ForensicTransactionGuard)
- Unauthorized direct model access (which should be blocked)
"""
import contextvars
import threading
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any

from django.utils import timezone


# =============================================================================
# CONTEXT VARIABLES (Thread-safe, async-safe)
# =============================================================================

# Primary context variable for forensic authorization
_forensic_context: contextvars.ContextVar[Optional['ForensicContext']] = contextvars.ContextVar(
    'forensic_context',
    default=None
)

# Fallback for environments where contextvars might not work as expected
_thread_local = threading.local()


# =============================================================================
# FORENSIC CONTEXT
# =============================================================================

@dataclass
class ForensicContext:
    """
    Context object that marks an operation as forensic-authorized.
    
    When this context is active, protected models allow save() operations.
    Without this context, save() is blocked and logged as a violation.
    """
    
    # Unique identifier for this forensic operation
    operation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Correlation ID for request tracing
    correlation_id: Optional[str] = None
    
    # Idempotency key from client
    idempotency_key: Optional[str] = None
    
    # Actor performing the operation
    actor_id: Optional[int] = None
    actor_username: Optional[str] = None
    
    # Request metadata
    endpoint: Optional[str] = None
    actor_ip: Optional[str] = None
    actor_user_agent: Optional[str] = None
    
    # Operation metadata
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    operation_type: Optional[str] = None
    
    # Timestamps
    started_at: datetime = field(default_factory=timezone.now)
    
    # Internal tracking
    _save_count: int = field(default=0, repr=False)
    _models_modified: list = field(default_factory=list, repr=False)
    
    def record_save(self, model_class: str, instance_id: Any):
        """Record that a model was saved within this context."""
        self._save_count += 1
        self._models_modified.append({
            'model': model_class,
            'id': instance_id,
            'timestamp': timezone.now().isoformat(),
        })


# =============================================================================
# CONTEXT MANAGEMENT
# =============================================================================

def get_forensic_context() -> Optional[ForensicContext]:
    """
    Get the current forensic context if one is active.
    
    Returns None if no forensic context is active, meaning
    the current operation is NOT authorized for protected model access.
    """
    # Try contextvars first (works with async and threads)
    context = _forensic_context.get()
    if context is not None:
        return context
    
    # Fallback to thread local
    return getattr(_thread_local, 'forensic_context', None)


def is_forensic_context_active() -> bool:
    """Check if a forensic context is currently active."""
    return get_forensic_context() is not None


def _set_forensic_context(context: Optional[ForensicContext]) -> None:
    """Set the forensic context (internal use only)."""
    _forensic_context.set(context)
    _thread_local.forensic_context = context


@contextmanager
def forensic_operation(
    *,
    operation_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
    idempotency_key: Optional[str] = None,
    actor_id: Optional[int] = None,
    actor_username: Optional[str] = None,
    endpoint: Optional[str] = None,
    actor_ip: Optional[str] = None,
    actor_user_agent: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    operation_type: Optional[str] = None,
):
    """
    Context manager that marks a block of code as a forensic operation.
    
    Within this context, protected models will allow save() operations.
    
    Usage:
        with forensic_operation(
            actor_id=user.id,
            entity_type='ShadowReviewDecision',
            operation_type='DECISION_SUBMITTED'
        ):
            # Protected model saves are allowed here
            review.decision = 'V2_CORRECT'
            review.save()
    
    Args:
        operation_id: Unique ID for this operation (auto-generated if not provided)
        correlation_id: Request correlation ID for tracing
        idempotency_key: Client-provided idempotency key
        actor_id: User ID performing the operation
        actor_username: Username for logging
        endpoint: API endpoint being called
        actor_ip: Client IP address
        actor_user_agent: Client user agent
        entity_type: Type of entity being modified
        entity_id: ID of entity being modified
        operation_type: Type of operation (e.g., DECISION_SUBMITTED)
    """
    # Check for nested context (not allowed to prevent confusion)
    existing = get_forensic_context()
    if existing is not None:
        # Allow nested contexts but track the nesting
        # The outer context remains active
        yield existing
        return
    
    # Create new context
    context = ForensicContext(
        operation_id=operation_id or str(uuid.uuid4()),
        correlation_id=correlation_id,
        idempotency_key=idempotency_key,
        actor_id=actor_id,
        actor_username=actor_username,
        endpoint=endpoint,
        actor_ip=actor_ip,
        actor_user_agent=actor_user_agent,
        entity_type=entity_type,
        entity_id=entity_id,
        operation_type=operation_type,
    )
    
    # Activate context
    _set_forensic_context(context)
    
    try:
        yield context
    finally:
        # Deactivate context
        _set_forensic_context(None)


# =============================================================================
# REQUEST CONTEXT HELPERS
# =============================================================================

def forensic_context_from_request(request) -> dict:
    """
    Extract forensic context parameters from a Django request.
    
    Looks for:
    - X-Idempotency-Key header
    - X-Correlation-ID header (or generates one)
    - User information
    - IP address
    - User agent
    """
    # Extract idempotency key
    idempotency_key = (
        request.headers.get('X-Idempotency-Key') or
        request.META.get('HTTP_X_IDEMPOTENCY_KEY')
    )
    
    # Extract or generate correlation ID
    correlation_id = (
        request.headers.get('X-Correlation-ID') or
        request.META.get('HTTP_X_CORRELATION_ID') or
        str(uuid.uuid4())
    )
    
    # Extract user info
    actor_id = None
    actor_username = None
    if hasattr(request, 'user') and request.user.is_authenticated:
        actor_id = request.user.id
        actor_username = request.user.username
    
    # Extract IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        actor_ip = x_forwarded_for.split(',')[0].strip()
    else:
        actor_ip = request.META.get('REMOTE_ADDR')
    
    # Extract user agent
    actor_user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
    
    # Get endpoint
    endpoint = request.path
    
    return {
        'idempotency_key': idempotency_key,
        'correlation_id': correlation_id,
        'actor_id': actor_id,
        'actor_username': actor_username,
        'actor_ip': actor_ip,
        'actor_user_agent': actor_user_agent,
        'endpoint': endpoint,
    }
