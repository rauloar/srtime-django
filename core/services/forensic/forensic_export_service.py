class TSAService:
    """Minimal timestamp authority service placeholder."""


class ForensicExportService:
    """Compatibility service used by forensic tests."""

    def __init__(self):
        self.tsa = TSAService()
