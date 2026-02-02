"""
Forensic Transaction Guard
Reusable component for enforcing forensic-safe transactional operations.

Provides:
- Idempotency enforcement
- Distributed locking
- Atomic transactions
- Optimistic locking
- Automatic audit logging
- Standardized error handling
"""
import hashlib
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Callable, Optional, TypeVar, Generic

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from core.models_forensic import (
    ForensicIdempotencyKey,
    ForensicAuditLog,
)
from core.forensic_utils import (
    canonical_json,
    sha256_hex,
    create_audit_log_entry,
)


# =============================================================================
# EXCEPTIONS
# =============================================================================

class ForensicTransactionError(Exception):
    """Base exception for forensic transaction errors."""
    pass


class IdempotencyKeyConflictError(ForensicTransactionError):
    """Raised when an idempotency key is reused with different data."""
    
    def __init__(self, key: str, message: str = "Idempotency key already used"):
        self.key = key
        super().__init__(message)


class IdempotencyKeyRequiredError(ForensicTransactionError):
    """Raised when idempotency key is missing."""
    pass


class OptimisticLockError(ForensicTransactionError):
    """Raised when version mismatch occurs during update."""
    
    def __init__(self, entity_id: int, expected: int, actual: int):
        self.entity_id = entity_id
        self.expected_version = expected
        self.actual_version = actual
        super().__init__(
            f"Version mismatch for entity {entity_id}: "
            f"expected {expected}, got {actual}"
        )


class DistributedLockError(ForensicTransactionError):
    """Raised when unable to acquire distributed lock."""
    
    def __init__(self, lock_key: str, timeout: int):
        self.lock_key = lock_key
        self.timeout = timeout
        super().__init__(f"Failed to acquire lock '{lock_key}' within {timeout}s")


class DistributedLockTimeout(ForensicTransactionError):
    """Raised when lock times out."""
    pass


# =============================================================================
# CACHED RESPONSE
# =============================================================================

@dataclass
class CachedResponse:
    """Response cached from idempotent operation."""
    status: int
    body: dict
    from_cache: bool = True


# =============================================================================
# DISTRIBUTED LOCK
# =============================================================================

class DistributedLock:
    """
    Simple distributed lock using Django cache backend.
    
    For production with multiple workers, use Redis with proper
    Redlock algorithm. This implementation is suitable for
    single-server deployments.
    """
    
    LOCK_PREFIX = "forensic_lock:"
    
    def __init__(self, key: str, timeout: int = 30):
        self.key = f"{self.LOCK_PREFIX}{key}"
        self.timeout = timeout
        self.token = sha256_hex(f"{key}:{timezone.now().isoformat()}:{id(self)}")
        self._acquired = False
    
    def acquire(self, blocking: bool = True, blocking_timeout: int = 10) -> bool:
        """
        Attempt to acquire the lock.
        
        Args:
            blocking: If True, wait for lock. If False, return immediately.
            blocking_timeout: How long to wait for lock (seconds).
            
        Returns:
            True if lock acquired, False otherwise.
        """
        start_time = timezone.now()
        
        while True:
            # Try to set lock with NX (only if not exists)
            acquired = cache.add(self.key, self.token, self.timeout)
            
            if acquired:
                self._acquired = True
                return True
            
            if not blocking:
                return False
            
            # Check timeout
            elapsed = (timezone.now() - start_time).total_seconds()
            if elapsed >= blocking_timeout:
                return False
            
            # Brief sleep before retry
            import time
            time.sleep(0.1)
    
    def release(self) -> bool:
        """
        Release the lock if we own it.
        
        Returns:
            True if lock was released, False if we didn't own it.
        """
        if not self._acquired:
            return False
        
        # Only delete if we own the lock
        current_token = cache.get(self.key)
        if current_token == self.token:
            cache.delete(self.key)
            self._acquired = False
            return True
        
        return False
    
    def __enter__(self):
        if not self.acquire():
            raise DistributedLockError(self.key, self.timeout)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False


@contextmanager
def distributed_lock(key: str, timeout: int = 30, blocking_timeout: int = 10):
    """
    Context manager for distributed locking.
    
    Args:
        key: Lock identifier
        timeout: Lock TTL in seconds
        blocking_timeout: How long to wait for lock acquisition
        
    Raises:
        DistributedLockError: If lock cannot be acquired
    """
    lock = DistributedLock(key, timeout)
    
    if not lock.acquire(blocking=True, blocking_timeout=blocking_timeout):
        raise DistributedLockError(key, blocking_timeout)
    
    try:
        yield lock
    finally:
        lock.release()


# =============================================================================
# FORENSIC TRANSACTION GUARD
# =============================================================================

T = TypeVar('T')


@dataclass
class ForensicOperationContext:
    """Context passed to operation callables."""
    idempotency_key: str
    endpoint: str
    entity_id: int
    entity_type: str
    actor: Any
    request_data: dict


@dataclass
class ForensicOperationResult(Generic[T]):
    """Result of a forensic operation."""
    success: bool
    data: Optional[T]
    from_cache: bool
    audit_log_id: Optional[int]
    error: Optional[str]


class ForensicTransactionGuard:
    """
    Enforces forensic-safe transactional operations.
    
    This guard wraps any state-changing operation to ensure:
    1. Idempotency - Same request produces same result
    2. Distributed locking - Prevents race conditions
    3. Atomic transactions - All or nothing
    4. Optimistic locking - Version-based concurrency
    5. Audit logging - Every action is recorded
    
    Usage:
        guard = ForensicTransactionGuard()
        result = guard.execute(
            idempotency_key="uuid",
            endpoint="/api/review/decision",
            entity_type="ShadowReview",
            entity_id=123,
            expected_version=1,
            actor=request.user,
            request_data=serializer.validated_data,
            operation_callable=my_operation,
            audit_event_type="DECISION_SUBMITTED",
        )
    """
    
    IDEMPOTENCY_TTL_HOURS = 24
    LOCK_TIMEOUT_SECONDS = 30
    LOCK_WAIT_SECONDS = 10
    
    def __init__(
        self,
        idempotency_ttl_hours: int = 24,
        lock_timeout: int = 30,
        lock_wait: int = 10
    ):
        self.idempotency_ttl = timedelta(hours=idempotency_ttl_hours)
        self.lock_timeout = lock_timeout
        self.lock_wait = lock_wait
    
    def execute(
        self,
        *,
        idempotency_key: str,
        endpoint: str,
        entity_type: str,
        entity_id: int,
        expected_version: Optional[int],
        actor: Any,
        request_data: dict,
        operation_callable: Callable[[ForensicOperationContext, Any], T],
        audit_event_type: str,
        get_entity_callable: Optional[Callable[[], Any]] = None,
        version_field: str = 'version',
        extra_audit_data: Optional[dict] = None,
        actor_ip: Optional[str] = None,
        actor_user_agent: Optional[str] = None,
    ) -> ForensicOperationResult[T]:
        """
        Execute a forensic-safe operation.
        
        Args:
            idempotency_key: Client-provided unique key for this operation
            endpoint: API endpoint path
            entity_type: Type of entity being modified
            entity_id: ID of entity being modified
            expected_version: Expected version for optimistic locking (None to skip)
            actor: User performing the operation
            request_data: Original request data
            operation_callable: Function that performs the actual operation
            audit_event_type: Type of audit event to log
            get_entity_callable: Function to retrieve entity for version check
            version_field: Name of version field on entity
            extra_audit_data: Additional data for audit log
            actor_ip: IP address of actor
            actor_user_agent: User agent of actor
            
        Returns:
            ForensicOperationResult with operation outcome
            
        Raises:
            IdempotencyKeyRequiredError: If key is missing
            IdempotencyKeyConflictError: If key reused with different data
            DistributedLockError: If lock cannot be acquired
            OptimisticLockError: If version mismatch
        """
        # Validate idempotency key
        if not idempotency_key:
            raise IdempotencyKeyRequiredError("Idempotency key is required")
        
        # Check for cached response
        cached = self._check_idempotency(
            idempotency_key, 
            endpoint, 
            request_data
        )
        if cached is not None:
            return ForensicOperationResult(
                success=True,
                data=cached.body,
                from_cache=True,
                audit_log_id=None,
                error=None
            )
        
        # Build lock key
        lock_key = f"{entity_type}:{entity_id}"
        
        # Execute with distributed lock
        with distributed_lock(lock_key, self.lock_timeout, self.lock_wait):
            return self._execute_guarded(
                idempotency_key=idempotency_key,
                endpoint=endpoint,
                entity_type=entity_type,
                entity_id=entity_id,
                expected_version=expected_version,
                actor=actor,
                request_data=request_data,
                operation_callable=operation_callable,
                audit_event_type=audit_event_type,
                get_entity_callable=get_entity_callable,
                version_field=version_field,
                extra_audit_data=extra_audit_data,
                actor_ip=actor_ip,
                actor_user_agent=actor_user_agent,
            )
    
    def _execute_guarded(
        self,
        *,
        idempotency_key: str,
        endpoint: str,
        entity_type: str,
        entity_id: int,
        expected_version: Optional[int],
        actor: Any,
        request_data: dict,
        operation_callable: Callable,
        audit_event_type: str,
        get_entity_callable: Optional[Callable],
        version_field: str,
        extra_audit_data: Optional[dict],
        actor_ip: Optional[str],
        actor_user_agent: Optional[str],
    ) -> ForensicOperationResult:
        """Execute operation within transaction."""
        
        with transaction.atomic():
            # Optimistic locking check
            if expected_version is not None and get_entity_callable is not None:
                entity = get_entity_callable()
                actual_version = getattr(entity, version_field, None)
                
                if actual_version != expected_version:
                    raise OptimisticLockError(
                        entity_id, 
                        expected_version, 
                        actual_version
                    )
            
            # Build context
            context = ForensicOperationContext(
                idempotency_key=idempotency_key,
                endpoint=endpoint,
                entity_id=entity_id,
                entity_type=entity_type,
                actor=actor,
                request_data=request_data,
            )
            
            # Execute operation
            entity = get_entity_callable() if get_entity_callable else None
            result = operation_callable(context, entity)
            
            # Build audit data
            audit_data = {
                'entity_type': entity_type,
                'entity_id': entity_id,
                'operation': audit_event_type,
                'idempotency_key': idempotency_key,
            }
            if extra_audit_data:
                audit_data.update(extra_audit_data)
            
            # Create audit log entry
            audit_log = create_audit_log_entry(
                event_type=audit_event_type,
                entity_type=entity_type,
                entity_id=entity_id,
                actor_id=actor.id if actor else None,
                event_data=audit_data,
                actor_ip=actor_ip,
                actor_user_agent=actor_user_agent,
            )
            
            # Cache response for idempotency
            response_body = result if isinstance(result, dict) else {'result': str(result)}
            self._cache_idempotency(
                idempotency_key=idempotency_key,
                endpoint=endpoint,
                request_data=request_data,
                response_status=200,
                response_body=response_body,
            )
            
            return ForensicOperationResult(
                success=True,
                data=result,
                from_cache=False,
                audit_log_id=audit_log.id,
                error=None
            )
    
    def _check_idempotency(
        self,
        idempotency_key: str,
        endpoint: str,
        request_data: dict,
    ) -> Optional[CachedResponse]:
        """
        Check for existing idempotency key.
        
        Returns cached response if key exists with same request hash.
        Raises if key exists with different request hash.
        """
        request_hash = sha256_hex(canonical_json(request_data))
        
        try:
            existing = ForensicIdempotencyKey.objects.get(
                idempotency_key=idempotency_key,
                endpoint=endpoint,
            )
            
            # Check if expired
            if existing.is_expired:
                existing.delete()
                return None
            
            # Check request hash matches
            if existing.request_hash != request_hash:
                raise IdempotencyKeyConflictError(
                    idempotency_key,
                    "Idempotency key already used with different request data"
                )
            
            # Return cached response
            return CachedResponse(
                status=existing.response_status,
                body=existing.response_body,
                from_cache=True
            )
            
        except ForensicIdempotencyKey.DoesNotExist:
            return None
    
    def _cache_idempotency(
        self,
        idempotency_key: str,
        endpoint: str,
        request_data: dict,
        response_status: int,
        response_body: dict,
    ) -> ForensicIdempotencyKey:
        """Cache response for idempotency key."""
        request_hash = sha256_hex(canonical_json(request_data))
        
        return ForensicIdempotencyKey.objects.create(
            idempotency_key=idempotency_key,
            endpoint=endpoint,
            request_hash=request_hash,
            response_status=response_status,
            response_body=response_body,
            expires_at=timezone.now() + self.idempotency_ttl,
        )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_client_ip(request) -> Optional[str]:
    """Extract client IP from Django request."""
    if request is None:
        return None
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    
    return request.META.get('REMOTE_ADDR')


def get_user_agent(request) -> str:
    """Extract user agent from Django request."""
    if request is None:
        return ''
    
    return request.META.get('HTTP_USER_AGENT', '')[:500]
