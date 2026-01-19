
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.database import settings
from backend import models

def check_db_status():
    print(f"Connecting to: {settings.DB_URL}")
    engine = create_engine(settings.DB_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Check Devices
        devices = db.query(models.Device).all()
        print(f"Devices found: {len(devices)}")
        for d in devices:
            print(f" - ID: {d.id}, Name: {d.name}, Enabled: {d.enabled}")
            
        # Check Attendance Logs
        log_count = db.query(models.AttendanceLog).count()
        print(f"Total AttendanceLogs: {log_count}")
        
        # Check Daily Attendance
        daily_count = db.query(models.DailyAttendance).count()
        print(f"Total DailyAttendance: {daily_count}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_db_status()
