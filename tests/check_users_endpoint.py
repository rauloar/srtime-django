import requests

BASE_URL = "http://localhost:8001"
DEVICE_ID = 1

def check_endpoint():
    print(f"Logging in...")
    login_data = {"username": "raul", "password": "zkr15ldi12"}
    token = requests.post(f"{BASE_URL}/api/token/", json=login_data).json().get("access")
    headers = {"Authorization": f"Bearer {token}"}

    print(f"Checking GET /api/v1/devices/{DEVICE_ID}/users/ ...")
    r = requests.get(f"{BASE_URL}/api/v1/devices/{DEVICE_ID}/users/", headers=headers)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")

if __name__ == "__main__":
    check_endpoint()
