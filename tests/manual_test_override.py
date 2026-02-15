
import sys
import os
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.database import settings
from backend import models
from backend.services.attendance_engine import resolve_schedule, calculate_day

def test_override():
    print(f"Connecting to: {settings.DB_URL}")
    engine = create_engine(settings.DB_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Setup Data for Employee 1 (Ana Lopez)
        emp = db.query(models.Employee).filter(models.Employee.user_id == '1').first()
        target_date = date(2025, 12, 15) # Assuming Dec 15 has a normal shift
        
        print(f"Testing for Emp: {emp.name} on {target_date}")
        
        # 2. Check Normal Resolution
        ctx = resolve_schedule(db, emp.id, target_date)
        if ctx:
            print(f"Normal Context: Source={ctx.source}, Timetable={ctx.timetable.name}")
        else:
            print("No Normal Schedule Found.")
            
        # 3. Create Override (Use different timetable if possible)
        # Find another timetable
        other_tt = db.query(models.Timetable).filter(models.Timetable.id != ctx.timetable.id).first()
        if not other_tt:
            print("Need at least 2 timetables to test override.")
            return

        print(f"Creating Override: Force {other_tt.name}")
        
        override = models.ScheduleOverride(
            employee_id=emp.id,
            date=target_date,
            timetable_id=other_tt.id
        )
        db.add(override)
        db.commit()
        
        # 4. Check Resolution Again
        new_ctx = resolve_schedule(db, emp.id, target_date)
        if new_ctx:
             print(f"Override Context: Source={new_ctx.source}, Timetable={new_ctx.timetable.name}")
             if new_ctx.source == "OVERRIDE" and new_ctx.timetable.id == other_tt.id:
                 print("PASS: Override logic worked.")
             else:
                 print("FAIL: Override logic failed.")
        
        # 5. Check Calculate Day
        daily = calculate_day(db, emp.id, target_date)
        print(f"Daily Schedule Type: {daily.schedule_type}")
        if daily.schedule_type == "OVERRIDE":
            print("PASS: DailyAttendance updated correctly.")
        else:
            print("FAIL: DailyAttendance type incorrect.")

        # Cleanup
        db.delete(override)
        db.commit()
        print("Cleanup done.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_override()
