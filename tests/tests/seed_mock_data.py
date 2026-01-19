
import sys
import os
import random
from datetime import datetime, timedelta, date, time

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import SessionLocal, engine, Base
from backend import models

def seed_data():
    db = SessionLocal()
    
    print("🧹 Cleaning up old mock data...")
    # Optional: Clear tables or just delete specific IDs if they exist
    # For a clean test, let's truncate/delete relevant data
    try:
        db.query(models.DailyAttendance).delete()
        db.query(models.AttendanceLog).delete()
        db.query(models.EmployeeShift).delete()
        db.query(models.ShiftTimetable).delete()
        db.query(models.Shift).delete()
        db.query(models.Timetable).delete()
        db.query(models.Employee).delete() # Be careful if real data exists
        db.query(models.Department).delete()
        db.commit()
    except Exception as e:
        print(f"Warning cleaning data: {e}")
        db.rollback()

    print("🌱 Seeding Departments...")
    dept = models.Department(id=1, name="Operaciones")
    db.add(dept)
    db.commit()

    print("🌱 Seeding Timetables...")
    tt_morning = models.Timetable(name="Morning (08-14)", on_duty_time="08:00", off_duty_time="14:00", late_allow_minutes=10, early_leave_allow_minutes=10)
    tt_afternoon = models.Timetable(name="Afternoon (14-18)", on_duty_time="14:00", off_duty_time="18:00", late_allow_minutes=5)
    tt_weekend = models.Timetable(name="Weekend (09-18)", on_duty_time="09:00", off_duty_time="18:00")
    tt_flexible = models.Timetable(name="Flexible (24h)", on_duty_time="00:00", off_duty_time="23:59")
    
    db.add_all([tt_morning, tt_afternoon, tt_weekend, tt_flexible])
    db.commit()

    print("🌱 Seeding Shifts...")
    # 1. Morning Shift (Mon-Fri)
    shift_morning = models.Shift(name="Turno Mañana")
    db.add(shift_morning)
    db.commit()
    for i in range(0, 5): # Mon-Fri
        db.add(models.ShiftTimetable(shift_id=shift_morning.id, timetable_id=tt_morning.id, day_index=i))
    
    # 2. Afternoon Shift (Mon-Fri)
    shift_afternoon = models.Shift(name="Turno Tarde")
    db.add(shift_afternoon)
    db.commit()
    for i in range(0, 5):
        db.add(models.ShiftTimetable(shift_id=shift_afternoon.id, timetable_id=tt_afternoon.id, day_index=i))

    # 3. Weekend Shift (Sat-Sun)
    shift_weekend = models.Shift(name="Turno Finde")
    db.add(shift_weekend)
    db.commit()
    for i in [5, 6]: # Sat, Sun
        db.add(models.ShiftTimetable(shift_id=shift_weekend.id, timetable_id=tt_weekend.id, day_index=i))

    # 4. Flexible Shift (Mon-Sun)
    shift_flexible = models.Shift(name="Turno Libre")
    db.add(shift_flexible)
    db.commit()
    for i in range(0, 7):
        db.add(models.ShiftTimetable(shift_id=shift_flexible.id, timetable_id=tt_flexible.id, day_index=i))
    
    db.commit()

    print("🌱 Seeding Employees and Assignments...")
    
    employees = [
        {"name": "Juan Mañana", "uid": "101", "shift": shift_morning, "fn": lambda d: ("07:55", "14:05") if d.weekday() < 5 else None},
        {"name": "Pedro Tarde", "uid": "102", "shift": shift_afternoon, "fn": lambda d: ("14:00", "18:00") if d.weekday() < 5 else None},
        {"name": "Lucas Finde", "uid": "103", "shift": shift_weekend, "fn": lambda d: ("08:50", "18:10") if d.weekday() >= 5 else None},
        {"name": "Maria Flexible", "uid": "104", "shift": shift_flexible, "fn": lambda d: ("09:00", "15:00") if d.day % 2 == 0 else ("10:00", "19:00")}, # Alternating hours
    ]

    for e_data in employees:
        emp = models.Employee(
            user_id=e_data["uid"], 
            name=e_data["name"], 
            department_id=1,
            active=True
        )
        db.add(emp)
        db.commit() # Commit to get ID
        
        # Assign Shift
        assign = models.EmployeeShift(
            employee_id=emp.id,
            shift_id=e_data["shift"].id,
            start_date=date(2025, 12, 1),
            end_date=date(2025, 12, 31)
        )
        db.add(assign)
        
        # Determine Device ID (Mock Device)
        device_id = 1 

        # Generate Logs
        # 1 Dec to 20 Dec
        start_date = date(2025, 12, 1)
        end_date = date(2025, 12, 20)
        delta = end_date - start_date
        
        for i in range(delta.days + 1):
            curr_date = start_date + timedelta(days=i)
            times = e_data["fn"](curr_date)
            
            if times:
                ts_in = datetime.combine(curr_date, datetime.strptime(times[0], "%H:%M").time())
                ts_out = datetime.combine(curr_date, datetime.strptime(times[1], "%H:%M").time())
                
                # Check In
                db.add(models.AttendanceLog(
                    device_id=device_id,
                    user_id=e_data["uid"],
                    timestamp=ts_in,
                    status=0, # Check In
                    punch=0
                ))
                
                # Check Out
                db.add(models.AttendanceLog(
                    device_id=device_id,
                    user_id=e_data["uid"],
                    timestamp=ts_out,
                    status=1, # Check Out
                    punch=1
                ))
        
        print(f"   Created {e_data['name']} with logs.")

    db.commit()
    print("✅ Seed Complete!")

if __name__ == "__main__":
    seed_data()
