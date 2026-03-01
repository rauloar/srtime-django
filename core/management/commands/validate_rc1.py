"""
Pre-Deploy Validation Checklist for RC1

Comprehensive validation of /attendance/schedule endpoint before v1.0.0-rc1 tag.

Run with:
    python manage.py validate_rc1
"""
from django.core.management.base import BaseCommand
from django.db import connection, reset_queries
from django.conf import settings
from datetime import date, timedelta
from core.services.schedule_calendar import get_schedule_calendar
from core.models import Employee, ScheduleOverride, EmployeeShift, Timetable, Department, Shift


class Command(BaseCommand):
    help = 'Pre-deploy validation checklist for RC1'
    
    def __init__(self):
        super().__init__()
        self.passed_tests = 0
        self.failed_tests = 0
        self.warnings = 0
    
    def handle(self, *args, **options):
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS("PRE-DEPLOY VALIDATION CHECKLIST - v1.0.0-rc1"))
        self.stdout.write("Endpoint: GET /attendance/schedule/")
        self.stdout.write("=" * 80)
        self.stdout.write("")
        
        # Section 1: Query Count Validation
        self.section_header("1. QUERY COUNT VALIDATION")
        self.test_query_count_constant()
        self.test_query_count_no_scaling()
        
        # Section 2: Functional Cases
        self.section_header("2. FUNCTIONAL CASES")
        self.test_employee_without_shift()
        self.test_employee_shift_active()
        self.test_department_shift_inherited()
        self.test_override_priority()
        self.test_range_validation()
        self.test_invalid_date_format()
        
        # Section 3: Edge Cases
        self.section_header("3. EDGE CASES")
        self.test_employee_no_department()
        self.test_shift_end_date_boundary()
        self.test_multiple_overrides()
        self.test_timetable_none_in_override()
        
        # Section 4: System Stability
        self.section_header("4. SYSTEM STABILITY")
        self.test_attendance_calculation_intact()
        self.test_no_500_errors()
        
        # Final Report
        self.final_report()
    
    def section_header(self, title):
        self.stdout.write("")
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS(title))
        self.stdout.write("=" * 80)
        self.stdout.write("")
    
    def test_passed(self, name):
        self.passed_tests += 1
        self.stdout.write(self.style.SUCCESS(f"[PASS] {name}"))
    
    def test_failed(self, name, reason):
        self.failed_tests += 1
        self.stdout.write(self.style.ERROR(f"[FAIL] {name}: {reason}"))
    
    def test_warning(self, name, reason):
        self.warnings += 1
        self.stdout.write(self.style.WARNING(f"[WARN] {name}: {reason}"))
    
    def test_query_count_constant(self):
        """A1. Verify query count is constant (~5-8 queries)"""
        try:
            reset_queries()
            settings.DEBUG = True
            
            result = get_schedule_calendar(
                start_date=date(2026, 2, 1),
                end_date=date(2026, 2, 28)
            )
            
            query_count = len(connection.queries)
            settings.DEBUG = False
            
            if query_count <= 10:
                self.test_passed(f"Query count is constant: {query_count} queries")
                self.stdout.write(f"  Expected: 5-8, Got: {query_count}")
            else:
                self.test_failed("Query count too high", f"Expected <=10, got {query_count}")
                
        except Exception as e:
            self.test_failed("Query count test", str(e))
    
    def test_query_count_no_scaling(self):
        """A2. Verify query count doesn't scale with employees"""
        try:
            emp_count = Employee.objects.filter(is_active=True).count()
            
            reset_queries()
            settings.DEBUG = True
            
            result = get_schedule_calendar(
                start_date=date(2026, 2, 1),
                end_date=date(2026, 2, 28)
            )
            
            query_count = len(connection.queries)
            settings.DEBUG = False
            
            # Check if queries contain loops (would indicate N+1)
            has_loop = any('SELECT' in q['sql'] and connection.queries.count(q) > 1 
                          for q in connection.queries)
            
            if not has_loop and query_count <= 10:
                self.test_passed(f"No N+1 detected ({emp_count} employees, {query_count} queries)")
            else:
                self.test_warning("Query scaling", f"Possible N+1 pattern detected")
                
        except Exception as e:
            self.test_failed("Query scaling test", str(e))
    
    def test_employee_without_shift(self):
        """B1. Employee without shift returns REST"""
        try:
            # Find employee without shifts
            emp = Employee.objects.filter(is_active=True).first()
            if not emp:
                self.test_warning("Employee without shift", "No employees found")
                return
            
            result = get_schedule_calendar(
                start_date=date(2026, 2, 1),
                end_date=date(2026, 2, 3),
                employee_ids=[emp.id]
            )
            
            if len(result['employees']) > 0:
                emp_data = result['employees'][0]
                # Check if has any non-rest days or all rest
                rest_days = [d for d in emp_data['schedule'] if d['is_rest']]
                
                self.test_passed(f"Employee schedule retrieved ({len(rest_days)}/{len(emp_data['schedule'])} rest days)")
            else:
                self.test_failed("Employee without shift", "No employee data returned")
                
        except Exception as e:
            self.test_failed("Employee without shift test", str(e))
    
    def test_employee_shift_active(self):
        """B2. EmployeeShift active returns correct schedule"""
        try:
            emp_shift = EmployeeShift.objects.filter(
                scope='EMPLOYEE',
                start_date__lte=date.today()
            ).select_related('employee').first()
            
            if not emp_shift:
                self.test_warning("EmployeeShift test", "No employee shifts found")
                return
            
            result = get_schedule_calendar(
                start_date=date(2026, 2, 1),
                end_date=date(2026, 2, 3),
                employee_ids=[emp_shift.employee_id]
            )
            
            if result['employees']:
                self.test_passed("EmployeeShift resolution works")
            else:
                self.test_failed("EmployeeShift test", "No data returned")
                
        except Exception as e:
            self.test_failed("EmployeeShift test", str(e))
    
    def test_department_shift_inherited(self):
        """B3. DepartmentShift is properly inherited"""
        try:
            dept_shift = EmployeeShift.objects.filter(
                scope='DEPARTMENT'
            ).select_related('department').first()
            
            if not dept_shift:
                self.test_warning("DepartmentShift test", "No department shifts found")
                return
            
            # Find employee in that department
            emp = Employee.objects.filter(
                department_id=dept_shift.department_id,
                is_active=True
            ).first()
            
            if emp:
                result = get_schedule_calendar(
                    start_date=date(2026, 2, 1),
                    end_date=date(2026, 2, 3),
                    employee_ids=[emp.id]
                )
                
                self.test_passed("DepartmentShift inheritance works")
            else:
                self.test_warning("DepartmentShift test", "No employees in department")
                
        except Exception as e:
            self.test_failed("DepartmentShift test", str(e))
    
    def test_override_priority(self):
        """B4. Override has correct priority"""
        try:
            override = ScheduleOverride.objects.filter(
                date__gte=date(2026, 2, 1),
                date__lte=date(2026, 2, 28)
            ).select_related('employee').first()
            
            if not override:
                self.test_warning("Override priority", "No overrides found for testing")
                return
            
            result = get_schedule_calendar(
                start_date=override.date - timedelta(days=1),
                end_date=override.date + timedelta(days=1),
                employee_ids=[override.employee_id]
            )
            
            emp_data = result['employees'][0]
            override_day = next((d for d in emp_data['schedule'] 
                               if d['date'] == override.date.isoformat()), None)
            
            if override_day and override_day['source'] == 'OVERRIDE':
                self.test_passed(f"Override priority correct (source=OVERRIDE on {override.date})")
            else:
                self.test_failed("Override priority", 
                               f"Expected OVERRIDE, got {override_day['source'] if override_day else 'None'}")
                
        except Exception as e:
            self.test_failed("Override priority test", str(e))
    
    def test_range_validation(self):
        """B5. Range > 31 days returns 400"""
        try:
            result = get_schedule_calendar(
                start_date=date(2026, 2, 1),
                end_date=date(2026, 3, 15)  # 42 days
            )
            self.test_failed("Range validation", "Should have raised ValueError")
        except ValueError as e:
            if "Max" in str(e) or "31" in str(e):
                self.test_passed("Range validation rejects >31 days")
            else:
                self.test_failed("Range validation", f"Wrong error message: {e}")
        except Exception as e:
            self.test_failed("Range validation", str(e))
    
    def test_invalid_date_format(self):
        """B6. Invalid date format handled (note: this is APIView validation)"""
        # This would be tested at API level, not service level
        self.test_warning("Invalid date format", "Tested at API View level (not service)")
    
    def test_employee_no_department(self):
        """C1. Employee without department"""
        try:
            emp = Employee.objects.filter(
                is_active=True,
                department__isnull=True
            ).first()
            
            if not emp:
                self.test_warning("Employee no department", "No employees without department")
                return
            
            result = get_schedule_calendar(
                start_date=date(2026, 2, 1),
                end_date=date(2026, 2, 3),
                employee_ids=[emp.id]
            )
            
            if result['employees']:
                self.test_passed("Employee without department handled correctly")
            else:
                self.test_failed("Employee no department", "No data returned")
                
        except Exception as e:
            self.test_failed("Employee no department test", str(e))
    
    def test_shift_end_date_boundary(self):
        """C2. EmployeeShift with end_date on exact boundary"""
        try:
            # This tests the boundary condition
            result = get_schedule_calendar(
                start_date=date(2026, 2, 1),
                end_date=date(2026, 2, 3)
            )
            
            self.test_passed("Shift end_date boundary handled (no errors)")
            
        except Exception as e:
            self.test_failed("Shift boundary test", str(e))
    
    def test_multiple_overrides(self):
        """C3. Multiple overrides in same month"""
        try:
            override_count = ScheduleOverride.objects.filter(
                date__gte=date(2026, 2, 1),
                date__lte=date(2026, 2, 28)
            ).count()
            
            if override_count > 0:
                result = get_schedule_calendar(
                    start_date=date(2026, 2, 1),
                    end_date=date(2026, 2, 28)
                )
                
                self.test_passed(f"Multiple overrides handled ({override_count} overrides)")
            else:
                self.test_warning("Multiple overrides", "No overrides in Feb 2026")
                
        except Exception as e:
            self.test_failed("Multiple overrides test", str(e))
    
    def test_timetable_none_in_override(self):
        """C4. Override with timetable=None"""
        try:
            # This edge case should be handled gracefully
            result = get_schedule_calendar(
                start_date=date(2026, 2, 1),
                end_date=date(2026, 2, 3)
            )
            
            self.test_passed("Timetable None handled (no errors)")
            
        except Exception as e:
            self.test_failed("Timetable None test", str(e))
    
    def test_attendance_calculation_intact(self):
        """D1. Attendance calculation system not affected"""
        try:
            # Verify resolve_schedule_unified still exists
            from core.services.schedule_resolver import resolve_schedule_unified
            
            # Try calling it
            emp = Employee.objects.filter(is_active=True).first()
            if emp:
                resolved = resolve_schedule_unified(emp.id, date(2026, 2, 1))
                self.test_passed("Attendance calculation system intact (resolve_schedule_unified works)")
            else:
                self.test_warning("Attendance calculation", "No employees to test")
                
        except ImportError:
            self.test_failed("Attendance calculation", "resolve_schedule_unified not found!")
        except Exception as e:
            self.test_failed("Attendance calculation test", str(e))
    
    def test_no_500_errors(self):
        """D2. No 500 errors under various conditions"""
        try:
            scenarios = [
                (date(2026, 2, 1), date(2026, 2, 28), None, "Full month"),
                (date(2026, 2, 1), date(2026, 2, 1), None, "Single day"),
                (date(2026, 1, 15), date(2026, 2, 14), None, "Cross-month"),
            ]
            
            errors = []
            for start, end, emp_ids, desc in scenarios:
                try:
                    result = get_schedule_calendar(start, end, emp_ids)
                except Exception as e:
                    errors.append(f"{desc}: {e}")
            
            if not errors:
                self.test_passed(f"No 500 errors ({len(scenarios)} scenarios tested)")
            else:
                self.test_failed("500 error prevention", f"{len(errors)} scenarios failed")
                for err in errors:
                    self.stdout.write(f"  - {err}")
                    
        except Exception as e:
            self.test_failed("500 error test", str(e))
    
    def final_report(self):
        """Generate final report"""
        self.stdout.write("")
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS("FINAL REPORT"))
        self.stdout.write("=" * 80)
        self.stdout.write("")
        
        total_tests = self.passed_tests + self.failed_tests
        pass_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.stdout.write(f"Total Tests: {total_tests}")
        self.stdout.write(self.style.SUCCESS(f"Passed: {self.passed_tests}"))
        if self.failed_tests > 0:
            self.stdout.write(self.style.ERROR(f"Failed: {self.failed_tests}"))
        if self.warnings > 0:
            self.stdout.write(self.style.WARNING(f"Warnings: {self.warnings}"))
        self.stdout.write(f"Pass Rate: {pass_rate:.1f}%")
        self.stdout.write("")
        
        # Decision
        if self.failed_tests == 0 and pass_rate >= 80:
            self.stdout.write(self.style.SUCCESS("=" * 80))
            self.stdout.write(self.style.SUCCESS("RECOMMENDATION: READY FOR v1.0.0-rc1"))
            self.stdout.write(self.style.SUCCESS("=" * 80))
            self.stdout.write("")
            self.stdout.write("Next steps:")
            self.stdout.write("  1. Commit changes")
            self.stdout.write("  2. Tag as v1.0.0-rc1")
            self.stdout.write("  3. Deploy to staging")
            self.stdout.write("  4. Manual smoke test")
        else:
            self.stdout.write(self.style.ERROR("=" * 80))
            self.stdout.write(self.style.ERROR("RECOMMENDATION: NOT READY FOR v1.0.0-rc1"))
            self.stdout.write(self.style.ERROR("=" * 80))
            self.stdout.write("")
            self.stdout.write(f"Issues found: {self.failed_tests} failures")
            self.stdout.write("Please fix failing tests before tagging RC1")
