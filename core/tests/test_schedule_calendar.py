"""
Tests for Schedule Calendar Service

Tests básicos para validar:
- Resolución correcta de horarios
- Prioridad de ScheduleOverride
- Manejo de rangos de fechas
- Prevención de N+1 queries
"""
from django.test import TestCase
from django.db import connection
from django.test.utils import override_settings
from datetime import date, timedelta
from core.services.schedule_calendar import get_schedule_calendar
from core.models import (
    Employee, Shift, ShiftTimetable, Timetable, 
    EmployeeShift, ScheduleOverride, Department
)


class ScheduleCalendarTestCase(TestCase):
    """Test suite for schedule calendar service"""
    
    def setUp(self):
        """Set up test data"""
        # Create department
        self.dept = Department.objects.create(name="Test Department")
        
        # Create timetables
        self.tt_morning = Timetable.objects.create(
            name="08:00-16:00",
            on_duty_time="08:00:00",
            off_duty_time="16:00:00"
        )
        
        self.tt_afternoon = Timetable.objects.create(
            name="14:00-22:00",
            on_duty_time="14:00:00",
            off_duty_time="22:00:00"
        )
        
        # Create shifts
        self.shift_morning = Shift.objects.create(
            name="Morning Shift",
            cycle_days=7
        )
        ShiftTimetable.objects.create(
            shift=self.shift_morning,
            timetable=self.tt_morning,
            day_index=0
        )
        
        self.shift_afternoon = Shift.objects.create(
            name="Afternoon Shift",
            cycle_days=7
        )
        ShiftTimetable.objects.create(
            shift=self.shift_afternoon,
            timetable=self.tt_afternoon,
            day_index=0
        )
        
        # Create employees
        self.emp1 = Employee.objects.create(
            user_id="EMP001",
            name="Employee 1",
            department=self.dept,
            is_active=True
        )
        
        self.emp2 = Employee.objects.create(
            user_id="EMP002",
            name="Employee 2",
            department=self.dept,
            is_active=True
        )
        
        self.emp3 = Employee.objects.create(
            user_id="EMP003",
            name="Employee 3 (No Shift)",
            department=None,
            is_active=True
        )
    
    def test_basic_employee_shift(self):
        """Test 1: Employee con EmployeeShift activo"""
        # Assign shift to employee
        EmployeeShift.objects.create(
            employee=self.emp1,
            shift=self.shift_morning,
            scope='EMPLOYEE',
            start_date=date(2026, 2, 1)
        )
        
        # Get schedule
        result = get_schedule_calendar(
            start_date=date(2026, 2, 1),
            end_date=date(2026, 2, 3)
        )
        
        # Verify
        self.assertEqual(len(result['employees']), 3)
        emp1_schedule = next(e for e in result['employees'] if e['id'] == self.emp1.id)
        self.assertEqual(len(emp1_schedule['schedule']), 3)
        
        # First day should have morning timetable
        day1 = emp1_schedule['schedule'][0]
        self.assertEqual(day1['date'], '2026-02-01')
        self.assertEqual(day1['timetable'], '08:00-16:00')
        self.assertEqual(day1['source'], 'EMPLOYEE_SHIFT')
        self.assertFalse(day1['is_rest'])
    
    def test_override_priority(self):
        """Test 2: ScheduleOverride tiene prioridad sobre EmployeeShift"""
        # Assign shift to employee
        EmployeeShift.objects.create(
            employee=self.emp1,
            shift=self.shift_morning,
            scope='EMPLOYEE',
            start_date=date(2026, 2, 1)
        )
        
        # Create override for specific day
        ScheduleOverride.objects.create(
            employee=self.emp1,
            timetable=self.tt_afternoon,
            date=date(2026, 2, 2)
        )
        
        # Get schedule
        result = get_schedule_calendar(
            start_date=date(2026, 2, 1),
            end_date=date(2026, 2, 3)
        )
        
        emp1_schedule = next(e for e in result['employees'] if e['id'] == self.emp1.id)
        
        # Day 1: regular shift
        day1 = emp1_schedule['schedule'][0]
        self.assertEqual(day1['timetable'], '08:00-16:00')
        self.assertEqual(day1['source'], 'EMPLOYEE_SHIFT')
        
        # Day 2: override should take priority
        day2 = emp1_schedule['schedule'][1]
        self.assertEqual(day2['timetable'], '14:00-22:00')
        self.assertEqual(day2['source'], 'OVERRIDE')
        
        # Day 3: back to regular shift
        day3 = emp1_schedule['schedule'][2]
        self.assertEqual(day3['timetable'], '08:00-16:00')
        self.assertEqual(day3['source'], 'EMPLOYEE_SHIFT')
    
    def test_department_shift_inheritance(self):
        """Test 3: Empleado hereda turno del departamento"""
        # Assign shift to department (not employee)
        EmployeeShift.objects.create(
            department=self.dept,
            shift=self.shift_morning,
            scope='DEPARTMENT',
            start_date=date(2026, 2, 1)
        )
        
        # Get schedule
        result = get_schedule_calendar(
            start_date=date(2026, 2, 1),
            end_date=date(2026, 2, 2)
        )
        
        # emp1 and emp2 should inherit department shift
        emp1_schedule = next(e for e in result['employees'] if e['id'] == self.emp1.id)
        day1 = emp1_schedule['schedule'][0]
        
        self.assertEqual(day1['timetable'], '08:00-16:00')
        self.assertEqual(day1['source'], 'DEPARTMENT_SHIFT')
    
    def test_employee_without_shift(self):
        """Test 4: Empleado sin turno debe devolver REST"""
        # emp3 has no department and no shift
        result = get_schedule_calendar(
            start_date=date(2026, 2, 1),
            end_date=date(2026, 2, 2)
        )
        
        emp3_schedule = next(e for e in result['employees'] if e['id'] == self.emp3.id)
        day1 = emp3_schedule['schedule'][0]
        
        self.assertIsNone(day1['timetable'])
        self.assertTrue(day1['is_rest'])
    
    def test_max_range_validation(self):
        """Test 5: Rango mayor a 31 días debe devolver ValueError"""
        with self.assertRaises(ValueError) as context:
            get_schedule_calendar(
                start_date=date(2026, 2, 1),
                end_date=date(2026, 3, 15)  # 42 days
            )
        
        self.assertIn("Max 31 days", str(context.exception))
    
    def test_no_n_plus_one_queries(self):
        """Test 6: Performance - No N+1 queries"""
        # Create multiple employees with shifts
        employees = []
        for i in range(10):
            emp = Employee.objects.create(
                user_id=f"PERF{i:03d}",
                name=f"Performance Test {i}",
                department=self.dept,
                is_active=True
            )
            employees.append(emp)
            
            EmployeeShift.objects.create(
                employee=emp,
                shift=self.shift_morning,
                scope='EMPLOYEE',
                start_date=date(2026, 2, 1)
            )
        
        # Reset query counter
        connection.queries_log.clear()
        
        # Execute with query logging
        with self.assertNumQueries(8, using='default'):
            result = get_schedule_calendar(
                start_date=date(2026, 2, 1),
                end_date=date(2026, 2, 28)
            )
        
        # Verify results
        # Should have original 3 + 10 new = 13 employees
        self.assertEqual(len(result['employees']), 13)
        
        # Each should have 28 days
        for emp_schedule in result['employees']:
            self.assertEqual(len(emp_schedule['schedule']), 28)
    
    def test_employee_ids_filter(self):
        """Test: Filtro por employee_ids funciona correctamente"""
        result = get_schedule_calendar(
            start_date=date(2026, 2, 1),
            end_date=date(2026, 2, 3),
            employee_ids=[self.emp1.id, self.emp2.id]
        )
        
        # Should only return 2 employees
        self.assertEqual(len(result['employees']), 2)
        returned_ids = [e['id'] for e in result['employees']]
        self.assertIn(self.emp1.id, returned_ids)
        self.assertIn(self.emp2.id, returned_ids)
        self.assertNotIn(self.emp3.id, returned_ids)
    
    def test_date_range_generation(self):
        """Test: Generación correcta de rango de fechas"""
        result = get_schedule_calendar(
            start_date=date(2026, 2, 1),
            end_date=date(2026, 2, 5)
        )
        
        emp1_schedule = next(e for e in result['employees'] if e['id'] == self.emp1.id)
        dates = [day['date'] for day in emp1_schedule['schedule']]
        
        expected_dates = [
            '2026-02-01', '2026-02-02', '2026-02-03', '2026-02-04', '2026-02-05'
        ]
        self.assertEqual(dates, expected_dates)
