import requests
import sys
import os
import time

BASE_URL = "http://localhost:8001"

def verify_new_endpoints():
    print(f"Logging in as raul...")
    login_data = {"username": "raul", "password": "zkr15ldi12"}
    
    r = requests.post(f"{BASE_URL}/api/token/", json=login_data)
    if r.status_code != 200:
        print("❌ Login failed")
        return

    token = r.json().get("access")
    headers = {"Authorization": f"Bearer {token}"}

    # Get a device ID
    r_dev = requests.get(f"{BASE_URL}/api/v1/devices/", headers=headers)
    if r_dev.status_code != 200:
        print("❌ Failed to list devices")
        return

    json_resp = r_dev.json()
    if isinstance(json_resp, dict):
        devices = json_resp.get('results', [])
    elif isinstance(json_resp, list):
        devices = json_resp
    else:
        devices = []
        
    if not devices:
        print("❌ No devices found")
        return

    device = devices[0]
    dev_id = device['id']
    print(f"Testing on Device: {device['name']} (ID: {dev_id})")

    # Test Endpoints
    endpoints = [
        ("GET", f"/api/v1/devices/{dev_id}/memory"),
        ("GET", f"/api/v1/devices/{dev_id}/attendance/recent?limit=5"),
        ("GET", f"/api/v1/devices/{dev_id}/templates"),
        # Hazardous operations (restart/poweroff) skipped for safety in automation, or test gently
        ("POST", f"/api/v1/devices/{dev_id}/sync-time"),
        ("POST", f"/api/v1/devices/{dev_id}/test-voice?voice_index=0"),
    ]

    for method, endpoint in endpoints:
        print(f"\nTesting {method} {endpoint}...")
        try:
            if method == "GET":
                r = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            else:
                r = requests.post(f"{BASE_URL}{endpoint}", headers=headers)
            
            print(f"Status: {r.status_code}")
            if r.status_code == 200:
                print(f"✅ Success: {r.text[:100]}...")
            else:
                print(f"❌ Failed: {r.text}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_new_endpoints()
