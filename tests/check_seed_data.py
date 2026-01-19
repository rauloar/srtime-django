
import sys
import os
from datetime import date

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import SessionLocal
from backend import models

def check_data():
    db = SessionLocal()
    try:
        emp_count = db.query(models.Employee).count()
        log_count = db.query(models.AttendanceLog).count()
        shift_count = db.query(models.Shift).count()
        
        print(f"Employees: {emp_count}")
        print(f"Logs: {log_count}")
        print(f"Shifts: {shift_count}")
        
        if emp_count == 4 and log_count > 0:
            print("✅ Data seems to be seeded correctly.")
            
            # Show a sample log
            log = db.query(models.AttendanceLog).first()
            print(f"Sample Log: {log.timestamp} User: {log.user_id} Status: {log.status}")
            
        else:
            print("❌ Data counts do not match expected seed values.")
            
    except Exception as e:
        print(f"Error checking data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_data()
