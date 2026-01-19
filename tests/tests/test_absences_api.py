
import sys
import os
import requests

def test_absences_api():
    import os
    try:
        from backend.database import settings
        base_url = os.getenv("BACKEND_URL", f"http://localhost:{settings.API_PORT}/attendance/absences/")
    except Exception:
        base_url = os.getenv("BACKEND_URL", "http://localhost:8001/attendance/absences/")
    print(f"GET {base_url}")
    
    try:
        r = requests.get(base_url)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Count: {len(data)}")
            for item in data:
                print(f" - [{item['id']}] {item['employee_name']}: {item['type']} ({item['start_date']})")
        else:
            print("Response:", r.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_absences_api()
