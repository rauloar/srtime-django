"""
Unified Schedule Resolution Service

Single source of truth for schedule resolution used by both V1 and V2 engines.

Priority:
1. ScheduleOverride (highest)
2. EmployeeShift (EMPLOYEE scope)
3. EmployeeShift (DEPARTMENT scope)
4. Department.default_shift
5. Implicit rest day (no schedule)

This module ensures consistency between engines and supports both:
- Weekly cycles (0-6 = Mon-Sun)
- Long cycles (cycle_days > 0)
"""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime, date, time, timedelta
from typing import Optional
import logging
from django.db.models import Q

from core import models

logger = logging.getLogger(__name__)


class ScheduleSource(Enum):
    """Enum for schedule resolution source (type-safe, replaces strings)."""
    OVERRIDE = "OVERRIDE"
    EMPLOYEE_SHIFT = "EMPLOYEE_SHIFT"
    DEPARTMENT_SHIFT = "DEPARTMENT_SHIFT"
    IMPLICIT_REST = "IMPLICIT_REST"
    UNRESOLVED = "UNRESOLVED"


class ScheduleResolutionError(Enum):
    """Why schedule resolution failed."""
    NO_SHIFT_ASSIGNED = "NO_SHIFT_ASSIGNED"
    SHIFT_NO_TIMETABLES = "SHIFT_NO_TIMETABLES"
    SHIFT_TIMETABLE_MISSING_DAY = "SHIFT_TIMETABLE_MISSING_DAY"
    INVALID_TIMETABLE = "INVALID_TIMETABLE"


@dataclass
class ResolvedSchedule:
    """
    Result of schedule resolution.
    
    Used by BOTH V1 and V2 engines to ensure consistency.
    """
    is_valid: bool
    timetable: Optional[models.Timetable]
    source: ScheduleSource
    error: Optional[ScheduleResolutionError]
    on_duty_dt: Optional[datetime]
    off_duty_dt: Optional[datetime]
    search_start: datetime
    search_end: datetime
    
    def __post_init__(self):
        """Validate state consistency."""
        if self.is_valid and self.timetable is None:
            raise ValueError("Cannot have is_valid=True with timetable=None")
        
        if not self.is_valid and self.error is None:
            raise ValueError("Must provide error when is_valid=False")


def resolve_schedule_unified(
    employee_id: int,
    target_date: date,
) -> ResolvedSchedule:
    """
    Unified schedule resolution for both V1 and V2 engines.
    
    This is the SINGLE SOURCE OF TRUTH for schedule resolution.
    Both engines call this function to ensure consistency.
    
    Args:
        employee_id: Employee ID
        target_date: Date to resolve schedule for
    
    Returns:
        ResolvedSchedule with timetable and metadata
    
    Raises:
        ValueError: If internal state is inconsistent
    """
    try:
        # 1. Check ScheduleOverride (highest priority)
        override = models.ScheduleOverride.objects.filter(
            employee_id=employee_id,
            date=target_date
        ).select_related('timetable').first()
        
        if override and override.timetable:
            logger.debug(
                f"Schedule resolved via OVERRIDE for employee {employee_id} on {target_date}"
            )
            return _build_resolved_schedule(
                timetable=override.timetable,
                target_date=target_date,
                source=ScheduleSource.OVERRIDE,
            )
        
        # 2. Check EmployeeShift (EMPLOYEE scope)
        emp_shift = models.EmployeeShift.objects.filter(
            scope='EMPLOYEE',
            employee_id=employee_id,
            start_date__lte=target_date,
        ).filter(
            Q(end_date__gte=target_date) | Q(end_date__isnull=True)
        ).select_related('shift').first()
        
        if emp_shift and emp_shift.shift:
            shift_tt, error_code = _resolve_shift_timetable(
                shift=emp_shift.shift,
                emp_shift=emp_shift,
                target_date=target_date,
            )
            if shift_tt and shift_tt.timetable:
                logger.debug(
                    f"Schedule resolved via EMPLOYEE_SHIFT for employee {employee_id} on {target_date}"
                )
                return _build_resolved_schedule(
                    timetable=shift_tt.timetable,
                    target_date=target_date,
                    source=ScheduleSource.EMPLOYEE_SHIFT,
                )
            elif error_code:
                # Shift is assigned but has issues with timetables
                logger.warning(
                    f"Employee has shift assigned but timetable resolution failed: {error_code}"
                )
                return ResolvedSchedule(
                    is_valid=False,
                    timetable=None,
                    source=ScheduleSource.EMPLOYEE_SHIFT,
                    error=error_code,
                    on_duty_dt=None,
                    off_duty_dt=None,
                    search_start=datetime.combine(target_date, time.min),
                    search_end=datetime.combine(target_date, time.max),
                )
        
        # 3. Check EmployeeShift (DEPARTMENT scope) - Fallback
        emp = models.Employee.objects.filter(id=employee_id).select_related(
            'department'
        ).first()
        
        if emp and emp.department:
            dept_shift = models.EmployeeShift.objects.filter(
                scope='DEPARTMENT',
                department_id=emp.department.id,
                start_date__lte=target_date,
            ).filter(
                Q(end_date__gte=target_date) | Q(end_date__isnull=True)
            ).select_related('shift').first()
            
            if dept_shift and dept_shift.shift:
                shift_tt, error_code = _resolve_shift_timetable(
                    shift=dept_shift.shift,
                    emp_shift=dept_shift,
                    target_date=target_date,
                )
                if shift_tt and shift_tt.timetable:
                    logger.debug(
                        f"Schedule resolved via DEPARTMENT_SHIFT for employee {employee_id} on {target_date}"
                    )
                    return _build_resolved_schedule(
                        timetable=shift_tt.timetable,
                        target_date=target_date,
                        source=ScheduleSource.DEPARTMENT_SHIFT,
                    )
                elif error_code:
                    # Department shift is assigned but has timetable issues
                    logger.warning(
                        f"Department has shift assigned but timetable resolution failed: {error_code}"
                    )
                    return ResolvedSchedule(
                        is_valid=False,
                        timetable=None,
                        source=ScheduleSource.DEPARTMENT_SHIFT,
                        error=error_code,
                        on_duty_dt=None,
                        off_duty_dt=None,
                        search_start=datetime.combine(target_date, time.min),
                        search_end=datetime.combine(target_date, time.max),
                    )
        
        # 4. Implicit rest day - no schedule found
        logger.warning(
            f"No schedule found for employee {employee_id} on {target_date} - implicit rest day"
        )
        return ResolvedSchedule(
            is_valid=False,
            timetable=None,
            source=ScheduleSource.IMPLICIT_REST,
            error=ScheduleResolutionError.NO_SHIFT_ASSIGNED,
            on_duty_dt=None,
            off_duty_dt=None,
            search_start=datetime.combine(target_date, time.min),
            search_end=datetime.combine(target_date, time.max),
        )
    
    except Exception as e:
        logger.error(
            f"Schedule resolution failed for employee {employee_id} on {target_date}: {e}",
            exc_info=True
        )
        return ResolvedSchedule(
            is_valid=False,
            timetable=None,
            source=ScheduleSource.UNRESOLVED,
            error=ScheduleResolutionError.INVALID_TIMETABLE,
            on_duty_dt=None,
            off_duty_dt=None,
            search_start=datetime.combine(target_date, time.min),
            search_end=datetime.combine(target_date, time.max),
        )


def _resolve_shift_timetable(
    shift: models.Shift,
    emp_shift: models.EmployeeShift,
    target_date: date,
) -> tuple:
    """
    Resolve which timetable applies for a shift on a given date.
    
    Returns: (ShiftTimetable or None, error_code or None)
    
    Error codes:
    - SHIFT_NO_TIMETABLES: Shift has no ShiftTimetables configured
    - SHIFT_TIMETABLE_MISSING_DAY: Shift has timetables but not for this day
    """
    try:
        # Check if shift has any timetables configured
        has_timetables = models.ShiftTimetable.objects.filter(
            shift=shift
        ).exists()
        
        if not has_timetables:
            logger.warning(
                f"Shift {shift.id} ({shift.name}) has no ShiftTimetable configured"
            )
            return (None, ScheduleResolutionError.SHIFT_NO_TIMETABLES)
        
        # Determine day_index based on cycle type
        if hasattr(shift, 'cycle_days') and shift.cycle_days and shift.cycle_days > 0:
            # Long cycle (e.g., 28-day rotation)
            if not emp_shift.start_date:
                logger.error(
                    f"EmployeeShift {emp_shift.id} has no start_date but shift has cycle_days"
                )
                return (None, ScheduleResolutionError.INVALID_TIMETABLE)
            
            days_since_start = (target_date - emp_shift.start_date).days
            day_index = days_since_start % shift.cycle_days
            
            logger.debug(
                f"Shift {shift.id} uses cycle (cycle_days={shift.cycle_days}), "
                f"day_index={day_index} for {target_date}"
            )
        else:
            # Weekly cycle (0=Mon, 6=Sun) - default behavior
            day_index = target_date.weekday()
            logger.debug(
                f"Shift {shift.id} uses weekly cycle, day_index={day_index} for {target_date}"
            )
        
        # Find ShiftTimetable for this day
        shift_tt = models.ShiftTimetable.objects.filter(
            shift=shift,
            day_index=day_index,
        ).select_related('timetable').first()
        
        if not shift_tt:
            logger.warning(
                f"No ShiftTimetable for shift {shift.id} on day_index {day_index} "
                f"(target_date: {target_date}) - shift has timetables but not for this day"
            )
            return (None, ScheduleResolutionError.SHIFT_TIMETABLE_MISSING_DAY)
        
        return (shift_tt, None)  # Success: return timetable and no error
    
    except Exception as e:
        logger.error(
            f"Shift timetable resolution failed for shift {shift.id}: {e}",
            exc_info=True
        )
        return (None, ScheduleResolutionError.INVALID_TIMETABLE)


def _build_resolved_schedule(
    timetable: models.Timetable,
    target_date: date,
    source: ScheduleSource,
) -> ResolvedSchedule:
    """
    Build ResolvedSchedule from timetable.
    
    Handles both fixed and flexible schedules.
    Correctly handles overnight shifts (off_duty < on_duty).
    Handles CharField time fields (stored as HH:MM strings).
    
    Args:
        timetable: Timetable model
        target_date: Date being resolved
        source: Where the timetable came from
    
    Returns:
        ResolvedSchedule with all metadata
    """
    search_start = datetime.combine(target_date, time(0, 0))
    search_end = datetime.combine(target_date + timedelta(days=1), time(0, 0))
    
    on_duty_dt = None
    off_duty_dt = None
    
    # Helper function to parse time field (can be string or time object)
    def parse_time_field(field_value):
        """Convert CharField time (HH:MM or HH:MM:SS) or time object to time object."""
        if field_value is None:
            return None
        
        # Already a time object
        if isinstance(field_value, time):
            return field_value
        
        # Parse string format (supports both HH:MM and HH:MM:SS)
        if isinstance(field_value, str):
            field_value = field_value.strip()
            if not field_value:  # Empty string
                return None
            try:
                # Try HH:MM:SS format first (most common from Timetable)
                try:
                    return datetime.strptime(field_value, "%H:%M:%S").time()
                except ValueError:
                    # Fallback to HH:MM format
                    return datetime.strptime(field_value, "%H:%M").time()
            except (ValueError, TypeError) as e:
                logger.error(f"Cannot parse time field '{field_value}': {e}")
                return None
        
        logger.error(f"Unexpected time field type: {type(field_value)}")
        return None
    
    # Parse time fields
    on_duty_time = parse_time_field(timetable.on_duty_time)
    off_duty_time = parse_time_field(timetable.off_duty_time)
    
    if on_duty_time is None:
        logger.warning(f"Timetable {timetable.id} has no valid on_duty_time")
    if off_duty_time is None:
        logger.warning(f"Timetable {timetable.id} has no valid off_duty_time")
    
    # Calculate on_duty datetime
    if on_duty_time:
        on_duty_dt = datetime.combine(target_date, on_duty_time)
    
    # Calculate off_duty datetime (handle overnight shifts)
    if off_duty_time:
        off_duty_dt = datetime.combine(target_date, off_duty_time)
        
        # If off_duty < on_duty, it's an overnight shift
        if on_duty_time and off_duty_time < on_duty_time:
            off_duty_dt = datetime.combine(
                target_date + timedelta(days=1), 
                off_duty_time
            )
            logger.debug(
                f"Overnight shift detected for timetable {timetable.id}: "
                f"on_duty={on_duty_time}, off_duty={off_duty_time}"
            )
    
    return ResolvedSchedule(
        is_valid=True,
        timetable=timetable,
        source=source,
        error=None,
        on_duty_dt=on_duty_dt,
        off_duty_dt=off_duty_dt,
        search_start=search_start,
        search_end=search_end,
    )
