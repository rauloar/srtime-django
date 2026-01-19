import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.database import SessionLocal, engine, Base
from backend import models

db = SessionLocal()

print("Cleaning up Schedules...")
try:
    # Order matters for foreign keys
    print("Deleting EmployeeShifts...")
    db.query(models.EmployeeShift).delete()
    db.commit()
    
    print("Deleting ShiftTimetables...")
    db.query(models.ShiftTimetable).delete()
    db.commit()
    
    print("Deleting Shifts...")
    db.query(models.Shift).delete()
    db.commit()
    
    print("Deleting Timetables...")
    db.query(models.Timetable).delete()
    db.commit()
    print("Cleanup successful.")
except Exception as e:
    print(f"Error cleaning: {e}")
    db.rollback()
finally:
    db.close()
