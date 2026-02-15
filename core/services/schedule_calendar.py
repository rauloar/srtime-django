"""
Schedule Calendar Service

Generates monthly schedule calendars for employees.
Uses schedule_resolver as single source of truth.

IMPORTANT: This service includes an OPTIMIZED resolver for range queries
that avoids N+1 problems by resolving schedules in-memory.
"""
from datetime import date, timedelta
from typing import List, Optional, Dict
from django.db.models import Prefetch, Q

from core import models


def resolve_schedule_range(
    employee: models.Employee,
    start_date: date,
    end_date: date,
    prefetched_shifts: List[models.EmployeeShift],
    prefetched_overrides: List[models.ScheduleOverride],
    dept_shifts: Dict[int, List[models.EmployeeShift]]
) -> List[Dict]:
    """
    Optimized schedule resolver for date ranges.
    
    Resolves schedule for all days in range IN MEMORY without DB queries.
    Uses prefetched data to maintain same priority logic as resolve_schedule_unified.
    
    Priority:
        1. ScheduleOverride (highest)
        2. EmployeeShift (scope=EMPLOYEE)
        3. EmployeeShift (scope=DEPARTMENT)
        4. Implicit rest day
    
    Args:
        employee: Employee instance (with prefetched relations)
        start_date: Start date
        end_date: End date
        prefetched_shifts: Employee's shift assignments (already loaded)
        prefetched_overrides: Employee's schedule overrides (already loaded)
        dept_shifts: Department-level shifts by department ID
    
    Returns:
        List of schedule days:
        [
            {
                "date": "2026-02-01",
                "timetable": "08:00-16:00",
                "on_duty": "08:00",
                "off_duty": "16:00",
                "source": "EMPLOYEE_SHIFT",
                "is_rest": false
            }
        ]
    """
    # Build lookup maps for O(1) access
    override_map = {ovr.date: ovr for ovr in prefetched_overrides}
    
    # Filter employee shifts valid in range
    employee_shifts = [
        s for s in prefetched_shifts
        if s.start_date <= end_date and (s.end_date is None or s.end_date >= start_date)
    ]
    
    # Get department shifts if employee has department
    department_shifts = []
    if employee.department_id and employee.department_id in dept_shifts:
        department_shifts = [
            s for s in dept_shifts[employee.department_id]
            if s.start_date <= end_date and (s.end_date is None or s.end_date >= start_date)
        ]
    
    # Generate schedule for each day
    days = (end_date - start_date).days + 1
    schedule = []
    
    for i in range(days):
        day = start_date + timedelta(days=i)
        
        # Priority 1: Check for override
        if day in override_map:
            override = override_map[day]
            if override.timetable:
                schedule.append({
                    "date": day.isoformat(),
                    "timetable": override.timetable.name,
                    "on_duty": override.timetable.on_duty_time.strftime("%H:%M") if override.timetable.on_duty_time else None,
                    "off_duty": override.timetable.off_duty_time.strftime("%H:%M") if override.timetable.off_duty_time else None,
                    "source": "OVERRIDE",
                    "is_rest": False
                })
                continue
        
        # Priority 2: Check employee-level shift
        emp_shift = _find_active_shift(employee_shifts, day)
        if emp_shift:
            timetable = _resolve_shift_timetable_for_date(emp_shift, day)
            if timetable:
                schedule.append({
                    "date": day.isoformat(),
                    "timetable": timetable.name,
                    "on_duty": timetable.on_duty_time.strftime("%H:%M") if timetable.on_duty_time else None,
                    "off_duty": timetable.off_duty_time.strftime("%H:%M") if timetable.off_duty_time else None,
                    "source": "EMPLOYEE_SHIFT",
                    "is_rest": False
                })
                continue
        
        # Priority 3: Check department-level shift
        dept_shift = _find_active_shift(department_shifts, day)
        if dept_shift:
            timetable = _resolve_shift_timetable_for_date(dept_shift, day)
            if timetable:
                schedule.append({
                    "date": day.isoformat(),
                    "timetable": timetable.name,
                    "on_duty": timetable.on_duty_time.strftime("%H:%M") if timetable.on_duty_time else None,
                    "off_duty": timetable.off_duty_time.strftime("%H:%M") if timetable.off_duty_time else None,
                    "source": "DEPARTMENT_SHIFT",
                    "is_rest": False
                })
                continue
        
        # Priority 4: Implicit rest day
        schedule.append({
            "date": day.isoformat(),
            "timetable": None,
            "on_duty": None,
            "off_duty": None,
            "source": "IMPLICIT_REST",
            "is_rest": True
        })
    
    return schedule


def _find_active_shift(shifts: List[models.EmployeeShift], target_date: date) -> Optional[models.EmployeeShift]:
    """
    Find the active shift for a specific date.
    Returns the most recent shift that covers the date.
    """
    active_shifts = [
        s for s in shifts
        if s.start_date <= target_date and (s.end_date is None or s.end_date >= target_date)
    ]
    
    if not active_shifts:
        return None
    
    # Return most recent (highest start_date, then highest ID)
    return max(active_shifts, key=lambda s: (s.start_date, s.id))


def _resolve_shift_timetable_for_date(
    emp_shift: models.EmployeeShift,
    target_date: date
) -> Optional[models.Timetable]:
    """
    Resolve timetable for a specific date from a shift.
    Handles both weekly cycles and long cycles.
    """
    shift = emp_shift.shift
    
    if not shift or not shift.cycle_days:
        return None
    
    # Calculate day index using custom_start or start_date
    cycle_start = emp_shift.custom_start or emp_shift.start_date
    days_since_start = (target_date - cycle_start).days
    day_index = days_since_start % shift.cycle_days
    
    # Find timetable for this day_index
    # shift.timetables is prefetched ShiftTimetable queryset
    for shift_tt in shift.timetables.all():
        if shift_tt.day_index == day_index and shift_tt.timetable:
            return shift_tt.timetable
    
    return None


def get_schedule_calendar(
    start_date: date,
    end_date: date,
    employee_ids: Optional[List[int]] = None
) -> Dict:
    """
    Generate schedule calendar for employees over a date range.
    
    OPTIMIZED VERSION: Uses resolve_schedule_range() to avoid N+1 queries.
    
    Args:
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
        employee_ids: Optional filter by employee IDs
    
    Returns:
        {
            "employees": [
                {
                    "id": 1,
                    "name": "Juan",
                    "department_id": 5,
                    "schedule": [...]
                }
            ]
        }
    
    Raises:
        ValueError: If date range exceeds 31 days
    """
    # Validate range
    if (end_date - start_date).days > 31:
        raise ValueError("Max range: 31 days")
    
    # Build employee queryset
    employees_qs = models.Employee.objects.filter(active=True)
    if employee_ids:
        employees_qs = employees_qs.filter(id__in=employee_ids)
    
    # CRITICAL: Prefetch to avoid N+1 queries
    employees_qs = employees_qs.select_related('department').prefetch_related(
        # Prefetch employee-level shift assignments valid in range
        Prefetch(
            'shift_assignments',
            queryset=models.EmployeeShift.objects.filter(
                scope='EMPLOYEE',
                start_date__lte=end_date
            ).filter(
                Q(end_date__gte=start_date) | Q(end_date__isnull=True)
            ).select_related('shift').prefetch_related(
                Prefetch(
                    'shift__timetables',
                    queryset=models.ShiftTimetable.objects.select_related('timetable')
                )
            )
        ),
        # Prefetch schedule overrides in range
        Prefetch(
            'schedule_overrides',
            queryset=models.ScheduleOverride.objects.filter(
                date__gte=start_date,
                date__lte=end_date
            ).select_related('timetable')
        )
    )
    
    # Also prefetch department-level shifts
    dept_ids = list(
        employees_qs.exclude(department__isnull=True)
        .values_list('department_id', flat=True)
        .distinct()
    )
    
    dept_shifts = {}
    if dept_ids:
        dept_shift_qs = models.EmployeeShift.objects.filter(
            scope='DEPARTMENT',
            department_id__in=dept_ids,
            start_date__lte=end_date
        ).filter(
            Q(end_date__gte=start_date) | Q(end_date__isnull=True)
        ).select_related('shift', 'department').prefetch_related(
            Prefetch(
                'shift__timetables',
                queryset=models.ShiftTimetable.objects.select_related('timetable')
            )
        )
        
        for dept_shift in dept_shift_qs:
            if dept_shift.department_id not in dept_shifts:
                dept_shifts[dept_shift.department_id] = []
            dept_shifts[dept_shift.department_id].append(dept_shift)
    
    # Build result using optimized resolver
    result = []
    for emp in employees_qs:
        # Use optimized resolver that works in-memory
        schedule = resolve_schedule_range(
            employee=emp,
            start_date=start_date,
            end_date=end_date,
            prefetched_shifts=list(emp.shift_assignments.all()),
            prefetched_overrides=list(emp.schedule_overrides.all()),
            dept_shifts=dept_shifts
        )
        
        result.append({
            "id": emp.id,
            "user_id": emp.user_id,
            "name": emp.name,
            "department_id": emp.department_id,
            "schedule": schedule
        })
    
    return {"employees": result}

