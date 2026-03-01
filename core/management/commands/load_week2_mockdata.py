"""
Management command to reset database and load realistic mock data for Week 2 testing.

Usage:
    python manage.py load_week2_mockdata

This will:
1. Clean attendance-related data (logs, operational indices)
2. Create/update: 1 company, 2 departments, 6 employees
3. Create realistic attendance logs for today
4. Trigger attendance calculation

Employees for 2026-02-02 (today):
- Ana García (Normal) - 8h complete
- Carlos López (Normal) - 8h complete
- María Rodríguez (LATE) - arrived 35min late
- Juan Pérez (ABSENT) - no logs
- Laura Martínez (PENDING) - only IN, no OUT yet
- Pedro Sánchez (Normal) - 8h complete
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, date, timedelta, time
from core.models import (
    Company, Department, Employee, AttendanceLog,
    Timetable, Shift, EmployeeShift
)
from core.models_operational_index import AttendanceDayIndex
from core.models_timeline import AttendanceTimelineBlock
from core.models_engine_snapshot import AttendanceEngineSnapshot


class Command(BaseCommand):
    help = 'Load realistic mock data for Week 2 Dashboard testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean-all',
            action='store_true',
            help='Also delete employees and departments (use with caution)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== Week 2 Mock Data Loader ===\n'))

        # Step 1: Clean attendance data
        self.stdout.write('Step 1: Cleaning attendance data...')
        self.clean_attendance_data()

        # Step 2: Clean structure if requested
        if options['clean_all']:
            self.stdout.write('Step 2: Cleaning employees and departments...')
            self.clean_structure()

        # Step 3: Create/update structure
        self.stdout.write('Step 3: Creating company and departments...')
        company, dept_rrhh, dept_it = self.create_structure()

        # Step 4: Create/update employees
        self.stdout.write('Step 4: Creating employees...')
        employees = self.create_employees(dept_rrhh, dept_it)

        # Step 5: Create timetable and shifts
        self.stdout.write('Step 5: Creating timetables and shifts...')
        self.create_timetables_and_shifts(employees)

        # Step 6: Create attendance logs for today
        self.stdout.write('Step 6: Creating attendance logs for today...')
        today = date.today()
        self.create_todays_logs(employees, today)

        # Step 7: Trigger calculation (if service exists)
        self.stdout.write('Step 7: Triggering attendance calculation...')
        self.calculate_attendance(employees, today)

        # Summary
        self.stdout.write(self.style.SUCCESS('\n✅ Mock data loaded successfully!\n'))
        self.stdout.write(f'Date: {today}')
        self.stdout.write(f'Employees: {len(employees)}')
        self.stdout.write(f'Logs created: {AttendanceLog.objects.filter(timestamp__date=today).count()}')
        self.stdout.write('\nTest the Dashboard at: http://localhost:9000/dashboard\n')

    def clean_attendance_data(self):
        """Remove all attendance logs (safe for missing tables)."""
        deleted = []
       
        # Only delete from tables that exist
        try:
            count = AttendanceLog.objects.all().delete()[0]
            deleted.append(f'logs({count})')
        except Exception as e:
            self.stdout.write(f'  ⚠ Logs: {str(e)[:50]}')
        
        try:
            count = AttendanceDayIndex.objects.all().delete()[0]
            deleted.append(f'indices({count})')
        except Exception:
            pass
        
        try:
            count = AttendanceTimelineBlock.objects.all().delete()[0]
            deleted.append(f'timeline({count})')
        except Exception:
            pass
        
        try:
            count = AttendanceEngineSnapshot.objects.all().delete()[0]
            deleted.append(f'snapshots({count})')
        except Exception:
            pass
        
        try:
            count = EmployeeShift.objects.all().delete()[0]
            deleted.append(f'shifts({count})')
        except Exception:
            pass
        
        if deleted:
            self.stdout.write(self.style.WARNING(f'  Deleted: {", ".join(deleted)}'))
        else:
            self.stdout.write(self.style.WARNING('  No data to delete or tables missing'))

    def clean_structure(self):
        """Remove employees and departments (use with caution)."""
        Employee.objects.all().delete()
        Department.objects.all().delete()
        self.stdout.write(self.style.WARNING('  Deleted: employees, departments'))

    def create_structure(self):
        """Create/update company and departments."""
        company, _ = Company.objects.get_or_create(
            name='Empresa Demo',
            defaults={
                'code': 'DEMO',
                'address': 'Av. Principal 123',
                'website': 'www.empresa-demo.com'
            }
        )

        dept_rrhh, _ = Department.objects.get_or_create(
            name='Recursos Humanos',
            defaults={'code': 'RRHH', 'company': company}
        )

        dept_it, _ = Department.objects.get_or_create(
            name='Tecnología',
            defaults={'code': 'IT', 'company': company}
        )

        self.stdout.write(f'  ✓ Company: {company.name}')
        self.stdout.write(f'  ✓ Departments: {dept_rrhh.name}, {dept_it.name}')

        return company, dept_rrhh, dept_it

    def create_employees(self, dept_rrhh, dept_it):
        """Create/update 6 employees with varied states."""
        employees_data = [
            {
                'user_id': '001',
                'name': 'Ana García',
                'department': dept_rrhh,
                'state': 'NORMAL',  # Complete 8h
            },
            {
                'user_id': '002',
                'name': 'Carlos López',
                'department': dept_it,
               'state': 'NORMAL',  # Complete 8h
            },
            {
                'user_id': '003',
                'name': 'María Rodríguez',
                'department': dept_rrhh,
                'state': 'LATE',  # Arrived 35min late
            },
            {
                'user_id': '004',
                'name': 'Juan Pérez',
                'department': dept_it,
                'state': 'ABSENT',  # No logs
            },
            {
                'user_id': '005',
                'name': 'Laura Martínez',
                'department': dept_rrhh,
                'state': 'PENDING',  # Only IN, no OUT
            },
            {
                'user_id': '006',
                'name': 'Pedro Sánchez',
                'department': dept_it,
                'state': 'NORMAL',  # Complete 8h
            },
        ]

        employees = []
        for data in employees_data:
            state = data.pop('state')
            emp, created = Employee.objects.update_or_create(
                user_id=data['user_id'],
                defaults={
                    'name': data['name'],
                    'department': data['department'],
                    'is_active': True,
                    'email': f"{data['name'].lower().replace(' ', '.')}@empresa-demo.com"
                }
            )
            emp.state_for_today = state  # Temporary attribute for log creation
            employees.append(emp)
            status = 'created' if created else 'updated'
            self.stdout.write(f'  ✓ {emp.name} ({state}) - {status}')

        return employees

    def create_timetables_and_shifts(self, employees):
        """Create standard 9-18h timetable and assign to all employees."""
        # Create timetable: 09:00 - 18:00 (8h work, 1h lunch)
        timetable, _ = Timetable.objects.get_or_create(
            name='Horario Estándar 9-18',
            defaults={
                'on_duty_time': '09:00',
                'off_duty_time': '18:00',
                'late_allow_minutes': 15,
                'early_leave_allow_minutes': 15,
                'break_minutes': 60,
                'required_minutes': 480,  # 8 hours
           'is_flexible': False
            }
        )

        # Create shift: Monday-Friday
        shift, _ = Shift.objects.get_or_create(
            name='Turno Diurno L-V',
        )

        # Create ShiftTimetable for Monday-Friday (days 0-4)
        from core.models import ShiftTimetable
        for day_index in range(5):  # 0=Monday to 4=Friday
            ShiftTimetable.objects.get_or_create(
                shift=shift,
                timetable=timetable,
                day_index=day_index
            )

        # Assign shift to all employees (for today's date)
        today = date.today()
        for emp in employees:
            EmployeeShift.objects.update_or_create(
                employee=emp,
                shift=shift,
                start_date=today - timedelta(days=30),  # Started 30 days ago
                defaults={
                    'end_date': None  # Ongoing
                }
            )

        self.stdout.write(f'  ✓ Timetable: {timetable.name} (09:00-18:00)')
        self.stdout.write(f'  ✓ Shift: {shift.name}')
        self.stdout.write(f'  ✓ Assigned to {len(employees)} employees')

    def create_todays_logs(self, employees, today):
        """Create realistic attendance logs for today based on employee state."""
        for emp in employees:
            state = getattr(emp, 'state_for_today', 'NORMAL')

            if state == 'NORMAL':
                # Complete day: IN at 09:00, OUT at 18:00
                self.create_log(emp, today, time(9, 0), 0)   # IN
                self.create_log(emp, today, time(18, 0), 1)  # OUT

            elif state == 'LATE':
                # Late arrival: IN at 09:35, OUT at 18:00
                self.create_log(emp, today, time(9, 35), 0)  # IN (35min late)
                self.create_log(emp, today, time(18, 0), 1)  # OUT

            elif state == 'PENDING':
                # Only IN, no OUT yet: IN at 09:00
                self.create_log(emp, today, time(9, 0), 0)   # IN only

            elif state == 'ABSENT':
                # No logs at all
                pass

            self.stdout.write(f'  ✓ {emp.name}: {state}')

    def create_log(self, employee, date, time_of_day, punch_state):
        """Create a single attendance log."""
        timestamp = timezone.make_aware(
            datetime.combine(date, time_of_day)
        )

        AttendanceLog.objects.create(
            user_id=employee.user_id,
            employee=employee,
            timestamp=timestamp,
            punch_state=punch_state,
            verify_type=1,  # Fingerprint
            work_code=0
        )

    def calculate_attendance(self, employees, today):
        """Trigger attendance calculation for today."""
        try:
            from core.services.attendance_application import AttendanceApplicationService

            service = AttendanceApplicationService()

            for emp in employees:
                try:
                    # Call process_employee_day which returns the calculation
                    calculation = service.process_employee_day(emp.id, today)
                    status = calculation.status if hasattr(calculation, 'status') else 'PROCESSED'
                    self.stdout.write(f'  ✓ Calculated: {emp.name} - {status}')
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  ⚠ Failed: {emp.name} - {str(e)}'))

        except ImportError:
            self.stdout.write(self.style.WARNING(
                '  ⚠ AttendanceApplicationService not found - skipping calculation'
            ))
            self.stdout.write('    Run calculation manually if needed')
