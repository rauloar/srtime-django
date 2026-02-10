"""
Script para poblar la base de datos con datos de prueba
Adaptado de ZKTimeWeb/tests/seed_data.py para Django
"""
import sys
import os
import random
from datetime import datetime, timedelta, date, time
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone

from core.models import (
    Company, Department, Employee, Device, User,
    Timetable, Shift, ShiftTimetable, EmployeeShift,
    AttendanceLog, Zone, Position, DailyAttendance,
    ScheduleOverride, Leave, Holiday
)

def seed():
    print("🌱 Seeding database (alpha test scenario)...")
    random.seed(2026)

    # 0. Clean database for a controlled test case
    print("🧹 Cleaning existing data...")
    AttendanceLog.objects.all().delete()
    DailyAttendance.objects.all().delete()
    ScheduleOverride.objects.all().delete()
    Leave.objects.all().delete()
    Holiday.objects.all().delete()
    EmployeeShift.objects.all().delete()
    ShiftTimetable.objects.all().delete()
    Shift.objects.all().delete()
    Timetable.objects.all().delete()
    User.objects.all().delete()
    Employee.objects.all().delete()
    Department.objects.all().delete()
    Position.objects.all().delete()
    Zone.objects.all().delete()
    Device.objects.all().delete()
    Company.objects.all().delete()

    # 1. Company
    company = Company.objects.create(
        name="SRTime Alpha Corp",
        code="ALPHA001",
        address="Av. Laboratorio 123",
        website="www.srtime.dev"
    )

    # 2. Department
    department = Department.objects.create(
        name="Operaciones",
        code="OPS",
        company=company,
    )

    # 3. Position (single for simplicity)
    position = Position.objects.create(
        name="Operario",
        code="OPR",
    )

    # 4. Device
    device = Device.objects.create(
        name="Terminal Alpha",
        ip="192.168.1.201",
        port=4370,
        enabled=True,
        device_name="iClock S880",
        serialnumber="SN-ALPHA-001",
    )

    # 5. Timetables (3 horarios)
    timetables = {
        "Morning": Timetable.objects.create(
            name="Tm_Morn_06-14",
            on_duty_time=time(6, 0, 0),
            off_duty_time=time(14, 0, 0),
            check_in_start=time(5, 30, 0),
            check_in_end=time(9, 0, 0),
            check_out_start=time(13, 0, 0),
            check_out_end=time(15, 30, 0),
            late_allow_minutes=10,
            early_leave_allow_minutes=10,
            work_days=1,
            is_flexible=False,
        ),
        "Afternoon": Timetable.objects.create(
            name="Tm_Aft_14-22",
            on_duty_time=time(14, 0, 0),
            off_duty_time=time(22, 0, 0),
            check_in_start=time(13, 0, 0),
            check_in_end=time(17, 0, 0),
            check_out_start=time(21, 0, 0),
            check_out_end=time(23, 30, 0),
            late_allow_minutes=10,
            early_leave_allow_minutes=10,
            work_days=1,
            is_flexible=False,
        ),
        "Night": Timetable.objects.create(
            name="Tm_Night_22-06",
            on_duty_time=time(22, 0, 0),
            off_duty_time=time(6, 0, 0),
            check_in_start=time(21, 0, 0),
            check_in_end=time(23, 59, 59),
            check_out_start=time(4, 0, 0),
            check_out_end=time(8, 0, 0),
            late_allow_minutes=10,
            early_leave_allow_minutes=10,
            work_days=1,
            is_flexible=False,
        ),
    }

    # 6. Shifts (3 turnos) linked to timetables
    shifts = {}
    for key, tt in timetables.items():
        shift = Shift.objects.create(name=f"Shift_{key}")
        shifts[key] = shift
        for day_idx in range(7):
            ShiftTimetable.objects.create(
                shift=shift,
                timetable=tt,
                day_index=day_idx,
            )

    # 7. Employees & Users (10 personas)
    employees = []
    for i in range(1, 11):
        user_id = f"EMP{i:03d}"
        name = f"Empleado {i:02d}"

        User.objects.create(
            device=device,
            uid=i,
            name=name,
            privilege=0,
            user_id=user_id,
            card=f"CARD{i:04d}",
        )

        emp = Employee.objects.create(
            user_id=user_id,
            name=name,
            department=department,
            position=position,
            email=f"emp{i:02d}@alpha.local",
            active=True,
        )
        employees.append(emp)

    # 8. Assign shifts (round-robin)
    shift_keys = list(shifts.keys())
    start_date = date(2026, 1, 11)
    end_date = date(2026, 2, 9)
    for idx, emp in enumerate(employees):
        shift_key = shift_keys[idx % len(shift_keys)]
        EmployeeShift.objects.create(
            scope="EMPLOYEE",
            employee=emp,
            shift=shifts[shift_key],
            start_date=start_date,
            end_date=end_date,
        )

    # 9. Attendance logs (30 days from 2026-02-09 backwards)
    print("📥 Creating attendance logs (30 days)...")
    log_count = 0
    tz = timezone.get_current_timezone()
    base_date = date(2026, 2, 9)

    for offset in range(0, 30):
        day = base_date - timedelta(days=offset)
        for emp in employees:
            has_forced_absence = (
                emp.user_id in {"EMP003", "EMP007"}
                and day.weekday() < 5
                and offset % 5 == 0
            )
            random_absence = random.random() < 0.08

            if has_forced_absence or random_absence:
                continue

            shift_key = shift_keys[(emp.id - 1) % len(shift_keys)]
            tt = timetables[shift_key]

            in_seconds = random.randint(0, 59)
            out_seconds = random.randint(0, 59)

            is_late_case = emp.user_id in {"EMP002", "EMP005"} and day.weekday() < 5 and offset % 4 == 1
            is_overtime_case = emp.user_id in {"EMP004", "EMP008"} and day.weekday() < 5 and offset % 6 == 2

            late_minutes = random.randint(5, 25) if is_late_case else 0
            overtime_minutes = random.randint(30, 90) if is_overtime_case else 0

            check_in = datetime.combine(day, tt.on_duty_time).replace(second=in_seconds)
            if late_minutes:
                check_in += timedelta(minutes=late_minutes)
            check_out_day = day

            if tt.off_duty_time <= tt.on_duty_time:
                check_out_day = day + timedelta(days=1)

            check_out = datetime.combine(check_out_day, tt.off_duty_time).replace(second=out_seconds)
            if overtime_minutes:
                check_out += timedelta(minutes=overtime_minutes)

            AttendanceLog.objects.create(
                device=device,
                user_id=emp.user_id,
                timestamp=timezone.make_aware(check_in, tz),
                status=0,
                punch=0,
                verify_mode=1,
            )
            AttendanceLog.objects.create(
                device=device,
                user_id=emp.user_id,
                timestamp=timezone.make_aware(check_out, tz),
                status=1,
                punch=1,
                verify_mode=1,
            )
            log_count += 2

    print(f"✅ Created {log_count} attendance logs")

    print("\n" + "=" * 60)
    print("🎉 Database seeded successfully!")
    print("=" * 60)
    print("\nSummary:")
    print(f"  - Companies: {Company.objects.count()}")
    print(f"  - Departments: {Department.objects.count()}")
    print(f"  - Positions: {Position.objects.count()}")
    print(f"  - Employees: {Employee.objects.count()}")
    print(f"  - Devices: {Device.objects.count()}")
    print(f"  - Timetables: {Timetable.objects.count()}")
    print(f"  - Shifts: {Shift.objects.count()}")
    print(f"  - EmployeeShifts: {EmployeeShift.objects.count()}")
    print(f"  - AttendanceLogs: {AttendanceLog.objects.count()}")

if __name__ == "__main__":
    seed()
