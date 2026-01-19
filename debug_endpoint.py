import requests

base_url = "http://127.0.0.1:9000/api/v1"

# Login
response = requests.post(f"{base_url}/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Test employee-shifts
print("📅 Probando /schedules/employee-shifts/...")
response = requests.get(f"{base_url}/schedules/employee-shifts/?skip=0&limit=5", headers=headers)
print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"Response text: {response.text[:200]}")

if response.status_code == 200:
    try:
        data = response.json()
        print(f"✅ JSON válido")
        print(f"Tipo: {type(data)}")
        print(f"Data: {data}")
    except Exception as e:
        print(f"❌ Error parseando JSON: {e}")
