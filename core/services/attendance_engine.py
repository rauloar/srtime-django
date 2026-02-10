"""
Attendance Calculation Engine - Adaptado para Django ORM
Motor de cálculo de asistencia con soporte para horarios fijos y flexibles

Uses unified schedule resolution via schedule_resolver.py
to ensure consistency between V1 and V2 engines.
"""
from datetime import date, datetime, timedelta, time
from typing import List, Optional
import logging
from django.db.models import Q
from django.utils import timezone
from core import models
from .day_context import DayContext
from .obligation import ObligationResolver
from .schedule_resolver import resolve_schedule_unified

logger = logging.getLogger(__name__)


def round_time(dt: datetime, rule: str, is_check_in: bool) -> datetime:
    """
    Apply rounding rules.
    """
    if not rule or rule == "none":
        return dt
    
    minute_step = 0
    if rule == "5min": minute_step = 5
    elif rule == "10min": minute_step = 10
    elif rule == "15min": minute_step = 15
    elif rule == "30min": minute_step = 30
    else: return dt 
    
    new_minute = int(round(dt.minute / minute_step) * minute_step)
    delta = new_minute - dt.minute
    return dt + timedelta(minutes=delta)


def _build_context(tt: models.Timetable, target_date: date, source: str) -> DayContext:
    try:
        # Flexible
        def parse_time_field(field_value, default_value=None):
            if field_value is None:
                return default_value
            if isinstance(field_value, time):
                return field_value
            if isinstance(field_value, str):
                field_value = field_value.strip()
                if not field_value:
                    return default_value
                for fmt in ("%H:%M:%S", "%H:%M"):
                    try:
                        return datetime.strptime(field_value, fmt).time()
                    except ValueError:
                        continue
                return default_value
            return default_value

        if tt.is_flexible:
            t_in_start = parse_time_field(tt.check_in_start, time(0, 0))
            t_out_end = parse_time_field(tt.check_out_end, time(23, 59))
            
            dt_search_start = timezone.make_aware(datetime.combine(target_date, t_in_start))
            dt_search_end = timezone.make_aware(datetime.combine(target_date, t_out_end))
            
            if dt_search_end < dt_search_start:
                 dt_search_end += timedelta(days=1)
            
            # Passive Obligation Resolution
            obl_res = ObligationResolver.resolve(tt, source)

            return DayContext(
                is_valid=True,
                obligation=True,
                timetable=tt,
                on_duty_dt=dt_search_start, # Flex uses range as duty reference
                off_duty_dt=dt_search_end,
                search_start=dt_search_start,
                search_end=dt_search_end,
                is_cross_day=False,
                source=source,
                resolved_obligation=obl_res
            )

        # Standard Fixed
        t_on = parse_time_field(tt.on_duty_time)
        t_off = parse_time_field(tt.off_duty_time)
        t_in_start = parse_time_field(tt.check_in_start, time.min)
        t_out_end = parse_time_field(tt.check_out_end, time.max)

        if not t_on or not t_off:
            return DayContext.empty()
        
        dt_on = timezone.make_aware(datetime.combine(target_date, t_on))
        dt_off = timezone.make_aware(datetime.combine(target_date, t_off))
        
        is_cross_day = False
        if dt_off < dt_on:
            is_cross_day = True
            dt_off += timedelta(days=1)
            
        dt_search_start = timezone.make_aware(datetime.combine(target_date, t_in_start))
        
        end_date = target_date if not is_cross_day else dt_off.date()
        dt_search_end = timezone.make_aware(datetime.combine(end_date, t_out_end))
        
        if dt_search_end < dt_search_start:
            dt_search_end += timedelta(days=1)

        # Passive Obligation Resolution
        obl_res = ObligationResolver.resolve(tt, source)

        return DayContext(
            is_valid=True,
            obligation=True,
            timetable=tt,
            on_duty_dt=dt_on,
            off_duty_dt=dt_off,
            search_start=dt_search_start,
            search_end=dt_search_end,
            is_cross_day=is_cross_day,
            source=source,
            resolved_obligation=obl_res
        )
            
    except Exception as e:
        return DayContext.empty()


def resolve_schedule(employee_id: int, target_date: date) -> DayContext:
    """
    Resolve schedule for an employee on a given date.
    
    This function delegates to the unified schedule resolver (schedule_resolver.py)
    to ensure consistency with V2 engine.
    
    Priority:
    1. ScheduleOverride (highest)
    2. EmployeeShift (EMPLOYEE scope)
    3. EmployeeShift (DEPARTMENT scope)
    4. Implicit rest day
    
    Returns:
        DayContext with resolved schedule or empty context if not found
    """
    # Use unified resolver
    resolved = resolve_schedule_unified(employee_id, target_date)
    
    if not resolved.is_valid:
        # Schedule resolution failed - return empty context with reason
        empty = DayContext.empty()
        return empty._replace(source=resolved.error.value)
    
    # Build DayContext from resolved schedule
    return _build_context(
        resolved.timetable,
        target_date,
        resolved.source.value
    )


def get_logs(user_id: str, start: datetime, end: datetime) -> List[models.AttendanceLog]:
    return list(models.AttendanceLog.objects.filter(
        user_id=user_id,
        timestamp__gte=start,
        timestamp__lte=end
    ).order_by('timestamp'))


def calculate_day(employee_id: int, target_date: date) -> models.DailyAttendance:
    """
    Calcula la asistencia diaria para un empleado en una fecha específica.
    Soporta horarios fijos y flexibles.
    """
    # 0. Prep Result (Get or Create)
    daily, created = models.DailyAttendance.objects.get_or_create(
        employee_id=employee_id,
        date=target_date
    )
    
    # Reset values
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
    # Audit
    daily.source_logs_count = 0 
    daily.schedule_type = "NONE"

    DAILY_TYPE_MAP = {
        "FIXED": "FIXED",
        "FLEX": "FLEX"
    }
    
    # 1. Resolve Schedule
    ctx = resolve_schedule(employee_id, target_date)
    
    if not ctx.is_valid:
        # Schedule resolution failed - capture reason
        daily.status = "Absent"
        daily.schedule_type = "NONE"
        daily.is_absent = True
        
        # Track reason for absence in exception_reason
        reason_map = {
            "IMPLICIT_REST": "No schedule configured for this date",
            "SHIFT_NO_TIMETABLES": "Shift assigned but has no timetable hours configured",
            "SHIFT_TIMETABLE_MISSING_DAY": "Shift has no timetable for this day of week"
        }
        daily.exception_reason = reason_map.get(ctx.source, f"Schedule error: {ctx.source}")
        daily.save()
        return daily

    tt = ctx.timetable
    # Safe guard if timetable is None but valid (should not happen with current constructor)
    if not tt: 
        daily.is_absent = True
        daily.exception_reason = "File processing error: timetable lost during resolution"
        daily.save()
        return daily

    daily.timetable_id = tt.id
    if tt.is_flexible:
        daily.on_duty = None  # Aligned with ZKTime.Net flexible schedule model
        daily.off_duty = None  # Aligned with ZKTime.Net flexible schedule model
    else:
        daily.on_duty = tt.on_duty_time
        daily.off_duty = tt.off_duty_time
    
    # Audit: Set schedule_type based on Source + Flexible
    # e.g. OVERRIDE, DEPARTMENT, SHIFT-FLEX, SHIFT-FIXED
    base_type = "FLEX" if tt.is_flexible else "FIXED"
    
    if ctx.source == "OVERRIDE":
        daily.schedule_type = "OVERRIDE"
    elif ctx.source == "DEPARTMENT":
        daily.schedule_type = "DEPT"
    else:
        daily.schedule_type = base_type

    # 2. Get Raw Data
    emp = models.Employee.objects.filter(id=employee_id).first()
    if not emp or not emp.user_id:
        daily.is_absent = True
        daily.save()
        return daily

    logs = get_logs(emp.user_id, ctx.search_start, ctx.search_end)
    daily.source_logs_count = len(logs)
    
    if not logs:
        if tt.is_flexible:
            daily.status = "Incomplete"  # Aligned with ZKTime.Net flexible schedule model
            daily.is_absent = False  # Aligned with ZKTime.Net flexible schedule model
        else:
            daily.is_absent = True
        daily.save()
        return daily

    daily.is_absent = False

    # 3. Apply Rules
    if tt.is_flexible:
        daily.status = "Incomplete"  # Aligned with ZKTime.Net flexible schedule model
        total_worked = 0
        current_in = None
        
        for log in logs:
            state = int(log.punch) if log.punch is not None else 0
            is_in = state in [0, 4, 8]
            is_out = state in [1, 5, 9]
            
            if is_in:
                if current_in is None: 
                    current_in = log.timestamp
                    if not daily.check_in: daily.check_in = current_in
            elif is_out:
                if current_in:
                    duration = (log.timestamp - current_in).total_seconds() / 60
                    total_worked += duration
                    daily.check_out = log.timestamp 
                    current_in = None
        
        daily.worked_minutes = int(total_worked)  # Aligned with ZKTime.Net flexible schedule model
        daily.overtime_minutes = 0  # Aligned with ZKTime.Net flexible schedule model
        if daily.worked_minutes > 0:
            daily.status = "Worked"  # Aligned with ZKTime.Net flexible schedule model
        
    else:
        # Fixed schedule logic
        daily.status = "Normal"
        
        # Find Check-in
        for log in logs:
            state = int(log.punch) if log.punch is not None else 0
            if state in [0, 4, 8]:  # Check-in states
                daily.check_in = log.timestamp
                break
        
        # Find Check-out
        for log in reversed(logs):
            state = int(log.punch) if log.punch is not None else 0
            if state in [1, 5, 9]:  # Check-out states
                daily.check_out = log.timestamp
                break
        
        # Apply rounding if configured
        if daily.check_in and tt.rounding_rule and tt.rounding_rule != "none":
            daily.check_in = round_time(daily.check_in, tt.rounding_rule, True)
        
        if daily.check_out and tt.rounding_rule and tt.rounding_rule != "none":
            daily.check_out = round_time(daily.check_out, tt.rounding_rule, False)
        
        # Calculate Late
        if daily.check_in and ctx.on_duty_dt:
            if daily.check_in > ctx.on_duty_dt:
                late_delta = (daily.check_in - ctx.on_duty_dt).total_seconds() / 60
                daily.late_minutes = int(late_delta)
                
                # Apply tolerance - subtract allowance from late minutes
                if tt.late_allow_minutes:
                    daily.late_minutes = max(0, daily.late_minutes - tt.late_allow_minutes)
                
                if daily.late_minutes > 0:
                    daily.status = "Late"
        
        # Calculate Early Leave
        if daily.check_out and ctx.off_duty_dt:
            if daily.check_out < ctx.off_duty_dt:
                early_delta = (ctx.off_duty_dt - daily.check_out).total_seconds() / 60
                daily.early_minutes = int(early_delta)
                
                # Apply tolerance - subtract allowance from early minutes
                if tt.early_leave_allow_minutes:
                    daily.early_minutes = max(0, daily.early_minutes - tt.early_leave_allow_minutes)
                
                if daily.early_minutes > 0:
                    if daily.status == "Late":
                        daily.status = "Late, Early Leave"
                    else:
                        daily.status = "Early Leave"
        
        # Calculate Worked Time
        if daily.check_in and daily.check_out:
            worked_delta = (daily.check_out - daily.check_in).total_seconds() / 60
            
            # Subtract break
            if tt.break_minutes:
                worked_delta = max(0, worked_delta - tt.break_minutes)
            
            daily.worked_minutes = int(worked_delta)
        
        # Calculate Overtime
        if daily.check_out and ctx.off_duty_dt:
            if daily.check_out > ctx.off_duty_dt:
                overtime_delta = (daily.check_out - ctx.off_duty_dt).total_seconds() / 60
                daily.overtime_minutes = int(overtime_delta)
                
                # Apply overtime threshold - only count if >= threshold
                if tt.overtime_threshold_minutes and daily.overtime_minutes < tt.overtime_threshold_minutes:
                    daily.overtime_minutes = 0
                
                if daily.overtime_minutes > 0:
                    if "Normal" in daily.status:
                        daily.status = "Normal, Overtime"
            
    daily.save()
    
    # Run shadow mode validation (if enabled)
    try:
        from .shadow_mode_service import ShadowModeService
        shadow = ShadowModeService()
        shadow.validate_daily_calculation(employee_id, target_date, daily)
    except Exception as e:
        # Shadow mode errors never affect production
        logger.warning(f"Shadow mode validation error: {e}", exc_info=False)
    
    return daily


def calculate_period(start_date: date, end_date: date, department_id: Optional[int] = None):
    """
    Calcula asistencia para todos los empleados en un periodo.
    
    Sistema inteligente:
    - Procesa solo empleados con EmployeeShift válido
    - Reporta empleados saltados sin detenerse
    - Continúa con siguientes registros si falla uno
    
    Returns:
        tuple: (results, skipped_employees_report)
    """
    employees = models.Employee.objects.filter(active=True)
    
    if department_id:
        employees = employees.filter(department_id=department_id)
    
    employees = list(employees)
    results = []
    skipped_employees = []
    
    # Filtrar empleados que SÍ tienen EmployeeShift asignado
    employee_shifts = models.EmployeeShift.objects.filter(
        employee_id__in=[e.id for e in employees]
    ).values_list('employee_id', flat=True).distinct()
    
    valid_employees = [e for e in employees if e.id in employee_shifts]
    skipped_no_shift = [e for e in employees if e.id not in employee_shifts]
    
    # Registrar empleados sin shift
    for emp in skipped_no_shift:
        skipped_employees.append({
            'employee_id': emp.id,
            'user_id': emp.user_id,
            'name': emp.name,
            'reason': 'NO_SHIFT_ASSIGNED'
        })
    
    # Procesar solo empleados válidos
    for emp in valid_employees:
        current_date = start_date
        while current_date <= end_date:
            try:
                daily = calculate_day(emp.id, current_date)
                results.append(daily)
            except Exception as e:
                # Continuar procesando otros días/empleados si hay error
                skipped_employees.append({
                    'employee_id': emp.id,
                    'user_id': emp.user_id,
                    'name': emp.name,
                    'date': str(current_date),
                    'reason': f'CALC_ERROR: {str(e)[:50]}'
                })
            current_date += timedelta(days=1)
    
    # Almacenar reporte en sesión/contexto si es necesario
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f'Attendance Calculation: {len(results)} processed, {len(skipped_employees)} skipped')
    for skip in skipped_employees:
        logger.warning(f'Skipped {skip}')
    
    return results, skipped_employees
