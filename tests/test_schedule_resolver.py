"""
Test suite for unified schedule resolver.

Verifies that schedule resolution works correctly for both V1 and V2 engines.
"""

import pytest
from datetime import date, time, datetime, timedelta
from django.test import TestCase
from django.db.models import Q

from core import models
from core.services.schedule_resolver import (
    resolve_schedule_unified,
    ScheduleSource,
    ScheduleResolutionError,
)


class TestScheduleResolverUnified(TestCase):
    """Test unified schedule resolver."""
    
    def setUp(self):
        """Create test data."""
        # Create company
        self.company = models.Company.objects.create(name="Test Corp")
        
        # Create department
        self.dept = models.Department.objects.create(
            name="Engineering",
            company=self.company,
        )
        
        # Create timetables
        self.timetable_9to5 = models.Timetable.objects.create(
            name="Standard 9-5",
            on_duty_time=time(9, 0),
            off_duty_time=time(17, 0),
            is_flexible=False,
            break_minutes=60,
        )
        
        self.timetable_evening = models.Timetable.objects.create(
            name="Evening Shift",
            on_duty_time=time(18, 0),
            off_duty_time=time(22, 0),
            is_flexible=False,
        )
        
        # Create shift
        self.shift_day = models.Shift.objects.create(name="Day Shift")
        models.ShiftTimetable.objects.create(
            shift=self.shift_day,
            timetable=self.timetable_9to5,
            day_index=0,  # Monday
        )
        
        # Create employee
        self.employee = models.Employee.objects.create(
            user_id="EMP001",
            name="John Doe",
            department=self.dept,
        )
        
        # Test date (Monday)
        self.target_date = date(2026, 2, 9)
    
    def test_resolve_with_employee_shift(self):
        """Test resolution with employee-level shift assignment."""
        models.EmployeeShift.objects.create(
            scope='EMPLOYEE',
            employee=self.employee,
            shift=self.shift_day,
            start_date=self.target_date,
        )
        
        resolved = resolve_schedule_unified(
            self.employee.id,
            self.target_date,
        )
        
        assert resolved.is_valid
        assert resolved.timetable.id == self.timetable_9to5.id
        assert resolved.source == ScheduleSource.EMPLOYEE_SHIFT
        assert resolved.error is None
        assert resolved.on_duty_dt is not None
        assert resolved.off_duty_dt is not None
    
    def test_resolve_with_department_shift(self):
        """Test resolution with department-level shift assignment (fallback)."""
        # Create department shift WITHOUT employee shift
        models.EmployeeShift.objects.create(
            scope='DEPARTMENT',
            department=self.dept,
            shift=self.shift_day,
            start_date=self.target_date,
        )
        
        resolved = resolve_schedule_unified(
            self.employee.id,
            self.target_date,
        )
        
        assert resolved.is_valid
        assert resolved.timetable.id == self.timetable_9to5.id
        assert resolved.source == ScheduleSource.DEPARTMENT_SHIFT
        assert resolved.error is None
    
    def test_resolve_with_override(self):
        """Test that ScheduleOverride has highest priority."""
        # Create both policies
        models.EmployeeShift.objects.create(
            scope='EMPLOYEE',
            employee=self.employee,
            shift=self.shift_day,
            start_date=self.target_date,
        )
        
        # Override has highest priority
        models.ScheduleOverride.objects.create(
            employee=self.employee,
            date=self.target_date,
            timetable=self.timetable_evening,
        )
        
        resolved = resolve_schedule_unified(
            self.employee.id,
            self.target_date,
        )
        
        # Should use override timetable, not employee shift
        assert resolved.is_valid
        assert resolved.timetable.id == self.timetable_evening.id
        assert resolved.source == ScheduleSource.OVERRIDE
    
    def test_resolve_no_assignment(self):
        """Test resolution when employee has no shift assignment."""
        # No assignment created
        
        resolved = resolve_schedule_unified(
            self.employee.id,
            self.target_date,
        )
        
        assert not resolved.is_valid
        assert resolved.timetable is None
        assert resolved.source == ScheduleSource.IMPLICIT_REST
        assert resolved.error == ScheduleResolutionError.NO_SHIFT_ASSIGNED
    
    def test_resolve_shift_no_timetables(self):
        """Test resolution when shift has no ShiftTimetables configured."""
        empty_shift = models.Shift.objects.create(name="Empty Shift")
        
        models.EmployeeShift.objects.create(
            scope='EMPLOYEE',
            employee=self.employee,
            shift=empty_shift,
            start_date=self.target_date,
        )
        
        resolved = resolve_schedule_unified(
            self.employee.id,
            self.target_date,
        )
        
        assert not resolved.is_valid
        assert resolved.timetable is None
        assert resolved.source == ScheduleSource.EMPLOYEE_SHIFT  # Shift was assigned but has no timetables
        assert resolved.error == ScheduleResolutionError.SHIFT_NO_TIMETABLES
    
    def test_resolve_shift_timetable_missing_day(self):
        """Test resolution when shift has no timetable for this day of week."""
        # Shift only has Monday (day_index=0)
        # Try to resolve for Tuesday (day_index=1)
        tuesday = self.target_date + timedelta(days=1)
        
        models.EmployeeShift.objects.create(
            scope='EMPLOYEE',
            employee=self.employee,
            shift=self.shift_day,
            start_date=self.target_date,
        )
        
        resolved = resolve_schedule_unified(
            self.employee.id,
            tuesday,  # Tuesday - no timetable configured
        )
        
        assert not resolved.is_valid
        assert resolved.timetable is None
        assert resolved.source == ScheduleSource.EMPLOYEE_SHIFT  # Shift was assigned but missing day
        assert resolved.error == ScheduleResolutionError.SHIFT_TIMETABLE_MISSING_DAY
    
    def test_resolve_overnight_shift(self):
        """Test resolution handles overnight shifts correctly."""
        # Create overnight timetable (22:00 to 06:00)
        timetable_night = models.Timetable.objects.create(
            name="Night Shift",
            on_duty_time=time(22, 0),
            off_duty_time=time(6, 0),  # off < on, so overnight
            is_flexible=False,
        )
        
        shift_night = models.Shift.objects.create(name="Night Shift")
        models.ShiftTimetable.objects.create(
            shift=shift_night,
            timetable=timetable_night,
            day_index=0,
        )
        
        models.EmployeeShift.objects.create(
            scope='EMPLOYEE',
            employee=self.employee,
            shift=shift_night,
            start_date=self.target_date,
        )
        
        resolved = resolve_schedule_unified(
            self.employee.id,
            self.target_date,
        )
        
        assert resolved.is_valid
        assert resolved.on_duty_dt.hour == 22  # 22:00
        assert resolved.off_duty_dt.hour == 6   # 06:00
        # off_duty should be NEXT day
        assert resolved.off_duty_dt.date() == self.target_date + timedelta(days=1)


class TestScheduleResolverConsistency(TestCase):
    """Test that resolver produces consistent results."""
    
    def setUp(self):
        """Create test data."""
        self.company = models.Company.objects.create(name="Test Corp")
        self.dept = models.Department.objects.create(
            name="Engineering",
            company=self.company,
        )
        self.timetable = models.Timetable.objects.create(
            name="Standard 9-5",
            on_duty_time=time(9, 0),
            off_duty_time=time(17, 0),
            is_flexible=False,
        )
        self.shift = models.Shift.objects.create(name="Day Shift")
        models.ShiftTimetable.objects.create(
            shift=self.shift,
            timetable=self.timetable,
            day_index=0,
        )
        self.employee = models.Employee.objects.create(
            user_id="EMP001",
            name="John Doe",
            department=self.dept,
        )
        self.target_date = date(2026, 2, 9)
    
    def test_resolution_idempotent(self):
        """Test that calling resolver multiple times gives same result."""
        models.EmployeeShift.objects.create(
            scope='EMPLOYEE',
            employee=self.employee,
            shift=self.shift,
            start_date=self.target_date,
        )
        
        result1 = resolve_schedule_unified(self.employee.id, self.target_date)
        result2 = resolve_schedule_unified(self.employee.id, self.target_date)
        
        assert result1.is_valid == result2.is_valid
        assert result1.timetable.id == result2.timetable.id
        assert result1.source == result2.source
        assert result1.on_duty_dt == result2.on_duty_dt
        assert result1.off_duty_dt == result2.off_duty_dt
    
    def test_resolution_handles_date_ranges(self):
        """Test that resolver handles date ranges correctly."""
        # Create shift for specific date range
        models.EmployeeShift.objects.create(
            scope='EMPLOYEE',
            employee=self.employee,
            shift=self.shift,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 2, 15),
        )
        
        # Within range - should resolve
        within = resolve_schedule_unified(self.employee.id, date(2026, 2, 9))
        assert within.is_valid
        
        # Before range - should not resolve
        before = resolve_schedule_unified(self.employee.id, date(2026, 1, 31))
        assert not before.is_valid
        
        # After range - should not resolve
        after = resolve_schedule_unified(self.employee.id, date(2026, 2, 16))
        assert not after.is_valid
