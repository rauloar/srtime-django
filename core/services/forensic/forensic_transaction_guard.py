class OptimisticLockError(Exception):
    """Raised when optimistic locking detects a stale version."""


class ForensicTransactionGuard:
    """Minimal guard implementation for compatibility tests."""

    def execute(self, fn, *args, **kwargs):
        return fn(*args, **kwargs)
