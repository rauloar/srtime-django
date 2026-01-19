import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.database import SessionLocal, engine, Base
from backend import models

db = SessionLocal()

print("--- Database Counts ---")
try:
    print(f"Companies: {db.query(models.Company).count()}")
    print(f"Departments: {db.query(models.Department).count()}")
    print(f"Employees: {db.query(models.Employee).count()}")
    print(f"Users: {db.query(models.User).count()}")
    print(f"Timetables: {db.query(models.Timetable).count()}")
    print(f"Shifts: {db.query(models.Shift).count()}")
    print(f"EmployeeShifts: {db.query(models.EmployeeShift).count()}")
    print(f"AttendanceLogs: {db.query(models.AttendanceLog).count()}")
except Exception as e:
    print(f"Error checking counts: {e}")
finally:
    db.close()
