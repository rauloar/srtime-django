import requests
import sys
import json
import datetime

BASE_URL = "http://127.0.0.1:8001/api/v1"
LOGIN_URL = "http://127.0.0.1:8001/api/v1/auth/login"

def test_attendance_config():
    session = requests.Session()
    
    # 0. Get Cookie
    try:
        session.get(LOGIN_URL) # Seed cookie
    except:
        pass

    # 1. Login
    print(f"Logging in...")
    try:
        # Include CSRF token in login POST if available
        csrf = session.cookies.get('csrftoken')
        headers_login = {'X-CSRFToken': csrf, 'Referer': LOGIN_URL} if csrf else {}
        
        resp = session.post(LOGIN_URL, json={'username': 'raul', 'password': 'admin'}, headers=headers_login)
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code}")
            return False
            
        token = resp.json().get('access_token')
        csrf_token = session.cookies.get('csrftoken')
        headers = {
            'Authorization': f'Bearer {token}',
            'X-CSRFToken': csrf_token,
            'Referer': BASE_URL  # Sometimes needed for strict referer check
        }
        print(f"Login successful. CSRF: {csrf_token}")

        # 2. Extract Data (Need Timetable and Shift)
        print("Fetching Timetables...")
        t_resp = session.get(f"{BASE_URL}/schedules/timetables/", headers=headers)
        timetables = t_resp.json()
        if not timetables:
            print("No timetables found. Creating one...")
            tt_data = {
                "name": "General 9-18",
                "on_duty_time": "09:00",
                "off_duty_time": "18:00",
                "check_in_start": "08:00",
                "check_out_end": "19:00"
            }
            t_resp = session.post(f"{BASE_URL}/schedules/timetables/", json=tt_data, headers=headers)
            timetable_id = t_resp.json()['id']
            print(f"Created Timetable ID: {timetable_id}")
        else:
            timetable_id = timetables[0]['id']
            print(f"Using Timetable ID: {timetable_id}")

        print("Fetching Shifts...")
        s_resp = session.get(f"{BASE_URL}/schedules/shifts/", headers=headers)
        shifts = s_resp.json()
        if not shifts:
            print("No shifts found. Creating one...")
            s_resp = session.post(f"{BASE_URL}/shifts/", json={"name": "Turno General"}, headers=headers)
            shift_id = s_resp.json()['id']
            print(f"Created Shift ID: {shift_id}")
        else:
            shift_id = shifts[0]['id']
            print(f"Using Shift ID: {shift_id}")

        # 3. Test Cycle Configuration (The new Action)
        print("Testing Cycle Configuration...")
        cycle_data = [
            {"timetable_id": timetable_id, "day_index": 0}, # Mon
            {"timetable_id": timetable_id, "day_index": 1}, # Tue
            {"timetable_id": timetable_id, "day_index": 2}, # Wed
            {"timetable_id": timetable_id, "day_index": 3}, # Thu
            {"timetable_id": timetable_id, "day_index": 4}, # Fri
        ]
        
        c_resp = session.post(f"{BASE_URL}/shifts/{shift_id}/timetables/", json=cycle_data, headers=headers)
        print(f"Configure Cycle Response: {c_resp.status_code}")
        if c_resp.status_code == 200:
            print(f"Cycle configured successfully. Items: {len(c_resp.json())}")
        else:
            print(f"Failed to configure cycle: {c_resp.text}")
            return False

        # 4. Test Assignment
        print("Testing Shift Assignment...")
        # Get an employee
        e_resp = session.get(f"{BASE_URL}/employees/", headers=headers)
        employees = e_resp.json()
        if not employees:
            print("No employees list returned.")
            return False
            
        print(f"Employees Type: {type(employees)}")
        
        emp_id = None
        if isinstance(employees, dict) and 'results' in employees:
            if employees['results']:
                emp_id = employees['results'][0]['id']
            else:
                 print("Results empty")
        elif isinstance(employees, list):
            if employees:
                emp_id = employees[0]['id']
        
        if not emp_id:
             print("Creating dummy employee...")
             emp_data = {"user_id": "9999", "name": "Test User", "active": True}
             e_resp = session.post(f"{BASE_URL}/employees/", json=emp_data, headers=headers)
             if e_resp.status_code == 201:
                 emp_id = e_resp.json()['id']
             else:
                 print(f"Failed to create employee: {e_resp.text}")
                 return False

        print(f"Using Employee ID: {emp_id}")

        today = datetime.date.today().isoformat()
        assign_data = {
            "employee": int(emp_id),
            "shift": shift_id,
            "start_date": today,
            "scope": "EMPLOYEE"
        }
        
        # Using the standard create endpoint for EmployeeShift
        a_resp = session.post(f"{BASE_URL}/employee-shifts/", json=assign_data, headers=headers)
        print(f"Assignment Response: {a_resp.status_code}")
        if a_resp.status_code == 201:
            print("Assignment created successfully.")
            return True
        else:
            print(f"Failed to assign: {a_resp.text}")
            return False

    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    if test_attendance_config():
        print("SUCCESS")
    else:
        print("FAILURE")
