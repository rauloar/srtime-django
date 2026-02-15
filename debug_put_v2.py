import requests
import json

BASE_URL = "http://127.0.0.1:9000/api/v1"

def debug_put():
    # 1. Get List
    print("Fetching users...")
    try:
        r = requests.get(f"{BASE_URL}/employees/")
        if r.status_code != 200:
            print(f"Failed to get users: {r.status_code} {r.text}")
            return
        
        users = r.json()
        if not users:
            print("No users found.")
            return
            
        target = users[0]
        tid = target['id']
        print(f"Targeting User ID {tid}: {target.get('name')}")
        print("Original Data:", json.dumps(target, indent=2))
        
        # 2. Prepare Payload (mimic Frontend)
        # Frontend sends: ...employee, device, uid, user_id, name, card, etc.
        # UserSerializer expects: device (int), uid (int), etc.
        
        payload = target.copy()
        payload['name'] = "Debug Updated Name"
        
        # Ensure strict typing as frontend might send
        payload['device'] = target.get('device')  # Should be int
        payload['uid'] = target.get('uid')        # Should be int
        
        # If keys are missing in GET response, we have a problem
        if 'device' not in payload:
            print("WARNING: 'device' missing in GET response. Sending mocked 1.")
            payload['device'] = 1
        if 'uid' not in payload:
            print("WARNING: 'uid' missing in GET response. Sending mocked 1.")
            payload['uid'] = 1
            
        print("Sending Payload:", json.dumps(payload, indent=2))
        
        # 3. Send PUT
        r_put = requests.put(f"{BASE_URL}/employees/{tid}/", json=payload)
        print(f"PUT Response Status: {r_put.status_code}")
        print(f"PUT Response Body: {r_put.text}")
        
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    debug_put()
