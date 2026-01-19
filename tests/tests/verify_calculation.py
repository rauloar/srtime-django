
import requests
import json
from datetime import datetime, timedelta
import os

try:
    from backend.database import settings
    BASE_URL = os.getenv("BACKEND_URL", f"http://localhost:{settings.API_PORT}")
except Exception:
    BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8001")

def test_calculation():
    print("Testing Calculation Engine...")
    
    # 1. Trigger Calculation
    start_date = "2025-12-01"
    end_date = "2025-12-20"
    
    print(f"Calculating from {start_date} to {end_date}...")
    res = requests.post(f"{BASE_URL}/attendance/calculate", params={
        "start_date": start_date,
        "end_date": end_date
    })
    
    if res.status_code == 200:
        print("✅ Calculation Triggered:", res.json())
    else:
        print("❌ Calculation Failed:", res.text)
        return

    # 2. Fetch Reports
    print("Fetching Daily Reports...")
    res = requests.get(f"{BASE_URL}/attendance/reports/daily", params={
        "from_date": start_date,
        "to_date": end_date
    })
    
    if res.status_code == 200:
        data = res.json()
        print(f"✅ Fetched {len(data)} records")
        
        # Group by employee to check coverage
        counts = {}
        for r in data:
            emp_name = r['employee']['name']
            counts[emp_name] = counts.get(emp_name, 0) + 1
            
        print("Records per employee:", counts)
        
        # Sample for each user
        seen = []
        for r in data:
            if r['employee']['name'] not in seen:
                print(f"\nSample for {r['employee']['name']} ({r['date']}):")
                print(f"  In: {r['check_in']} | Out: {r['check_out']}")
                print(f"  Status: {r['status']}")
                print(f"  Worked: {r['worked_minutes']} mins")
                seen.append(r['employee']['name'])
                
    else:
        print("❌ Fetch Failed:", res.text)

if __name__ == "__main__":
    test_calculation()
