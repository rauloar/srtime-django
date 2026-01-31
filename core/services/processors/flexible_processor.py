"""
Flexible Processor - Strategy Implementation
Wraps the domain flexible engine for use in the main attendance engine.
"""
from datetime import datetime
from typing import List

from core.domain.flexible import (
    Punch, 
    FlexPolicy,
    DailyCalculationResult,
)
from core.services.flexible_engine import calculate_flexible_day
from . import AttendanceProcessor, ProcessorContext


class FlexibleProcessor(AttendanceProcessor):
    """
    Processor for flexible (punch-based) schedules.
    
    Delegates calculation to the domain engine.
    This is a thin wrapper that adapts the ProcessorContext
    to the domain function signature.
    """
    
    def __init__(self, policy: FlexPolicy = None):
        """
        Initialize with optional policy override.
        
        Args:
            policy: FlexPolicy to use. If None, default policy is used.
        """
        self._policy = policy or FlexPolicy()
    
    @property
    def mode(self) -> str:
        return "FLEXIBLE"
    
    def process(self, context: ProcessorContext) -> DailyCalculationResult:
        """
        Process flexible attendance.
        
        Converts logs to Punches and delegates to domain engine.
        """
        # Convert AttendanceLog objects to Punch objects
        punches = self._convert_logs_to_punches(context.logs or [])
        
        # Get holidays (already provided in context, no DB access)
        holidays = context.holidays or []
        
        # Build policy from context if needed
        policy = self._build_policy(context)
        
        # Delegate to domain engine
        result = calculate_flexible_day(
            employee_id=context.employee_id,
            target_date=context.target_date,
            punches=punches,
            policy=policy,
            holidays=holidays,
            has_leave=context.has_leave,
            is_rest_day=context.is_rest_day,
        )
        
        # Set timetable_id from context
        result.timetable_id = context.timetable_id
        
        return result
    
    def _convert_logs_to_punches(self, logs: List) -> List[Punch]:
        """
        Convert AttendanceLog model objects to domain Punch objects.
        
        Args:
            logs: List of AttendanceLog ORM objects
        
        Returns:
            List of domain Punch objects
        """
        punches = []
        
        for log in logs:
            # Get punch state
            state = int(log.punch) if log.punch is not None else 0
            
            # Only include check-in (0,4,8) and check-out (1,5,9) punches
            is_valid_punch = state in [0, 1, 4, 5, 8, 9]
            
            if is_valid_punch and log.timestamp:
                punch = Punch(
                    id=log.id,
                    timestamp=log.timestamp,
                    device_id=str(log.device_id) if log.device_id else "UNKNOWN",
                )
                punches.append(punch)
        
        return punches
    
    def _build_policy(self, context: ProcessorContext) -> FlexPolicy:
        """
        Build FlexPolicy from context, merging with defaults.
        """
        return FlexPolicy(
            break_threshold_minutes=context.required_minutes or 360,
            break_duration_minutes=context.break_minutes or 30,
            daily_regular_minutes=context.required_minutes or 480,
        )
