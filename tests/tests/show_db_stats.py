
import sys
import os
from sqlalchemy import text

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import SessionLocal
from backend import models

def show_stats():
    db = SessionLocal()
    try:
        print("📊 Database Persistence Check:")
        
        # 1. Inputs (Mock Data)
        emp_count = db.query(models.Employee).count()
        log_count = db.query(models.AttendanceLog).count()
        
        print(f"   - Inputs:")
        print(f"     ✅ Employees: {emp_count} (Saved in 'employees')")
        print(f"     ✅ Logs: {log_count} (Saved in 'attendance_logs')")
        
        # 2. Outputs (Calculation Results)
        daily_count = db.query(models.DailyAttendance).count()
        print(f"   - Outputs:")
        if daily_count > 0:
            print(f"     ✅ Calculated Daily Reports: {daily_count} (Saved in 'att_daily_attendance')")
        else:
            print(f"     ⚠️ Calculated Daily Reports: 0 (Run calculation first!)")

        # 3. Sample
        if daily_count > 0:
            last = db.query(models.DailyAttendance).order_by(models.DailyAttendance.id.desc()).first()
            print(f"\n   📝 Last Saved Calculation Record (ID: {last.id}):")
            print(f"      Employee: {last.employee.name}")
            print(f"      Date: {last.date}")
            print(f"      Status: {last.status}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    show_stats()
