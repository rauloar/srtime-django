import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.database import SessionLocal, engine, Base
from backend import models
from datetime import date, datetime, timedelta

# Drop and Recreate All Tables
print("RESETTING DATABASE FOR BIO TIME MOCK DATA")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# 1. Company
print("1. Creating Company...")
company = models.Company(id=1, name="TechSur SRL")
db.add(company)
db.commit()

# 2. Departments
print("2. Creating Departments...")
# Note: Ensure company_id is passsed if model has it
depts = [
    models.Department(id=1, name="Administracion", company_id=1, parent_id=None),
    models.Department(id=2, name="Produccion", company_id=1, parent_id=None),
    models.Department(id=3, name="Soporte Tecnico", company_id=1, parent_id=None)
]
db.add_all(depts)
db.commit()

# 3. Timetables
print("3. Creating Timetables...")

# Horario A - Admin
tt_admin = models.Timetable(
    name="Horario Administrativo",
    on_duty_time="08:00",
    off_duty_time="17:00",
    check_in_start="07:30",
    check_in_end="08:15",
    check_out_start="16:45",
    check_out_end="18:00",
    late_allow_minutes=5,
    early_leave_allow_minutes=5,
    break_minutes=60,
    rounding_rule="none",
    is_flexible=False
)

# Horario B - Produccion (06:00 - 14:00)
tt_prod_am = models.Timetable(
    name="Produccion Manana",
    on_duty_time="06:00",
    off_duty_time="14:00",
    check_in_start="05:30",
    check_in_end="06:10",
    check_out_start="13:50",
    check_out_end="14:30",
    late_allow_minutes=3,
    early_leave_allow_minutes=5,
    break_minutes=30,
    rounding_rule="5min",
    is_flexible=False
)

# Horario C - Flexible (09:00 - 18:00 nominal, but wide range)
tt_flex = models.Timetable(
    name="Soporte Flexible 8h",
    on_duty_time="09:00",
    off_duty_time="18:00",
    check_in_start="07:00",
    check_in_end="23:00", # Expanded to allow late IN
    check_out_start="07:00",
    check_out_end="23:00", # Expanded to allow early OUT (within reason) or late OUT
    required_minutes=480,
    break_minutes=30,
    rounding_rule="none",
    is_flexible=True
)

db.add(tt_admin)
db.add(tt_prod_am)
db.add(tt_flex)
db.commit()
db.refresh(tt_admin); db.refresh(tt_prod_am); db.refresh(tt_flex)

# 4. Shifts
print("4. Creating Shifts...")

s_admin = models.Shift(name="Turno Administrativo")
db.add(s_admin)
db.commit(); db.refresh(s_admin)
for i in range(7): # 7 days cycle usually? Or 5? Let's do 7 to cover weekends as Rest
    if i < 5: # Mon-Fri
        db.add(models.ShiftTimetable(shift_id=s_admin.id, timetable_id=tt_admin.id, day_index=i))
    else: 
        # Weekend - No Timetable ? or specific Rest Timetable? 
        # BioTime: No entry = Rest Day.
        pass

s_prod = models.Shift(name="Produccion Rotativo")
db.add(s_prod)
db.commit(); db.refresh(s_prod)
for i in range(5):
    db.add(models.ShiftTimetable(shift_id=s_prod.id, timetable_id=tt_prod_am.id, day_index=i))

s_sup = models.Shift(name="Soporte Flexible")
db.add(s_sup)
db.commit(); db.refresh(s_sup)
for i in range(5):
    db.add(models.ShiftTimetable(shift_id=s_sup.id, timetable_id=tt_flex.id, day_index=i))

db.commit()

# 5. Employees & Devices
print("5. Creating Devices and Employees...")

# Dummy Device
device = models.Device(name="Main Door", ip="192.168.1.201", port=4370)
db.add(device)
db.commit(); db.refresh(device)

users_data = [
    {"id": 1, "name": "Ana Lopez", "dept": 1, "shift": s_admin},
    {"id": 2, "name": "Carlos Mendez", "dept": 1, "shift": s_admin},
    {"id": 3, "name": "Laura Perez", "dept": 1, "shift": s_admin},
    {"id": 4, "name": "Juan Gomez", "dept": 2, "shift": s_prod},
    {"id": 5, "name": "Marcos Diaz", "dept": 2, "shift": s_prod},
    {"id": 6, "name": "Lucia Romero", "dept": 2, "shift": s_prod},
    {"id": 7, "name": "Sofia Torres", "dept": 3, "shift": s_sup},
    {"id": 8, "name": "Pedro Sanchez", "dept": 3, "shift": s_sup},
    {"id": 9, "name": "Valentina Rios", "dept": 3, "shift": s_sup},
    {"id": 10, "name": "Diego Fernandez", "dept": 3, "shift": s_sup}
]

for u in users_data:
    # User needs device_id
    user = models.User(
        uid=u["id"], 
        user_id=str(u["id"]), 
        name=u["name"], 
        privilege=0,
        device_id=device.id # Linked to device
    )
    db.add(user)
    db.commit(); db.refresh(user)
    
    emp = models.Employee(
        id=u["id"],
        name=u["name"],
        department_id=u["dept"],
        user_id=user.user_id # Link by user_id string
    )
    db.add(emp)
    db.commit()
    
    assign = models.EmployeeShift(
        employee_id=emp.id,
        shift_id=u["shift"].id,
        start_date=date(2025, 9, 1),
        end_date=None
    )
    db.add(assign)
db.commit()

# 7. Real Logs
print("7. Generating Real Logs for 2025-09-10...")

logs_data = [
    { "eid": 1, "t": "08:02:00", "s": 0 }, { "eid": 1, "t": "17:05:00", "s": 1 },
    { "eid": 2, "t": "08:20:00", "s": 0 }, { "eid": 2, "t": "17:00:00", "s": 1 },
    { "eid": 4, "t": "06:01:00", "s": 0 }, { "eid": 4, "t": "13:55:00", "s": 1 },
    { "eid": 7, "t": "09:12:00", "s": 0 }, { "eid": 7, "t": "18:00:00", "s": 1 },
    { "eid": 9, "t": "10:30:00", "s": 0 }, { "eid": 9, "t": "16:30:00", "s": 1 }
]

for log in logs_data:
    dt_str = f"2025-09-10 {log['t']}"
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    
    att_log = models.AttendanceLog(
        user_id=str(log["eid"]),
        device_id=device.id,
        timestamp=dt,
        punch=log["s"],
        status=log["s"],
        verify_mode=1,
        raw_json={}
    )
    db.add(att_log)
db.commit()

print("MOCK DATA SEEDED SUCCESSFULLY")
db.close()
