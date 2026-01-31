import requests
import sys

BASE_URL = "http://localhost:8001"

def verify_info_endpoint():
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
        print(f"❌ Failed to list devices: {r_dev.status_code}")
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
    print(f"Testing Info on Device: {device['name']} (ID: {dev_id})")

    # Test Info Endpoint
    endpoint = f"/api/v1/devices/{dev_id}/info/"
    print(f"Testing GET {endpoint}...")
    try:
        r = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print(f"✅ Success: {r.text[:200]}...")
            data = r.json()
            if data.get('success') and 'firmware_version' in data:
                 print("✅ Data validation passed")
            else:
                 print("⚠️ Data validation warning")
        else:
            print(f"❌ Failed: {r.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_info_endpoint()
