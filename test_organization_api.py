import requests
import sys

BASE_URL = "http://127.0.0.1:8001/api/v1"
LOGIN_URL = "http://127.0.0.1:8001/api/v1/auth/login"

def test_api():
    session = requests.Session()
    
    # 1. Login
    print(f"Logging in to {LOGIN_URL}...")
    try:
        resp = session.post(LOGIN_URL, json={'username': 'raul', 'password': 'admin'})
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} - {resp.text}")
            # Try port 9000 if 8001 fails or returns 404 (if not mapped correctly)
            return False
            
        token = resp.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}'}
        print("Login successful.")

        # 2. Check Company
        print("Checking Company endpoint...")
        resp = session.get(f"{BASE_URL}/companies/", headers=headers)
        print(f"Company: {resp.status_code}")
        if resp.status_code == 200:
             print(resp.json())

        # 3. Check Positions
        print("Checking Positions endpoint...")
        resp = session.get(f"{BASE_URL}/positions/", headers=headers)
        print(f"Positions: {resp.status_code}")

        # 4. Check Zones
        print("Checking Zones endpoint...")
        resp = session.get(f"{BASE_URL}/zones/", headers=headers)
        print(f"Zones: {resp.status_code}")
        
        return True

    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_api()
    if not success:
        # Retry on 9000
        print("\nRetrying on port 9000...")
        BASE_URL = "http://127.0.0.1:9000/api/v1"
        LOGIN_URL = "http://127.0.0.1:9000/api/v1/auth/login"
        test_api()
