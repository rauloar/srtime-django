
import sys
import os
from datetime import date

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import SessionLocal
from backend.services import attendance_engine
from backend import models

def verify_logic():
    print("🔬 Verifying Logic Directly (No HTTP)...")
    db = SessionLocal()
    try:
        start_date = date(2025, 12, 1)
        end_date = date(2025, 12, 20)
        
        print(f"   Calculating {start_date} to {end_date}...")
        results = attendance_engine.calculate_period(db, start_date, end_date)
        
        print(f"✅ Calculation returned {len(results)} daily records.")
        
        # Check specific scenarios
        # 1. Juan Mañana (Morning Shift)
        juan_recs = [r for r in results if r.employee.name == "Juan Mañana"]
        print(f"   Juan Mañana records: {len(juan_recs)}")
        if juan_recs:
            sample = juan_recs[0]
            print(f"   Sample Juan: {sample.date} Status: {sample.status} Worked: {sample.worked_minutes}")
            
        # 2. Lucas Finde (Weekend)
        lucas_recs = [r for r in results if r.employee.name == "Lucas Finde"]
        print(f"   Lucas Finde records: {len(lucas_recs)}")
        # Check a Sunday
        sunday_rec = next((r for r in lucas_recs if r.date.weekday() == 6), None)
        if sunday_rec:
             print(f"   Lucas Sunday: {sunday_rec.date} Status: {sunday_rec.status} Worked: {sunday_rec.worked_minutes}")

    except Exception as e:
        print(f"❌ Logic Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_logic()
