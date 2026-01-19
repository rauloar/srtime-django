import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.database import SessionLocal
from backend.services.attendance_engine import calculate_day
from backend import models
from datetime import date

db = SessionLocal()

target_date = date(2025, 9, 10)
print(f"--- Verifying Calculation for {target_date} ---")

# Employees to check
# 1: Ana (Admin, Normal)
# 2: Carlos (Admin, Late)
# 4: Juan (Prod, Normal)
# 7: Sofia (Flex, Normal)
# 9: Valentina (Flex, Early/Partial)

check_list = [
    (1, "Ana Lopez", "Normal"),
    (2, "Carlos Mendez", "Late"),
    (4, "Juan Gomez", "Normal"),
    (7, "Sofia Torres", "Normal"),
    (9, "Valentina Rios", "Early/Partial")
]

for emp_id, name, expected in check_list:
    print(f"\nCalculating for {name} (ID {emp_id})...")
    res = calculate_day(db, emp_id, target_date)
    
    status = res.status if res else "No Result"
    worked = res.worked_minutes if res else 0
    in_t = res.check_in.strftime("%H:%M") if res and res.check_in else "None"
    out_t = res.check_out.strftime("%H:%M") if res and res.check_out else "None"
    
    print(f"  > Time: {in_t} - {out_t}")
    print(f"  > Worked: {worked} min")
    print(f"  > Status: {status}")
    print(f"  > Expected: {expected}")
    
    match = expected in status if expected != "Normal" else status == "Normal"
    # Looser match for combos
    
    if match:
        print("  ✅ MATCH")
    else:
        print("  ❌ MISMATCH")

db.close()
