from .forensic_transaction_guard import ForensicTransactionGuard


class ForensicReviewService:
    """Compatibility service used by forensic tests."""

    def __init__(self):
        self.guard = ForensicTransactionGuard()
