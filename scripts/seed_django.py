"""
Script para poblar la base de datos con datos de prueba
Adaptado de ZKTimeWeb/tests/seed_data.py para Django
"""
import sys
import os
import random
from datetime import datetime, timedelta, date
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import (
    Company, Department, Employee, Device, User,
    Timetable, Shift, ShiftTimetable, EmployeeShift,
    AttendanceLog, Zone, Position
)

def seed():
    print("🌱 Seeding database...")

    # 1. Company
    if not Company.objects.exists():
        print("Creating Company...")
        company = Company.objects.create(
            name="SR Time Demo Corp",
            code="SR001",
            address="123 Tech Park",
            website="www.srtime.com"
        )
    else:
        company = Company.objects.first()
    
    # 2. Zones
    zones_data = ["Administración", "Producción", "Ventas"]
    zones = []
    for z_name in zones_data:
        zone, created = Zone.objects.get_or_create(name=z_name)
        zones.append(zone)
    
    # 3. Positions
    positions_data = ["Gerente", "Analista", "Técnico", "Asistente"]
    positions = []
    for p_name in positions_data:
        position, created = Position.objects.get_or_create(name=p_name)
        positions.append(position)
    
    # 4. Departments
    depts_data = ["Recursos Humanos", "Desarrollo", "Ventas", "Soporte"]
    db_depts = []
    for d_name in depts_data:
        dept, created = Department.objects.get_or_create(
            name=d_name,
            defaults={'code': d_name[:3].upper()}
        )
        db_depts.append(dept)

    # 5. Devices
    device, created = Device.objects.get_or_create(
        ip="192.168.1.201",
        defaults={
            'name': "Puerta Principal",
            'port': 4370,
            'enabled': True,
            'device_name': "iClock S880",
            'serialnumber': "SN882233",
            'zone_rel': random.choice(zones) if zones else None
        }
    )

    # 6. Employees & Users
    names = ["Juan Perez", "Maria Garcia", "Carlos Lopez", "Ana Martinez", "Luis Rodriguez"]
    employees = []
    
    for i, name in enumerate(names):
        uid = i + 1
        user_id = str(1000 + i)
        
        # User (biometric user from device)
        user, created = User.objects.get_or_create(
            device=device,
            uid=uid,
            defaults={
                'name': name,
                'privilege': 0,
                'user_id': user_id,
                'card': str(556600+i)
            }
        )
        
        # Employee
        emp, created = Employee.objects.get_or_create(
            user_id=user_id,
            defaults={
                'name': name,
                'department': random.choice(db_depts),
                'position': random.choice(positions) if positions else None,
                'email': f"{name.split()[0].lower()}@demo.com",
                'phone': f"+57 300 {random.randint(100, 999)} {random.randint(1000, 9999)}",
                'mobile_phone': f"+57 310 {random.randint(100, 999)} {random.randint(1000, 9999)}",
                'country': "Colombia",
                'birthday': date(1990 + i, random.randint(1, 12), random.randint(1, 28)),
                'active': True
            }
        )
        employees.append(emp)
    
    print(f"✅ Created {len(employees)} employees")

    # 7. Timetables (Horarios)
    timetables_data = [
        {"name": "Tm_Morn_06-14", "on": "06:00", "off": "14:00", "flex": False},
        {"name": "Tm_Aft_14-22", "on": "14:00", "off": "22:00", "flex": False},
        {"name": "Tm_Night_22-06", "on": "22:00", "off": "06:00", "flex": False},
        {"name": "Tm_Flex", "on": "09:00", "off": "18:00", "flex": True}
    ]
    
    created_tts = {}
    print("Creating Timetables...")
    for tt_data in timetables_data:
        tt, created = Timetable.objects.get_or_create(
            name=tt_data["name"],
            defaults={
                'on_duty_time': tt_data["on"],
                'off_duty_time': tt_data["off"],
                'check_in_start': "05:00" if "Morn" in tt_data["name"] else "13:00" if "Aft" in tt_data["name"] else "20:00" if "Night" in tt_data["name"] else "00:00",
                'check_in_end': "10:00" if "Morn" in tt_data["name"] else "18:00" if "Aft" in tt_data["name"] else "23:59" if "Night" in tt_data["name"] else "23:59",
                'check_out_start': "10:00" if "Morn" in tt_data["name"] else "18:00" if "Aft" in tt_data["name"] else "03:00" if "Night" in tt_data["name"] else "00:00",
                'check_out_end': "18:00" if "Morn" in tt_data["name"] else "23:59" if "Aft" in tt_data["name"] else "09:00" if "Night" in tt_data["name"] else "23:59",
                'late_allow_minutes': 15,
                'early_leave_allow_minutes': 15,
                'work_days': 1,
                'is_flexible': tt_data["flex"]
            }
        )
        created_tts[tt_data["name"]] = tt
    
    print(f"✅ Created {len(created_tts)} timetables")

    # 8. Shifts (Turnos) con horarios para cada día
    shifts_map = {
        "Shift_Morning": "Tm_Morn_06-14",
        "Shift_Afternoon": "Tm_Aft_14-22",
        "Shift_Night": "Tm_Night_22-06",
        "Shift_Flex": "Tm_Flex"
    }
    
    created_shifts = {}
    print("Creating Shifts...")
    for s_name, tt_name in shifts_map.items():
        tt = created_tts.get(tt_name)
        if not tt:
            continue
        
        shift, created = Shift.objects.get_or_create(name=s_name)
        created_shifts[s_name] = shift
        
        # Crear ShiftTimetables para cada día de la semana
        for day_idx in range(7):  # 0=Lunes, 6=Domingo
            ShiftTimetable.objects.get_or_create(
                shift=shift,
                day_index=day_idx,
                defaults={'timetable': tt}
            )
    
    print(f"✅ Created {len(created_shifts)} shifts")

    # 9. Asignar turnos a empleados
    print("Assigning shifts to employees...")
    shift_list = list(created_shifts.values())
    if shift_list and employees:
        for emp in employees:
            # Asignar turno aleatorio con scope EMPLOYEE
            shift = random.choice(shift_list)
            EmployeeShift.objects.get_or_create(
                scope='EMPLOYEE',
                employee=emp,
                shift=shift,
                defaults={'start_date': date.today()}
            )
    
    # 10. Crear logs de asistencia de prueba (últimos 7 días)
    print("Creating sample attendance logs...")
    log_count = 0
    for emp in employees:
        user_id = emp.user_id
        for days_ago in range(7, 0, -1):
            log_date = datetime.now() - timedelta(days=days_ago)
            # Entrada
            check_in = log_date.replace(hour=8, minute=random.randint(0, 30), second=0, microsecond=0)
            AttendanceLog.objects.get_or_create(
                device=device,
                user_id=user_id,
                timestamp=check_in,
                defaults={
                    'status': 0,
                    'punch': 0,
                    'verify_mode': 1
                }
            )
            log_count += 1
            
            # Salida
            check_out = log_date.replace(hour=17, minute=random.randint(0, 30), second=0, microsecond=0)
            AttendanceLog.objects.get_or_create(
                device=device,
                user_id=user_id,
                timestamp=check_out,
                defaults={
                    'status': 0,
                    'punch': 1,
                    'verify_mode': 1
                }
            )
            log_count += 1
    
    print(f"✅ Created {log_count} attendance logs")
    
    print("\n" + "="*60)
    print("🎉 Database seeded successfully!")
    print("="*60)
    print("\nSummary:")
    print(f"  - Companies: {Company.objects.count()}")
    print(f"  - Zones: {Zone.objects.count()}")
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
