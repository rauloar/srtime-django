
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
    else:
        # Pick the first device
        device = devices[0]
        print(f"Found device ID {device['id']}: {device['name']} ({device['ip']})")
        
        # Update IP if needed (API doesn't have PUT /devices/{id} update endpoint generic yet? 
        # Let's check routers/devices.py. 
        # It seems I only implemented CREATE and READ. 
        # Wait, I need to check if there is an update endpoint.
        # If not, I might need to update via DB directly or add the endpoint.
        # Let's assume I need to ADD the endpoint or update via DB loop if missing.
        # Checking routers/devices.py content from memory... only create_device, read_devices, read_device.
        # No update? I should check.
        pass

if __name__ == "__main__":
    pass
