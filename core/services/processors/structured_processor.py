"""
Structured Processor - Strategy Implementation
Wraps the existing fixed-schedule logic for use in the main attendance engine.

This processor handles traditional schedules with expected on_duty/off_duty times.
"""
from datetime import datetime, timedelta
from typing import Optional

from core.domain.flexible.result import DailyCalculationResult
from core.domain.flexible.forensic import Confidence
from . import AttendanceProcessor, ProcessorContext


ENGINE_VERSION = "2.0.0"


class StructuredProcessor(AttendanceProcessor):
    """
    Processor for structured (fixed schedule) attendance.
    
    Calculates:
    - Late minutes
    - Early leave minutes
    - Worked minutes
    - Overtime minutes
    
    Based on expected on_duty and off_duty times.
    """
    
    @property
    def mode(self) -> str:
        return "STRUCTURED"
    
    def process(self, context: ProcessorContext) -> DailyCalculationResult:
        """
        Process structured attendance.
        
        Uses traditional fixed-schedule logic with late/early calculations.
        """
        now = datetime.now()
        logs = context.logs or []
        
        # Initialize result
        result = DailyCalculationResult(
            employee_id=context.employee_id,
            target_date=context.target_date,
            calculation_mode="STRUCTURED",
            timetable_id=context.timetable_id,
            engine_version=ENGINE_VERSION,
            calculated_at=now,
            source_punches_count=len(logs),
            expected_minutes=context.required_minutes,
        )
        
        # No logs = Absent
        if not logs:
            result.status = "Absent"
            return result
        
        # Find check-in (first in-punch)
        check_in = self._find_check_in(logs)
        
        # Find check-out (last out-punch)
        check_out = self._find_check_out(logs)
        
        # Apply rounding
        if check_in and context.rounding_rule:
            check_in = self._round_time(check_in, context.rounding_rule, is_check_in=True)
        
        if check_out and context.rounding_rule:
            check_out = self._round_time(check_out, context.rounding_rule, is_check_in=False)
        
        result.check_in = check_in
        result.check_out = check_out
        
        # Calculate late minutes
        late_minutes = 0
        if check_in and context.on_duty:
            if check_in > context.on_duty:
                late_minutes = int((check_in - context.on_duty).total_seconds() / 60)
                
                # Apply tolerance
                if context.late_allow_minutes and late_minutes <= context.late_allow_minutes:
                    late_minutes = 0
        
        result.late_minutes = late_minutes
        
        # Calculate early leave minutes
        early_minutes = 0
        if check_out and context.off_duty:
            if check_out < context.off_duty:
                early_minutes = int((context.off_duty - check_out).total_seconds() / 60)
                
                # Apply tolerance
                if context.early_leave_allow_minutes and early_minutes <= context.early_leave_allow_minutes:
                    early_minutes = 0
        
        result.early_out_minutes = early_minutes
        
        # Calculate worked minutes
        worked_minutes = 0
        if check_in and check_out:
            worked_delta = (check_out - check_in).total_seconds() / 60
            
            # Subtract break
            if context.break_minutes:
                worked_delta = max(0, worked_delta - context.break_minutes)
            
            worked_minutes = int(worked_delta)
        
        result.worked_minutes = worked_minutes
        result.break_minutes = context.break_minutes
        result.net_worked_minutes = worked_minutes  # No additional break deduction
        
        # Calculate overtime
        overtime_minutes = 0
        if check_out and context.off_duty:
            if check_out > context.off_duty:
                overtime_minutes = int((check_out - context.off_duty).total_seconds() / 60)
        
        result.overtime_minutes = overtime_minutes
        
        # Calculate regular (net - overtime, capped at expected)
        result.regular_minutes = min(
            worked_minutes - overtime_minutes,
            context.required_minutes
        )
        if result.regular_minutes < 0:
            result.regular_minutes = 0
        
        # Determine status
        result.status = self._determine_status(
            late_minutes=late_minutes,
            early_minutes=early_minutes,
            overtime_minutes=overtime_minutes,
            worked_minutes=worked_minutes,
            required_minutes=context.required_minutes,
        )
        
        # Check holiday
        if context.holidays and context.target_date in context.holidays:
            result.is_holiday = True
        
        # Set confidence
        result.calculation_confidence = Confidence.HIGH
        result.requires_review = False
        
        # Orphan punch check
        if check_in and not check_out:
            result.has_orphan_punch = True
            result.requires_review = True
            result.status = "Incomplete"
        
        result.blocks_count = 1 if (check_in and check_out) else 0
        
        return result
    
    def _find_check_in(self, logs: list) -> Optional[datetime]:
        """Find first check-in punch."""
        for log in logs:
            state = int(log.punch) if log.punch is not None else 0
            if state in [0, 4, 8]:  # Check-in states
                return log.timestamp
        return None
    
    def _find_check_out(self, logs: list) -> Optional[datetime]:
        """Find last check-out punch."""
        for log in reversed(logs):
            state = int(log.punch) if log.punch is not None else 0
            if state in [1, 5, 9]:  # Check-out states
                return log.timestamp
        return None
    
    def _round_time(self, dt: datetime, rule: str, is_check_in: bool) -> datetime:
        """Apply rounding rules to timestamp."""
        if rule == "none" or not rule:
            return dt
        
        minutes = dt.minute
        
        if rule == "round_15":
            # Round to nearest 15 minutes
            remainder = minutes % 15
            if remainder < 8:
                new_minutes = minutes - remainder
            else:
                new_minutes = minutes + (15 - remainder)
        elif rule == "round_30":
            # Round to nearest 30 minutes
            remainder = minutes % 30
            if remainder < 15:
                new_minutes = minutes - remainder
            else:
                new_minutes = minutes + (30 - remainder)
        elif rule == "advance":
            # Always round up for check-in
            if is_check_in:
                remainder = minutes % 15
                if remainder > 0:
                    new_minutes = minutes + (15 - remainder)
                else:
                    new_minutes = minutes
            else:
                new_minutes = minutes
        elif rule == "delay":
            # Always round down for check-out
            if not is_check_in:
                remainder = minutes % 15
                new_minutes = minutes - remainder
            else:
                new_minutes = minutes
        else:
            return dt
        
        # Handle hour overflow
        hour_delta = new_minutes // 60
        new_minutes = new_minutes % 60
        
        return dt.replace(minute=new_minutes, second=0, microsecond=0) + timedelta(hours=hour_delta)
    
    def _determine_status(
        self,
        late_minutes: int,
        early_minutes: int,
        overtime_minutes: int,
        worked_minutes: int,
        required_minutes: int,
    ) -> str:
        """Determine status based on calculated values."""
        statuses = []
        
        if late_minutes > 0:
            statuses.append("Late")
        
        if early_minutes > 0:
            statuses.append("Early Leave")
        
        if overtime_minutes > 0:
            statuses.append("Overtime")
        
        if not statuses:
            if worked_minutes >= required_minutes:
                return "Normal"
            else:
                return "Attendance"
        
        return ", ".join(statuses)
