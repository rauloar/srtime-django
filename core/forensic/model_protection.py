"""
Forensic Model Protection
Mixin and utilities to block unauthorized model modifications.

Protected models cannot be saved or deleted unless:
1. The operation is within a ForensicContext
2. OR the model is being created for the first time

Any unauthorized modification attempt is:
1. Blocked with ForensicImmutabilityError
2. Logged to ForensicImmutabilityViolation table
"""
import inspect
from typing import Optional, Set, Type

from django.db import models
from django.utils import timezone

from core.forensic.context import get_forensic_context, is_forensic_context_active


# =============================================================================
# EXCEPTIONS
# =============================================================================

class ForensicImmutabilityError(Exception):
    """
    Raised when attempting to modify a protected model outside forensic context.
    
    This exception indicates a security violation that has been logged.
    """
    
    def __init__(
        self,
        model_name: str,
        instance_id: Optional[int],
        operation: str,
        message: Optional[str] = None,
    ):
        self.model_name = model_name
        self.instance_id = instance_id
        self.operation = operation
        
        default_message = (
            f"FORENSIC SECURITY VIOLATION: Attempted {operation} on "
            f"{model_name}(id={instance_id}) outside forensic context. "
            f"Use ForensicReviewService or ForensicExportService instead."
        )
        super().__init__(message or default_message)


class ForensicDeleteBlockedError(ForensicImmutabilityError):
    """Raised when attempting to delete a protected model."""
    
    def __init__(self, model_name: str, instance_id: Optional[int]):
        super().__init__(
            model_name=model_name,
            instance_id=instance_id,
            operation='DELETE',
            message=(
                f"FORENSIC SECURITY VIOLATION: DELETE operations are NEVER "
                f"allowed on {model_name}. Records are immutable."
            )
        )


class ForensicUpdateBlockedError(ForensicImmutabilityError):
    """Raised when attempting to update a protected model in closed state."""
    
    def __init__(self, model_name: str, instance_id: Optional[int], status: str):
        super().__init__(
            model_name=model_name,
            instance_id=instance_id,
            operation='UPDATE',
            message=(
                f"FORENSIC SECURITY VIOLATION: Cannot modify {model_name}"
                f"(id={instance_id}) in status '{status}'. Record is immutable."
            )
        )


# =============================================================================
# VIOLATION LOGGING
# =============================================================================

def log_immutability_violation(
    table_name: str,
    record_id: Optional[int],
    operation: str,
    old_values: dict,
    attempted_by: Optional[str] = None,
) -> None:
    """
    Log an immutability violation to the forensic audit table.
    
    This runs outside the normal model protection to prevent recursion.
    """
    # Import here to avoid circular imports
    from core.models_forensic import ForensicImmutabilityViolation
    
    # Get caller information for attempted_by if not provided
    if attempted_by is None:
        # Walk the stack to find the original caller
        stack = inspect.stack()
        caller_info = []
        for frame_info in stack[2:7]:  # Skip this function and its caller
            caller_info.append(f"{frame_info.filename}:{frame_info.lineno}")
        attempted_by = ' -> '.join(caller_info)
    
    # Create violation record (bypasses protection via direct SQL concept,
    # but since ForensicImmutabilityViolation is the logger itself,
    # we use a special flag approach)
    try:
        # Use raw create to bypass any model-level checks
        ForensicImmutabilityViolation.objects.create(
            table_name=table_name,
            record_id=record_id or 0,
            attempted_operation=operation,
            attempted_by=attempted_by[:100] if attempted_by else 'unknown',
            attempted_at=timezone.now(),
            old_values=old_values,
            blocked=True,
        )
    except Exception:
        # If we can't log, at least don't crash
        # The violation will still be raised
        import logging
        logger = logging.getLogger('forensic.violations')
        logger.error(
            f"Failed to log violation: {table_name}.{record_id} {operation}",
            exc_info=True
        )


# =============================================================================
# MODEL PROTECTION MIXIN
# =============================================================================

class ForensicModelProtectionMixin:
    """
    Django Model Mixin that enforces forensic context for write operations.
    
    When applied to a model:
    1. save() requires active ForensicContext (except for initial creation)
    2. delete() is ALWAYS blocked
    3. Violations are logged to ForensicImmutabilityViolation
    
    Usage:
        class ShadowReviewDecision(ForensicModelProtectionMixin, models.Model):
            FORENSIC_PROTECTED = True  # Required marker
            FORENSIC_IMMUTABLE_STATUSES = ['CLOSED']  # Optional: status-based immutability
            ...
    """
    
    # Override in subclass to enable protection
    FORENSIC_PROTECTED: bool = False
    
    # Status values that make the record completely immutable
    FORENSIC_IMMUTABLE_STATUSES: Set[str] = frozenset()
    
    # Field that contains the status (default: 'status')
    FORENSIC_STATUS_FIELD: str = 'status'
    
    # Allow initial creation without context (set to False for audit tables)
    FORENSIC_ALLOW_INITIAL_CREATE: bool = True
    
    def save(self, *args, **kwargs):
        """
        Override save to enforce forensic context.
        
        Blocks saves unless:
        1. Model is not protected (FORENSIC_PROTECTED = False)
        2. This is initial creation AND FORENSIC_ALLOW_INITIAL_CREATE is True
        3. A ForensicContext is active
        """
        if not getattr(self, 'FORENSIC_PROTECTED', False):
            # Not a protected model, allow save
            return super().save(*args, **kwargs)
        
        is_new = self.pk is None
        
        # Check if initial creation is allowed without context
        if is_new and getattr(self, 'FORENSIC_ALLOW_INITIAL_CREATE', True):
            return super().save(*args, **kwargs)
        
        # Check for forensic context
        context = get_forensic_context()
        
        if context is None:
            # NO FORENSIC CONTEXT - BLOCK AND LOG
            self._handle_unauthorized_save()
        
        # Check for immutable status
        if not is_new:
            self._check_immutable_status()
        
        # Context is active - record the save
        if context:
            context.record_save(
                self.__class__.__name__,
                self.pk
            )
        
        return super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """
        Override delete to ALWAYS block.
        
        Forensic records are NEVER deleted.
        """
        if not getattr(self, 'FORENSIC_PROTECTED', False):
            # Not a protected model, allow delete
            return super().delete(*args, **kwargs)
        
        # Block and log
        self._handle_unauthorized_delete()
    
    def _handle_unauthorized_save(self):
        """Handle unauthorized save attempt."""
        model_name = self.__class__.__name__
        instance_id = self.pk
        
        # Capture current state for logging
        old_values = {}
        if instance_id:
            try:
                old_instance = self.__class__.objects.get(pk=instance_id)
                for field in self._meta.fields:
                    old_values[field.name] = str(getattr(old_instance, field.name, None))
            except self.__class__.DoesNotExist:
                pass
        
        # Log the violation
        log_immutability_violation(
            table_name=self._meta.db_table,
            record_id=instance_id,
            operation='UPDATE' if instance_id else 'INSERT',
            old_values=old_values,
        )
        
        # Raise exception
        raise ForensicImmutabilityError(
            model_name=model_name,
            instance_id=instance_id,
            operation='UPDATE' if instance_id else 'INSERT',
        )
    
    def _handle_unauthorized_delete(self):
        """Handle unauthorized delete attempt."""
        model_name = self.__class__.__name__
        instance_id = self.pk
        
        # Capture current state for logging
        old_values = {}
        for field in self._meta.fields:
            old_values[field.name] = str(getattr(self, field.name, None))
        
        # Log the violation
        log_immutability_violation(
            table_name=self._meta.db_table,
            record_id=instance_id,
            operation='DELETE',
            old_values=old_values,
        )
        
        # Raise exception
        raise ForensicDeleteBlockedError(
            model_name=model_name,
            instance_id=instance_id,
        )
    
    def _check_immutable_status(self):
        """Check if record is in an immutable status."""
        immutable_statuses = getattr(self, 'FORENSIC_IMMUTABLE_STATUSES', set())
        if not immutable_statuses:
            return
        
        status_field = getattr(self, 'FORENSIC_STATUS_FIELD', 'status')
        
        # Get current status from database
        try:
            current_db_record = self.__class__.objects.get(pk=self.pk)
            current_status = getattr(current_db_record, status_field, None)
            
            if current_status in immutable_statuses:
                # Record is immutable - block and log
                log_immutability_violation(
                    table_name=self._meta.db_table,
                    record_id=self.pk,
                    operation='UPDATE',
                    old_values={status_field: current_status},
                )
                
                raise ForensicUpdateBlockedError(
                    model_name=self.__class__.__name__,
                    instance_id=self.pk,
                    status=current_status,
                )
        except self.__class__.DoesNotExist:
            pass


# =============================================================================
# REGISTRY OF PROTECTED MODELS
# =============================================================================

# Models that should be protected (populated at import time)
PROTECTED_MODELS: Set[Type[models.Model]] = set()


def register_protected_model(model_class: Type[models.Model]) -> Type[models.Model]:
    """
    Decorator to register a model as forensically protected.
    
    Usage:
        @register_protected_model
        class ShadowReviewDecision(ForensicModelProtectionMixin, models.Model):
            FORENSIC_PROTECTED = True
            ...
    """
    PROTECTED_MODELS.add(model_class)
    return model_class


def is_protected_model(model_class: Type[models.Model]) -> bool:
    """Check if a model class is forensically protected."""
    return (
        model_class in PROTECTED_MODELS or
        getattr(model_class, 'FORENSIC_PROTECTED', False)
    )
