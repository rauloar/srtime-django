
import requests
import json

def test_logs_names():
    import os
    try:
        from backend.database import settings
        url = os.getenv("BACKEND_URL", f"http://localhost:{settings.API_PORT}/attendance/")
    except Exception:
        url = os.getenv("BACKEND_URL", "http://localhost:8001/attendance/")
    try:
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            print(f"Count: {len(data)}")
            if len(data) > 0:
                print(f"Sample Log: ID={data[0]['id']}, UserID={data[0]['user_id']}, Name={data[0].get('user_name')}")
                if 'user_name' in data[0]:
                    print("PASS: user_name field present.")
                else:
                    print("FAIL: user_name field missing.")
        else:
            print(f"Error: {r.status_code} {r.text}")
    except Exception as e:
        print(f"Ex: {e}")

if __name__ == "__main__":
    test_logs_names()
