
import requests
import datetime
import sys

import os
try:
    from backend.database import settings
    BASE_URL = os.getenv("BACKEND_URL", f"http://localhost:{settings.API_PORT}")
except Exception:
    BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8001")

def verify_schedules():
    print("Testing Schedule Matrix API...")
    
    # 1. Create Timetables
    print("Creating Timetables...")
    tt1 = requests.post(f"{BASE_URL}/schedules/timetables/", json={
        "name": "Morning", "on_duty_time": "08:00", "off_duty_time": "16:00"
    }).json()
    
    tt2 = requests.post(f"{BASE_URL}/schedules/timetables/", json={
        "name": "Afternoon", "on_duty_time": "16:00", "off_duty_time": "00:00"
    }).json()
    print(f"✅ Created Timetables: {tt1['name']}, {tt2['name']}")

    # 2. Create Shift
    print("Creating Shift...")
    shift = requests.post(f"{BASE_URL}/schedules/shifts/", json={"name": "Weekly Rotate"}).json()
    shift_id = shift['id']
    print(f"✅ Created Shift: {shift['name']} (ID: {shift_id})")

    # 3. Configure Shift Cycle (Mon-Fri)
    print("Configuring Cycle...")
    cycle_data = [
        {"timetable_id": tt1['id'], "day_index": i} for i in range(5) # 0-4 (Mon-Fri)
    ]
    r = requests.post(f"{BASE_URL}/schedules/shifts/{shift_id}/timetables", json=cycle_data)
    if r.status_code == 200:
        print("✅ Cycle Configured")
    else:
        print(f"❌ Cycle Config Failed: {r.text}")

    # 4. Assign to Employee (Need an employee)
    # Get first employee
    emps = requests.get(f"{BASE_URL}/employees/").json()
    if not emps:
        print("Creating dummy employee...")
        dept = requests.post(f"{BASE_URL}/departments/", json={"name": "Temp Dept"}).json()
        emp = requests.post(f"{BASE_URL}/employees/", json={
            "user_id": "9998", "name": "Schedule Test User", "department_id": dept['id']
        }).json()
    else:
        emp = emps[0]
    
    print(f"Assigning to Employee {emp['name']} (ID: {emp['id']})...")
    
    today = datetime.date.today()
    start = today.isoformat()
    end = (today + datetime.timedelta(days=30)).isoformat()
    
    r = requests.post(f"{BASE_URL}/schedules/assign/", json={
        "employee_id": emp['id'],
        "shift_id": shift_id,
        "start_date": start,
        "end_date": end
    })
    
    if r.status_code == 200:
        print("✅ Assignment Created")
    else:
        print(f"❌ Assignment Failed: {r.text}")
        
    # 5. Verify Assignment List
    print("Verifying List...")
    r = requests.get(f"{BASE_URL}/schedules/assignments/?start_date={start}&end_date={end}")
    assignments = r.json()
    found = any(a['employee_id'] == emp['id'] and a['shift_id'] == shift_id for a in assignments)
    
    if found:
        print(f"✅ Assignment found in list! Total: {len(assignments)}")
    else:
        print(f"❌ Assignment NOT found in list. Response: {assignments}")

if __name__ == "__main__":
    verify_schedules()
