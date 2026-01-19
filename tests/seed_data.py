import sys
import os
import random
from datetime import datetime, timedelta, date

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import SessionLocal, engine, Base
from backend import models

# Init DB
Base.metadata.create_all(bind=engine)
db = SessionLocal()

def seed():
    print("Seeding database...")

    # 1. Company
    if not db.query(models.Company).first():
        print("Creating Company...")
        company = models.Company(
            name="ZK Teco Demo Corp",
            code="ZK001",
            address="123 Tech Park",
            website="www.zkteco.com"
        )
        db.add(company)
    
    # 2. Departments
    depts = ["Recursos Humanos", "Desarrollo", "Ventas", "Soporte"]
    db_depts = []
    for d_name in depts:
        d = db.query(models.Department).filter_by(name=d_name).first()
        if not d:
            d = models.Department(name=d_name, code=d_name[:3].upper())
            db.add(d)
            db.commit() # Commit to get ID
            db.refresh(d)
        db_depts.append(d)

    # 3. Devices
    device = db.query(models.Device).first()
    if not device:
        print("Creating Mock Device...")
        device = models.Device(
            name="Puerta Principal",
            ip="192.168.1.201",
            port=4370,
            enabled=True,
            device_name="iClock S880",
            serialnumber="SN882233"
        )
        db.add(device)
        db.commit()
    db.refresh(device)

    # 4. Employees & Users
    names = ["Juan Perez", "Maria Garcia", "Carlos Lopez", "Ana Martinez", "Luis Rodriguez"]
    employees = []
    
    for i, name in enumerate(names):
        uid = i + 1
        user_id = str(1000 + i)
        
        # User
        # Check by Unique Constraint (device_id, uid) to avoid 1062 Duplicate entry
        user = db.query(models.User).filter_by(device_id=device.id, uid=uid).first()
        if not user:
            # Also check if user_id (string) is used to avoid confusion?
            # Ideally uid is the physical key.
            print(f"Creating user {name}...")
            user = models.User(
                device_id=device.id,
                uid=uid,
                name=name,
                privilege=0,
                user_id=user_id,
                card=str(556600+i)
            )
            db.add(user)
            db.commit() # Commit each user to be safe or flush
        
        # Employee
        emp = db.query(models.Employee).filter_by(user_id=user_id).first()
        if not emp:
            emp = models.Employee(
                user_id=user_id,
                name=name,
                department_id=random.choice(db_depts).id,
                email=f"{name.split()[0].lower()}@demo.com",
                active=True
            )
            db.add(emp)
            db.commit()
        # Re-fetch to ensure we have the instance linked to session
        if emp not in db: emp = db.query(models.Employee).filter_by(user_id=user_id).first()
        employees.append(emp)
    
    db.commit()

    # 5. Timetables (Horarios)
    # 5. Timetables (Horarios)
    timetables_data = [
        {"name": "Tm_Morn_06-14", "on": "06:00", "off": "14:00", "flex": False},
        {"name": "Tm_Aft_14-22", "on": "14:00", "off": "22:00", "flex": False},
        {"name": "Tm_Night_22-06", "on": "22:00", "off": "06:00", "flex": False},
        {"name": "Tm_Flex", "on": "09:00", "off": "18:00", "flex": True}
    ]
    
    created_tts = {}
    print("Creating Timetables...")
    for tt_data in timetables_data:
        try:
            tt = db.query(models.Timetable).filter_by(name=tt_data["name"]).first()
            if not tt:
                tt = models.Timetable(
                    name=tt_data["name"],
                    on_duty_time=tt_data["on"],
                    off_duty_time=tt_data["off"],
                    check_in_start="05:00" if "Morn" in tt_data["name"] else "13:00" if "Aft" in tt_data["name"] else "20:00" if "Night" in tt_data["name"] else "00:00",
                    check_in_end="10:00" if "Morn" in tt_data["name"] else "18:00" if "Aft" in tt_data["name"] else "23:59" if "Night" in tt_data["name"] else "23:59",
                    check_out_start="10:00" if "Morn" in tt_data["name"] else "18:00" if "Aft" in tt_data["name"] else "03:00" if "Night" in tt_data["name"] else "00:00",
                    check_out_end="18:00" if "Morn" in tt_data["name"] else "23:59" if "Aft" in tt_data["name"] else "09:00" if "Night" in tt_data["name"] else "23:59",
                    late_allow_minutes=15,
                    early_leave_allow_minutes=15,
                    work_days=1,
                    is_flexible=tt_data["flex"]
                )
                db.add(tt)
                db.commit() # Commit immediately
                db.refresh(tt)
            created_tts[tt_data["name"]] = tt
        except Exception as e:
            print(f"Error creating TT {tt_data['name']}: {e}")
            db.rollback()

    # 6. Shifts (Turnos)
    shifts_map = {
        "Shift_Morning": "Tm_Morn_06-14",
        "Shift_Afternoon": "Tm_Aft_14-22",
        "Shift_Night": "Tm_Night_22-06",
        "Shift_Flex": "Tm_Flex"
    }
    
    created_shifts = {}
    print("Creating Shifts...")
    for s_name, tt_name in shifts_map.items():
        try:
            shift = db.query(models.Shift).filter_by(name=s_name).first()
            if not shift:
                shift = models.Shift(name=s_name)
                db.add(shift)
                db.commit()
                db.refresh(shift)
                
                # Add Cycle
                tt = created_tts.get(tt_name)
                if tt:
                    for day in range(7): 
                        st = models.ShiftTimetable(shift_id=shift.id, timetable_id=tt.id, day_index=day)
                        db.add(st)
                    db.commit()
            created_shifts[s_name] = shift
        except Exception as e:
            print(f"Error creating Shift {s_name}: {e}")
            db.rollback()

    # 7. Assign Shifts (Dec 1-31 2025)
    # Strategy: 
    # Emp 0 (Juan) -> Morning
    # Emp 1 (Maria) -> Afternoon
    # Emp 2 (Carlos) -> Night
    # Emp 3 (Ana) -> Flex
    # Emp 4 (Luis) -> Morning
    start_date = date(2025, 12, 1)
    end_date = date(2025, 12, 31)
    
    emp_assignments = {} # emp_id -> type ("Morn", "Aft", "Night", "Flex")

    for i, emp in enumerate(employees):
        shift_key = "Shift_Morning" # Default
        atype = "Morn"
        
        if i == 1: 
            shift_key = "Shift_Afternoon"
            atype = "Aft"
        elif i == 2:
            shift_key = "Shift_Night"
            atype = "Night"
        elif i == 3:
            shift_key = "Shift_Flex"
            atype = "Flex"
            
        target_shift = created_shifts[shift_key]
        emp_assignments[emp.id] = atype
        
        try:
            # Delete old assignment for clean slate for this month
            db.query(models.EmployeeShift).filter_by(employee_id=emp.id).delete()
            db.commit()
            
            assign = models.EmployeeShift(
                employee_id=emp.id,
                shift_id=target_shift.id,
                start_date=start_date,
                end_date=end_date
            )
            db.add(assign)
            db.commit()
        except Exception as e:
            print(f"Error assigning shift to {emp.name}: {e}")
            db.rollback()

    # 8. Generate Attendance Logs (Dec 1-22 2025)
    print("Generating logs for new schedules...")
    
    try:
        db.query(models.AttendanceLog).filter(models.AttendanceLog.timestamp >= datetime(2025, 12, 1)).delete(synchronize_session=False)
        db.commit()
    except:
        db.rollback()

    log_count = 0
    current_day = date(2025, 12, 1)
    target_day = date(2025, 12, 22)
    
    while current_day <= target_day:
        if current_day.weekday() < 6: # Mon-Sat (Include Sat for variety)
            for emp in employees:
                atype = emp_assignments.get(emp.id, "Morn")
                
                # Randomized presence (90%)
                if random.random() > 0.1:
                    logs_to_add = []
                    
                    if atype == "Morn":
                        # 06:00 - 14:00
                        in_t = datetime.combine(current_day, datetime.strptime("06:00", "%H:%M").time()) + timedelta(minutes=random.randint(-10, 15))
                        out_t = datetime.combine(current_day, datetime.strptime("14:00", "%H:%M").time()) + timedelta(minutes=random.randint(-5, 30))
                        logs_to_add.append((in_t, 0))
                        logs_to_add.append((out_t, 1))

                    elif atype == "Aft":
                        # 14:00 - 22:00
                        in_t = datetime.combine(current_day, datetime.strptime("14:00", "%H:%M").time()) + timedelta(minutes=random.randint(-10, 10))
                        out_t = datetime.combine(current_day, datetime.strptime("22:00", "%H:%M").time()) + timedelta(minutes=random.randint(0, 20))
                        logs_to_add.append((in_t, 0))
                        logs_to_add.append((out_t, 1))

                    elif atype == "Night":
                        # 22:00 - 06:00 (Next Day)
                        in_t = datetime.combine(current_day, datetime.strptime("22:00", "%H:%M").time()) + timedelta(minutes=random.randint(-15, 5))
                        # Out is next day
                        next_day = current_day + timedelta(days=1)
                        out_t = datetime.combine(next_day, datetime.strptime("06:00", "%H:%M").time()) + timedelta(minutes=random.randint(-5, 10))
                        logs_to_add.append((in_t, 0))
                        logs_to_add.append((out_t, 1))

                    elif atype == "Flex":
                        # Two chunks: ~09-13 and ~14-18
                        # Chunk 1
                        t1_in = datetime.combine(current_day, datetime.strptime("09:00", "%H:%M").time()) + timedelta(minutes=random.randint(-30, 30))
                        t1_out = datetime.combine(current_day, datetime.strptime("13:00", "%H:%M").time()) + timedelta(minutes=random.randint(-10, 10))
                        # Chunk 2
                        t2_in = datetime.combine(current_day, datetime.strptime("14:00", "%H:%M").time()) + timedelta(minutes=random.randint(-10, 10))
                        t2_out = datetime.combine(current_day, datetime.strptime("18:00", "%H:%M").time()) + timedelta(minutes=random.randint(-20, 40))
                        
                        logs_to_add.append((t1_in, 0))
                        logs_to_add.append((t1_out, 1))
                        logs_to_add.append((t2_in, 0))
                        logs_to_add.append((t2_out, 1))
                    
                    try:
                        for timestamp, state in logs_to_add:
                            log = models.AttendanceLog(
                                device_id=device.id,
                                user_id=emp.user_id,
                                timestamp=timestamp,
                                status=state,
                                punch=state,
                                verify_mode=1,
                                raw_json={}
                            )
                            db.add(log)
                            log_count += 1
                        db.commit()
                    except Exception as e:
                        db.rollback()
                        
        current_day += timedelta(days=1)

    print(f"Seeding complete! {log_count} logs generated.")
    db.close()

if __name__ == "__main__":
    try:
        seed()
    except Exception as e:
        print(f"Error seeding: {e}")
