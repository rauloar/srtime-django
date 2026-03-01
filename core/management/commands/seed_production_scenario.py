"""
Production scenario seeder - creates realistic company structure with hierarchy model.

Creates:
- 1 Company
- 3 Departments: Administración, Fábrica, TI
- Shifts and Timetables following department-based hierarchy
- 27 Employees distributed across departments
- Realistic attendance logs for the last 7 days

Usage:
    python manage.py seed_production_scenario [--clear-all] [--days=7]
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, date, timedelta, time
from random import randint, choice
from core.models import (
    Company, Department, Employee, AttendanceLog,
    Timetable, Shift, ShiftTimetable, EmployeeShift, ScheduleOverride, Device
)


class Command(BaseCommand):
    help = 'Seed production scenario with department-based shift hierarchy'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-all',
            action='store_true',
            help='Clear all data before seeding',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days of attendance logs to generate (default: 7)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== Production Scenario Seeder ===\n'))

        if options['clear_all']:
            self.stdout.write('🗑️  Clearing database...')
            cleared = self.clear_database()
            if not cleared:
                self.stdout.write(self.style.ERROR(
                    '❌ No se pudo limpiar completamente la base de datos. Abortando seeder.'
                ))
                return
        else:
            self.stdout.write(self.style.ERROR(
                '❌ Este seeder solo se ejecuta con --clear-all para garantizar base limpia.'
            ))
            return

        self.stdout.write('📊 Creating company structure...')
        company = self.create_company()

        self.stdout.write('🏢 Creating departments...')
        dept_admin, dept_fabrica, dept_ti = self.create_departments(company)

        self.stdout.write('⏰ Creating timetables...')
        tt_admin, tt_fabrica_man, tt_fabrica_tarde, tt_ti_flex = self.create_timetables()

        self.stdout.write('🔄 Creating shifts...')
        shift_admin, shift_fabrica_rotativo, shift_ti = self.create_shifts(
            tt_admin, tt_fabrica_man, tt_fabrica_tarde, tt_ti_flex
        )

        self.stdout.write('🔗 Assigning shifts to departments (hierarchy)...')
        self.assign_shifts_to_departments(
            dept_admin, shift_admin,
            dept_fabrica, shift_fabrica_rotativo,
            dept_ti, shift_ti
        )

        self.stdout.write('👥 Creating employees...')
        employees = self.create_employees(dept_admin, dept_fabrica, dept_ti, shift_fabrica_rotativo)

        self.stdout.write('📝 Creating attendance logs...')
        device = self.get_or_create_device()
        days = options['days']
        self.create_attendance_logs(employees, device, days)

        # Summary
        self.stdout.write(self.style.SUCCESS('\n✅ Production scenario seeded successfully!\n'))
        self.stdout.write(f'Company: {company.name}')
        self.stdout.write(f'Departments: {Department.objects.count()}')
        self.stdout.write(f'Timetables: {Timetable.objects.count()}')
        self.stdout.write(f'Shifts: {Shift.objects.count()}')
        self.stdout.write(f'Individual employee shift assignments: {EmployeeShift.objects.filter(scope="EMPLOYEE").count()}')
        self.stdout.write(f'Employees: {Employee.objects.count()}')
        self.stdout.write(f'  - Administración: {Employee.objects.filter(department=dept_admin).count()}')
        self.stdout.write(f'  - Fábrica: {Employee.objects.filter(department=dept_fabrica).count()}')
        self.stdout.write(f'  - TI: {Employee.objects.filter(department=dept_ti).count()}')
        self.stdout.write(f'Attendance logs: {AttendanceLog.objects.count()}')
        self.stdout.write('\nAccess the system at: http://localhost:3000\n')

    def clear_database(self) -> bool:
        """Clear all data in reverse dependency order. Returns True if fully cleared."""
        try:
            from django.db import transaction
            
            # Ensure we're not in atomic block, then use explicit transactions
            with transaction.atomic():
                AttendanceLog.objects.all().delete()
                ScheduleOverride.objects.all().delete()
                EmployeeShift.objects.all().delete()
                Employee.objects.all().delete()
                ShiftTimetable.objects.all().delete()
                Shift.objects.all().delete()
                Timetable.objects.all().delete()
                Department.objects.all().delete()
                Company.objects.all().delete()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error during clear: {e}'))
            return False
        
        # Force database query refresh by re-querying
        import time
        time.sleep(0.1)  # Small delay to ensure DB sync
        
        # Verify deletion with fresh queries
        from django.db import connection
        connection  # Force connection
        Employee.objects.all().query  # Force SQL generation
        
        remaining = (
            AttendanceLog.objects.exists()
            or ScheduleOverride.objects.exists()
            or EmployeeShift.objects.exists()
            or Employee.objects.exists()
            or ShiftTimetable.objects.exists()
            or Shift.objects.exists()
            or Timetable.objects.exists()
            or Department.objects.exists()
            or Company.objects.exists()
        )
        if remaining:
            # If still remaining, try harder
            counts = {
                'Employee': Employee.objects.count(),
                'AttendanceLog': AttendanceLog.objects.count(),
                'EmployeeShift': EmployeeShift.objects.count(),
            }
            self.stdout.write(self.style.ERROR(f'  ❌ Data remaining after clear: {counts}'))
            return False
        self.stdout.write('  ✓ Database cleared')
        return True

    def create_company(self):
        """Create main company."""
        company = Company.objects.create(
            name='Empresa Productiva S.A.',
            code='EMPROD',
            address='Av. Industrial 1234, Ciudad',
            website='www.empresaproductiva.com.ar'
        )
        self.stdout.write(f'  ✓ {company.name}')
        return company

    def create_departments(self, company):
        """Create 3 departments."""
        dept_admin = Department.objects.create(
            name='Administración',
            code='ADMIN',
            company=company
        )
        
        dept_fabrica = Department.objects.create(
            name='Fábrica',
            code='FAB',
            company=company
        )
        
        dept_ti = Department.objects.create(
            name='TI',
            code='TI',
            company=company
        )
        
        self.stdout.write(f'  ✓ {dept_admin.name}, {dept_fabrica.name}, {dept_ti.name}')
        return dept_admin, dept_fabrica, dept_ti

    def create_timetables(self):
        """Create 4 timetables for different work schedules."""
        
        # Administración: 8-17 (60 min almuerzo = 8h trabajo)
        tt_admin = Timetable.objects.create(
            name='Administrativo 8-17',
            on_duty_time=time(8, 0),
            off_duty_time=time(17, 0),
            late_allow_minutes=10,
            early_leave_allow_minutes=10,
            break_minutes=60,
            required_minutes=480,  # 8 hours
            is_flexible=False,
            rounding_rule='5min'
        )
        
        # Fábrica Mañana: 6-14 (45 min parada = 7h 15min trabajo)
        tt_fabrica_man = Timetable.objects.create(
            name='Fábrica Mañana 6-14',
            on_duty_time=time(6, 0),
            off_duty_time=time(14, 0),
            late_allow_minutes=5,
            early_leave_allow_minutes=5,
            break_minutes=45,
            required_minutes=435,  # 7.25 hours
            is_flexible=False,
            rounding_rule='5min'
        )
        
        # Fábrica Tarde: 14-18 (sin parada = 4h trabajo)
        tt_fabrica_tarde = Timetable.objects.create(
            name='Fábrica Tarde 14-18',
            on_duty_time=time(14, 0),
            off_duty_time=time(18, 0),
            late_allow_minutes=5,
            early_leave_allow_minutes=5,
            break_minutes=0,
            required_minutes=240,  # 4 hours
            is_flexible=False,
            rounding_rule='5min'
        )
        
        # TI: Flexible (máximo 120 min = 2h por día)
        tt_ti_flex = Timetable.objects.create(
            name='TI Flexible',
            on_duty_time=time(0, 0),
            off_duty_time=time(23, 59),
            check_in_start=time(6, 0),
            check_in_end=time(12, 0),
            check_out_start=time(14, 0),
            check_out_end=time(22, 0),
            required_minutes=120,  # 2 hours
            is_flexible=True
        )
        
        self.stdout.write(f'  ✓ Admin 8-17, Fábrica Mañana 6-14, Fábrica Tarde 14-18, TI Flexible')
        return tt_admin, tt_fabrica_man, tt_fabrica_tarde, tt_ti_flex

    def create_shifts(self, tt_admin, tt_fabrica_man, tt_fabrica_tarde, tt_ti_flex):
        """Create shifts and link to timetables via ShiftTimetable.
        
        Fábrica uses ROTATIVE 7-day cycle (no hardcoding per employee).
        Other departments use fixed weekly cycle (cycle_days=0).
        """
        
        # Turno Administración (L-V, weekly cycle)
        shift_admin = Shift.objects.create(
            name='Turno Administrativo',
            cycle_days=0
        )
        for weekday in range(5):  # Monday=0 to Friday=4
            ShiftTimetable.objects.create(
                shift=shift_admin,
                timetable=tt_admin,
                day_index=weekday
            )
        
        # Turno Fábrica ROTATIVO (7 días, cycle_days=7)
        # Patrón: Lun-Mar Mañana, Mié-Vie Tarde, Sáb Mañana, Dom Descanso
        shift_fabrica_rotativo = Shift.objects.create(
            name='Turno Fábrica Rotativo',
            cycle_days=7  # 7-day rotation
        )
        rotation_pattern = [
            (0, tt_fabrica_man),   # Lunes: Mañana
            (1, tt_fabrica_man),   # Martes: Mañana
            (2, tt_fabrica_tarde), # Miércoles: Tarde
            (3, tt_fabrica_tarde), # Jueves: Tarde
            (4, tt_fabrica_tarde), # Viernes: Tarde
            (5, tt_fabrica_man),   # Sábado: Mañana
            # Domingo (6): Descanso, sin ShiftTimetable
        ]
        for day_idx, timetable in rotation_pattern:
            ShiftTimetable.objects.create(
                shift=shift_fabrica_rotativo,
                timetable=timetable,
                day_index=day_idx
            )
        
        # Turno TI (L-V, flexible)
        shift_ti = Shift.objects.create(
            name='Turno TI Flexible',
            cycle_days=0
        )
        for weekday in range(5):  # Monday=0 to Friday=4
            ShiftTimetable.objects.create(
                shift=shift_ti,
                timetable=tt_ti_flex,
                day_index=weekday
            )
        
        self.stdout.write(f'  ✓ 3 shifts created (Admin fijo, Fábrica rotativo 7d, TI flexible)')
        return shift_admin, shift_fabrica_rotativo, shift_ti

    def assign_shifts_to_departments(self, dept_admin, shift_admin, dept_fabrica, 
                                     shift_fabrica_rotativo, dept_ti, shift_ti):
        """Departments have NO shift assigned (hierarchy model).
        
        All employees get individual shift assignments (EMPLOYEE scope).
        This allows flexibility for rotations via ScheduleOverride.
        """
        self.stdout.write(f'  ✓ Departments created without shift assignments')
        self.stdout.write(f'  → All shifts will be assigned individually to employees')

    def create_employees(self, dept_admin, dept_fabrica, dept_ti, shift_fabrica_rotativo):
        """Create 27 employees distributed across departments with individual shift assignments.
        
        All Fábrica employees use the SAME rotative shift (cycle_days=7).
        The rotation logic is in the shift, not in employee data (no hardcoding).
        """
        employees = []
        start_date = date.today() - timedelta(days=30)
        shift_admin = Shift.objects.get(name='Turno Administrativo')
        shift_ti = Shift.objects.get(name='Turno TI Flexible')
        
        # Administración: 5 employees (all with individual shift assignment)
        admin_names = [
            'Ana García', 'Carlos Ruiz', 'María López', 
            'Roberto Fernández', 'Laura Martínez'
        ]
        for i, name in enumerate(admin_names, start=1):
            emp = Employee.objects.create(
                user_id=f'A{i:03d}',
                name=name,
                department=dept_admin,
                is_active=True,
                email=f"{name.lower().replace(' ', '.')}@empresaproductiva.com.ar"
            )
            # Individual shift assignment
            EmployeeShift.objects.create(
                employee=emp,
                shift=shift_admin,
                scope='EMPLOYEE',
                start_date=start_date
            )
            employees.append(emp)
        
        self.stdout.write(f'  ✓ Administración: {len(admin_names)} employees (individual shifts)')
        
        # Fábrica: 20 employees - ALL use same ROTATIVE shift (cycle_days=7)
        # No hardcoding per employee: rotation is in the Shift model
        fabrica_names = [f'Operario Fábrica {i}' for i in range(1, 21)]
        
        for i, name in enumerate(fabrica_names, start=1):
            emp = Employee.objects.create(
                user_id=f'FAB{i:03d}',
                name=name,
                department=dept_fabrica,
                is_active=True,
                email=f"operario.{i}@empresaproductiva.com.ar"
            )
            # Individual shift assignment - ALL use rotative shift
            EmployeeShift.objects.create(
                employee=emp,
                shift=shift_fabrica_rotativo,
                scope='EMPLOYEE',
                start_date=start_date
            )
            employees.append(emp)
        
        self.stdout.write(f'  ✓ Fábrica: {len(fabrica_names)} employees (ROTATIVE 7-day cycle)')
        
        # TI: 2 employees (individual shift assignment)
        ti_names = ['Juan Pérez', 'Sandra González']
        for i, name in enumerate(ti_names, start=1):
            emp = Employee.objects.create(
                user_id=f'TI{i:03d}',
                name=name,
                department=dept_ti,
                is_active=True,
                email=f"{name.lower().replace(' ', '.')}@empresaproductiva.com.ar"
            )
            # Individual shift assignment
            EmployeeShift.objects.create(
                employee=emp,
                shift=shift_ti,
                scope='EMPLOYEE',
                start_date=start_date
            )
            employees.append(emp)
        
        self.stdout.write(f'  ✓ TI: {len(ti_names)} employees (individual shifts)')
        
        return employees

    def get_or_create_device(self):
        """Get or create default device for logs."""
        device, created = Device.objects.get_or_create(
            name='Terminal Principal',
            defaults={
                'ip': '192.168.1.100',
                'port': 4370,
                'enabled': True
            }
        )
        return device

    def create_attendance_logs(self, employees, device, days):
        """Create realistic attendance logs for the last N days."""
        logs_created = 0
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)
        
        for current_date in (start_date + timedelta(n) for n in range(days)):
            # Skip weekends for some employees
            weekday = current_date.weekday()
            
            for emp in employees:
                dept_name = emp.department.name
                
                # Determine schedule
                if dept_name == 'Administración':
                    if weekday >= 5:  # Skip weekends
                        continue
                    in_time = time(8, randint(0, 15))  # 8:00-8:15
                    out_time = time(17, randint(0, 10))  # 17:00-17:10
                    
                elif dept_name == 'Fábrica':
                    if 'Mañana' in emp.name:
                        if weekday == 6:  # Skip Sunday
                            continue
                        in_time = time(6, randint(0, 10))  # 6:00-6:10
                        out_time = time(14, randint(0, 5))  # 14:00-14:05
                    else:  # Tarde
                        if weekday >= 5:  # Skip weekends
                            continue
                        in_time = time(14, randint(0, 5))  # 14:00-14:05
                        out_time = time(18, randint(0, 5))  # 18:00-18:05
                        
                elif dept_name == 'TI':
                    if weekday >= 5:  # Skip weekends
                        continue
                    # Flexible: random entry/exit
                    in_time = time(randint(8, 11), randint(0, 59))
                    out_time = time(randint(16, 20), randint(0, 59))
                
                # 10% chance of absence (no logs)
                if randint(1, 10) == 1:
                    continue
                
                # Create IN log
                in_dt = timezone.make_aware(datetime.combine(current_date, in_time))
                AttendanceLog.objects.create(
                    device=device,
                    employee=emp,
                    user_id=emp.user_id,
                    timestamp=in_dt,
                    status=0,
                    punch=0,  # IN
                    verify_mode=1
                )
                logs_created += 1
                
                # 5% chance of incomplete day (no OUT)
                if randint(1, 20) == 1:
                    continue
                
                # Create OUT log
                out_dt = timezone.make_aware(datetime.combine(current_date, out_time))
                AttendanceLog.objects.create(
                    device=device,
                    employee=emp,
                    user_id=emp.user_id,
                    timestamp=out_dt,
                    status=0,
                    punch=1,  # OUT
                    verify_mode=1
                )
                logs_created += 1
        
        self.stdout.write(f'  ✓ {logs_created} attendance logs created for {days} days')
