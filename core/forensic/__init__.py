# Forensic Package
# =================
# Provides cryptographically coercive forensic path enforcement.
#
# Components:
# - context: Thread-safe forensic operation context
# - model_protection: Model-level save/delete blocking
# - middleware: Request tracking and idempotency enforcement
# - admin: Read-only Django admin for forensic models

from core.forensic.context import (
    ForensicContext,
    forensic_operation,
    get_forensic_context,
    is_forensic_context_active,
    forensic_context_from_request,
)

from core.forensic.model_protection import (
    ForensicModelProtectionMixin,
    ForensicImmutabilityError,
    ForensicDeleteBlockedError,
    ForensicUpdateBlockedError,
    log_immutability_violation,
    register_protected_model,
    is_protected_model,
    PROTECTED_MODELS,
)

from core.forensic.middleware import (
    ForensicRequestMiddleware,
    IdempotencyKeyRequiredMiddleware,
    ForensicAuditMiddleware,
)

__all__ = [
    # Context
    'ForensicContext',
    'forensic_operation',
    'get_forensic_context',
    'is_forensic_context_active',
    'forensic_context_from_request',
    # Model Protection
    'ForensicModelProtectionMixin',
    'ForensicImmutabilityError',
    'ForensicDeleteBlockedError',
    'ForensicUpdateBlockedError',
    'log_immutability_violation',
    'register_protected_model',
    'is_protected_model',
    'PROTECTED_MODELS',
    # Middleware
    'ForensicRequestMiddleware',
    'IdempotencyKeyRequiredMiddleware',
    'ForensicAuditMiddleware',
]
