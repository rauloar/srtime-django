"""
Flexible Processor - Result Model (Phase 7)
Final result object for the flexible calculation pipeline.

This is the output contract between the engine and persistence layer.
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional, Dict, Any

from .status import FlexStatus
from .forensic import Warning, Confidence


@dataclass
class DailyCalculationResult:
    """
    Complete result of a daily attendance calculation.
    
    This object contains all computed values ready for persistence.
    It represents the contract between the calculation engine and the storage layer.
    """
    # Identity
    employee_id: int
    target_date: date
    calculation_mode: str  # "FLEXIBLE" or "STRUCTURED"
    
    # Timestamps
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    
    # Time metrics (all in minutes)
    worked_minutes: int = 0
    break_minutes: int = 0
    net_worked_minutes: int = 0
    
    # Legal classification
    regular_minutes: int = 0
    overtime_minutes: int = 0
    night_minutes: int = 0
    
    # Structured mode only (NULL in flexible)
    expected_minutes: Optional[int] = None
    late_minutes: Optional[int] = None
    early_out_minutes: Optional[int] = None
    
    # Status
    status: str = ""
    
    # Flags
    is_holiday: bool = False
    exceeded_daily_limit: bool = False
    has_orphan_punch: bool = False
    requires_review: bool = False
    
    # Audit fields
    calculation_warnings: List[Warning] = field(default_factory=list)
    calculation_confidence: Confidence = Confidence.HIGH
    blocks_count: int = 0
    
    # Traceability
    policy_id: Optional[int] = None
    timetable_id: Optional[int] = None
    engine_version: str = "2.0.0"
    calculated_at: Optional[datetime] = None
    
    # Forensic extensions
    forensic_flags: Dict[str, bool] = field(default_factory=dict)
    source_punches_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "employee_id": self.employee_id,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "calculation_mode": self.calculation_mode,
            "check_in": self.check_in.isoformat() if self.check_in else None,
            "check_out": self.check_out.isoformat() if self.check_out else None,
            "worked_minutes": self.worked_minutes,
            "break_minutes": self.break_minutes,
            "net_worked_minutes": self.net_worked_minutes,
            "regular_minutes": self.regular_minutes,
            "overtime_minutes": self.overtime_minutes,
            "night_minutes": self.night_minutes,
            "expected_minutes": self.expected_minutes,
            "late_minutes": self.late_minutes,
            "early_out_minutes": self.early_out_minutes,
            "status": self.status,
            "is_holiday": self.is_holiday,
            "exceeded_daily_limit": self.exceeded_daily_limit,
            "has_orphan_punch": self.has_orphan_punch,
            "requires_review": self.requires_review,
            "calculation_confidence": self.calculation_confidence.value,
            "blocks_count": self.blocks_count,
            "engine_version": self.engine_version,
            "calculated_at": self.calculated_at.isoformat() if self.calculated_at else None,
        }
