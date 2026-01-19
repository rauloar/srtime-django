
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.database import settings
from backend import models

def check_leaves():
    print(f"Connecting to: {settings.DB_URL}")
    engine = create_engine(settings.DB_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        count = db.query(models.Leave).count()
        print(f"Total Leaves (Absences): {count}")
        
        if count > 0:
            leaves = db.query(models.Leave).all()
            for l in leaves:
                print(f" - Emp {l.employee_id}: {l.leave_type} ({l.start_time} - {l.end_time})")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_leaves()
