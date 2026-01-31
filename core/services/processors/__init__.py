"""
Attendance Processor Interface
Abstract base class for attendance calculation strategies.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional, Protocol

from core.domain.flexible.result import DailyCalculationResult


@dataclass
class ProcessorContext:
    """
    Context passed to all processors.
    Contains all data needed for calculation.
    """
    employee_id: int
    target_date: date
    
    # Schedule context
    timetable_id: Optional[int] = None
    on_duty: Optional[datetime] = None
    off_duty: Optional[datetime] = None
    break_minutes: int = 0
    required_minutes: int = 480
    
    # Logs/Punches
    logs: List = None  # AttendanceLog list
    
    # External data (no DB access in processors)
    holidays: List[date] = None
    has_leave: bool = False
    is_rest_day: bool = False
    
    # Policy overrides
    rounding_rule: Optional[str] = None
    late_allow_minutes: int = 0
    early_leave_allow_minutes: int = 0


class AttendanceProcessor(ABC):
    """
    Abstract base class for attendance calculation strategies.
    
    All processors must:
    - Accept ProcessorContext
    - Return DailyCalculationResult
    - NOT access database
    - NOT modify input data
    """
    
    @abstractmethod
    def process(self, context: ProcessorContext) -> DailyCalculationResult:
        """
        Process attendance for a single day.
        
        Args:
            context: ProcessorContext with all required data
        
        Returns:
            DailyCalculationResult with calculated values
        """
        pass
    
    @property
    @abstractmethod
    def mode(self) -> str:
        """Return the calculation mode (FLEXIBLE or STRUCTURED)."""
        pass
