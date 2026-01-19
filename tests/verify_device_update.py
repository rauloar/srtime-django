
import requests
import time
import sys

import os
try:
    from backend.database import settings
    BASE_URL = os.getenv("BACKEND_URL", f"http://localhost:{settings.API_PORT}")
except Exception:
    BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8001")

def update_and_test():
    print("Fetching devices...")
    try:
        r = requests.get(f"{BASE_URL}/devices/")
        devices = r.json()
    except Exception as e:
        print(f"❌ Error fetching devices: {e}")
        return

    device_id = None
    if not devices:
        print("No devices found. Creating one...")
        r = requests.post(f"{BASE_URL}/devices/", json={
            "name": "ZKTeco Device",
            "ip": "192.168.1.201",
            "port": 4370
        })
        if r.status_code != 200:
            print(f"❌ Failed to create device: {r.text}")
            return
        device = r.json()
        device_id = device['id']
    else:
        # Pick the first device
        device = devices[0]
        device_id = device['id']
        print(f"Found device ID {device_id}: {device['name']} ({device['ip']})")

    # Update Device
    print(f"Updating device {device_id} to 192.168.1.201:4370...")
    update_data = {
        "name": device['name'], # Keep name
        "ip": "192.168.1.201",
        "port": 4370,
        "enabled": True
    }
    r = requests.put(f"{BASE_URL}/devices/{device_id}", json=update_data)
    if r.status_code == 200:
        print(f"✅ Device updated successfully.")
        updated_device = r.json()
        print(f"   IP: {updated_device['ip']}, Port: {updated_device['port']}")
    else:
        print(f"❌ Failed to update device: {r.status_code} {r.text}")
        return

    # Test Connection
    print(f"Testing connection for device {device_id}...")
    r = requests.post(f"{BASE_URL}/devices/{device_id}/test-connection")
    if r.status_code == 200:
        job = r.json()
        print(f"✅ Connection Job Started: Job ID {job['job_id']}")
    else:
        print(f"❌ Failed to start connection job: {r.text}")

if __name__ == "__main__":
    update_and_test()
