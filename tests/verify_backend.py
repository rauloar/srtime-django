
import sys
import os
import requests
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Base URL (env BACKEND_URL or backend.settings.API_PORT; fallback 8001)
try:
    from backend.database import settings
    BASE_URL = os.getenv("BACKEND_URL", f"http://localhost:{settings.API_PORT}")
except Exception:
    BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8001")

def test_health():
    print(f"Testing Health Check...")
    try:
        r = requests.get(f"{BASE_URL}/")
        if r.status_code == 200:
            print("✅ Health Check Passed")
        else:
            print(f"❌ Health Check Failed: {r.status_code}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")

def test_devices():
    print(f"\nTesting Devices Endpoints...")
    # Create Device
    device_data = {
        "name": "Test Device",
        "ip": "192.168.1.201",
        "port": 4370
    }
    r = requests.post(f"{BASE_URL}/devices/", json=device_data)
    if r.status_code == 200:
        device = r.json()
        print(f"✅ Device Created: ID {device['id']}")
        return device['id']
    else:
        print(f"❌ Device Creation Failed: {r.text}")
        return None

def test_connection_logic(device_id):
    print(f"\nTesting Connection Logic (Mocked Device)...")
    # This triggers the pyzk logic in a background task. 
    # Since we don't have a real device, it will eventually fail or timeout in the background.
    # But we check if the endpoint accepts the request.
    r = requests.post(f"{BASE_URL}/devices/{device_id}/test-connection")
    if r.status_code == 200:
        job = r.json()
        print(f"✅ Connection Job Started: ID {job['job_id']}")
    else:
        print(f"❌ Connection Job Failed: {r.text}")

def test_personnel():
    print(f"\nTesting Personnel Endpoints...")
    # 1. Departments
    dept_data = {"name": "Test Dept", "code": "TD01"}
    r = requests.post(f"{BASE_URL}/departments/", json=dept_data)
    if r.status_code == 200:
        dept = r.json()
        print(f"✅ Department Created: {dept['name']}")
        dept_id = dept['id']
    else:
        print(f"❌ Department Creation Failed: {r.text}")
        dept_id = None

    # 2. Employees
    emp_data = {
        "user_id": "9999",
        "name": "Test User",
        "department_id": dept_id
    }
    r = requests.post(f"{BASE_URL}/employees/", json=emp_data)
    if r.status_code == 200:
        emp = r.json()
        print(f"✅ Employee Created: {emp['name']}")
    else:
        print(f"❌ Employee Creation Failed: {r.text}")

def test_attendance():
    print(f"\nTesting Attendance Endpoints...")
    # 1. Timetables
    tt_data = {
        "name": "General Shift",
        "on_duty_time": "09:00",
        "off_duty_time": "18:00"
    }
    r = requests.post(f"{BASE_URL}/schedules/timetables/", json=tt_data)
    if r.status_code == 200:
        tt = r.json()
        print(f"✅ Timetable Created: {tt['name']}")
    else:
        print(f"❌ Timetable Creation Failed: {r.text}")

    # 2. Shifts
    shift_data = {"name": "Morning Shift"}
    r = requests.post(f"{BASE_URL}/schedules/shifts/", json=shift_data)
    if r.status_code == 200:
        shift = r.json()
        print(f"✅ Shift Created: {shift['name']}")
    else:
        print(f"❌ Shift Creation Failed: {r.text}")

if __name__ == "__main__":
    print("Waiting for server to start...")
    time.sleep(5) # Give it a moment if started recently
    test_health()
    dev_id = test_devices()
    if dev_id:
        test_connection_logic(dev_id)
    test_personnel()
    test_attendance()
