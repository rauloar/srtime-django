import requests
import json
import sys

BASE_URL = "http://localhost:8001"

def check_structure():
    print(f"Logging in...")
    login_data = {"username": "raul", "password": "zkr15ldi12"}
    
    r = requests.post(f"{BASE_URL}/api/token/", json=login_data)
    token = r.json().get("access")
    headers = {"Authorization": f"Bearer {token}"}

    print(f"Fetching /api/v1/devices/ ...")
    r = requests.get(f"{BASE_URL}/api/v1/devices/", headers=headers)
    print(f"Status: {r.status_code}")
    
    try:
        data = r.json()
        print(f"Raw Response Type: {type(data)}")
        print(json.dumps(data, indent=2))
    except:
        print("Failed to parse JSON")
        print(r.text)

if __name__ == "__main__":
    check_structure()
