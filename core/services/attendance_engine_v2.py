"""
Attendance Engine V2 - Hybrid Calculation Engine
Supports both STRUCTURED (fixed) and FLEXIBLE (punch-based) schedules.

Uses Strategy pattern to delegate calculation to appropriate processor.
This module handles:
- Schedule resolution
- Log retrieval
- Processor selection
- Result persistence

The processors themselves are pure and don't access DB.
"""
from datetime import date, datetime, timedelta, time
from typing import List, Optional, Set

from django.db.models import Q

from core import models
from .day_context import DayContext
from .processors import ProcessorContext
from .processors.flexible_processor import FlexibleProcessor
from .processors.structured_processor import StructuredProcessor


# =============================================================================
# SCHEDULE RESOLUTION (Existing Logic)
# =============================================================================

def _build_context(tt: models.Timetable, target_date: date, source: str) -> DayContext:
    """Build DayContext from Timetable for a given date."""
    # Calculate search window
    search_start = datetime.combine(target_date, time(0, 0))
    search_end = datetime.combine(target_date + timedelta(days=1), time(0, 0))
    
    # Calculate on_duty and off_duty datetimes
    on_duty_dt = None
    off_duty_dt = None
    
    if tt.on_duty_time:
        on_duty_dt = datetime.combine(target_date, tt.on_duty_time)
    
    if tt.off_duty_time:
        off_duty_dt = datetime.combine(target_date, tt.off_duty_time)
        # Handle overnight shifts
        if tt.on_duty_time and tt.off_duty_time < tt.on_duty_time:
            off_duty_dt = datetime.combine(target_date + timedelta(days=1), tt.off_duty_time)
    
    return DayContext(
        is_valid=True,
        timetable=tt,
        source=source,
        search_start=search_start,
        search_end=search_end,
        on_duty_dt=on_duty_dt,
        off_duty_dt=off_duty_dt,
    )


def resolve_schedule(employee_id: int, target_date: date) -> DayContext:
    """
    Resolve the schedule for an employee on a given date.
    
    Priority:
    1. ScheduleOverride (highest)
    2. EmployeeShift (calendar assignment)
    3. Department default shift (fallback)
    """
    # 1. Check Overrides
    override = models.ScheduleOverride.objects.filter(
        employee_id=employee_id,
        date=target_date
    ).select_related('timetable').first()
    
    if override and override.timetable:
        return _build_context(override.timetable, target_date, "OVERRIDE")
    
    # 2. Check EmployeeShift
    emp_shift = models.EmployeeShift.objects.filter(
        employee_id=employee_id,
        start_date__lte=target_date,
    ).filter(
        Q(end_date__gte=target_date) | Q(end_date__isnull=True)
    ).select_related('shift').first()
    
    if emp_shift and emp_shift.shift:
        shift = emp_shift.shift
        
        # Resolve timetable for this day
        if shift.cycle_days and shift.cycle_days > 0:
            # Cyclical shift
            days_since_start = (target_date - emp_shift.start_date).days
            cycle_index = days_since_start % shift.cycle_days
            
            shift_tt = models.ShiftTimetable.objects.filter(
                shift=shift,
                day_index=cycle_index
            ).select_related('timetable').first()
            
            if shift_tt and shift_tt.timetable:
                return _build_context(shift_tt.timetable, target_date, "SHIFT")
        else:
            # Weekly shift
            day_of_week = target_date.weekday()
            shift_tt = models.ShiftTimetable.objects.filter(
                shift=shift,
                day_index=day_of_week
            ).select_related('timetable').first()
            
            if shift_tt and shift_tt.timetable:
                return _build_context(shift_tt.timetable, target_date, "SHIFT")
    
    # 3. Check Department default
    emp = models.Employee.objects.filter(id=employee_id).select_related('department').first()
    if emp and emp.department and emp.department.default_shift_id:
        shift = models.Shift.objects.filter(id=emp.department.default_shift_id).first()
        if shift:
            day_of_week = target_date.weekday()
            shift_tt = models.ShiftTimetable.objects.filter(
                shift=shift,
                day_index=day_of_week
            ).select_related('timetable').first()
            
            if shift_tt and shift_tt.timetable:
                return _build_context(shift_tt.timetable, target_date, "DEPARTMENT")
    
    # No schedule found
    return DayContext(is_valid=False)


# =============================================================================
# DATA RETRIEVAL
# =============================================================================

def get_logs(user_id: str, start: datetime, end: datetime) -> List[models.AttendanceLog]:
    """Get attendance logs for a user in a time range."""
    return list(models.AttendanceLog.objects.filter(
        user_id=user_id,
        timestamp__gte=start,
        timestamp__lt=end
    ).order_by('timestamp'))


def get_holidays(target_date: date) -> Set[date]:
    """
    Get holiday dates around the target date.
    
    Returns a set of dates for O(1) lookup.
    """
    # TODO: Implement when Holiday model exists
    # For now, return empty set
    return set()


def check_employee_leave(employee_id: int, target_date: date) -> bool:
    """
    Check if employee has approved leave on this date.
    
    Returns True if leave exists.
    """
    # TODO: Implement when Leave model exists
    return False


# =============================================================================
# PROCESSOR SELECTION (Strategy Pattern)
# =============================================================================

_flexible_processor = FlexibleProcessor()
_structured_processor = StructuredProcessor()


def get_processor(is_flexible: bool):
    """
    Select the appropriate processor based on schedule type.
    
    Args:
        is_flexible: Whether the schedule is flexible
    
    Returns:
        AttendanceProcessor implementation
    """
    if is_flexible:
        return _flexible_processor
    return _structured_processor


# =============================================================================
# MAIN CALCULATION FUNCTION
# =============================================================================

def calculate_day_v2(employee_id: int, target_date: date) -> models.DailyAttendance:
    """
    Calculate attendance for an employee on a given date.
    
    Uses Strategy pattern to delegate to appropriate processor.
    
    Args:
        employee_id: Employee ID
        target_date: Date to calculate
    
    Returns:
        DailyAttendance model instance (saved)
    """
    # 1. Get or create attendance record
    daily, _ = models.DailyAttendance.objects.get_or_create(
        employee_id=employee_id,
        date=target_date
    )
    
    # 2. Reset values
    _reset_daily_attendance(daily)
    
    # 3. Resolve schedule
    ctx = resolve_schedule(employee_id, target_date)
    
    if not ctx.is_valid:
        daily.status = "Absent"
        daily.schedule_type = "NONE"
        daily.is_absent = True
        daily.save()
        return daily
    
    tt = ctx.timetable
    if not tt:
        daily.is_absent = True
        daily.save()
        return daily
    
    # 4. Get employee logs
    emp = models.Employee.objects.filter(id=employee_id).first()
    if not emp or not emp.user_id:
        daily.is_absent = True
        daily.save()
        return daily
    
    logs = get_logs(emp.user_id, ctx.search_start, ctx.search_end)
    
    # 5. Get external data
    holidays = get_holidays(target_date)
    has_leave = check_employee_leave(employee_id, target_date)
    
    # 6. Build processor context
    processor_context = ProcessorContext(
        employee_id=employee_id,
        target_date=target_date,
        timetable_id=tt.id,
        on_duty=ctx.on_duty_dt,
        off_duty=ctx.off_duty_dt,
        break_minutes=tt.break_minutes or 0,
        required_minutes=tt.required_minutes or 480,
        logs=logs,
        holidays=list(holidays),
        has_leave=has_leave,
        is_rest_day=False,
        rounding_rule=tt.rounding_rule,
        late_allow_minutes=tt.late_allow_minutes or 0,
        early_leave_allow_minutes=tt.early_leave_allow_minutes or 0,
    )
    
    # 7. Select processor (Strategy Pattern)
    processor = get_processor(tt.is_flexible)
    
    # 8. Calculate
    result = processor.process(processor_context)
    
    # 9. Map result to Django model
    _map_result_to_model(daily, result, ctx, tt)
    
    # 10. Save and return
    daily.save()
    return daily


def _reset_daily_attendance(daily: models.DailyAttendance) -> None:
    """Reset all calculated fields on a DailyAttendance record."""
    daily.status = "Absent"
    daily.worked_minutes = 0
    daily.late_minutes = 0
    daily.early_minutes = 0
    daily.overtime_minutes = 0
    daily.check_in = None
    daily.check_out = None
    daily.timetable_id = None
    daily.on_duty = None
    daily.off_duty = None
    daily.exception_reason = None
    daily.source_logs_count = 0
    daily.schedule_type = "NONE"
    daily.is_absent = True


def _map_result_to_model(
    daily: models.DailyAttendance,
    result,  # DailyCalculationResult
    ctx: DayContext,
    tt: models.Timetable,
) -> None:
    """Map DailyCalculationResult to DailyAttendance model."""
    # Identity
    daily.timetable_id = result.timetable_id
    daily.on_duty = tt.on_duty_time
    daily.off_duty = tt.off_duty_time
    
    # Schedule type
    if ctx.source == "OVERRIDE":
        daily.schedule_type = "OVERRIDE"
    elif ctx.source == "DEPARTMENT":
        daily.schedule_type = "DEPT"
    else:
        daily.schedule_type = result.calculation_mode
    
    # Timestamps
    daily.check_in = result.check_in
    daily.check_out = result.check_out
    
    # Time metrics
    daily.worked_minutes = result.worked_minutes
    daily.overtime_minutes = result.overtime_minutes
    daily.late_minutes = result.late_minutes or 0
    daily.early_minutes = result.early_out_minutes or 0
    
    # Status
    daily.status = result.status
    daily.is_absent = result.status == "Absent"
    
    # Audit
    daily.source_logs_count = result.source_punches_count


# =============================================================================
# BATCH CALCULATION
# =============================================================================

def calculate_period_v2(
    start_date: date,
    end_date: date,
    department_id: Optional[int] = None
) -> List[models.DailyAttendance]:
    """
    Calculate attendance for all employees in a period.
    
    Args:
        start_date: Start of period
        end_date: End of period (inclusive)
        department_id: Optional filter by department
    
    Returns:
        List of DailyAttendance records
    """
    employees = models.Employee.objects.filter(is_active=True)
    
    if department_id:
        employees = employees.filter(department_id=department_id)
    
    results = []
    current = start_date
    
    while current <= end_date:
        for emp in employees:
            daily = calculate_day_v2(emp.id, current)
            results.append(daily)
        current += timedelta(days=1)
    
    return results
