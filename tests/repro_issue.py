import requests
import sys
import os

# Base URL
BASE_URL = "http://localhost:8001"

def reproduce():
    # 1. Login
    print(f"Logging in as raul...")
    login_data = {
        "username": "raul",
        "password": "zkr15ldi12"
    }
    
    # Try different login endpoints common in Django Rest Framework
    token = None
    for endpoint in ["/api/token/", "/api/v1/token/", "/api/login/", "/token/"]:
        try:
            r = requests.post(f"{BASE_URL}{endpoint}", json=login_data)
            if r.status_code == 200:
                print(f"✅ Login successful at {endpoint}")
                token = r.json().get("access")
                break
        except Exception as e:
            print(f"Failed to connect to {endpoint}: {e}")
            continue

    if not token:
        print("❌ Login failed. check credentials or endpoints.")
        # Try finding the correct login endpoint by checking urls
        return

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # 2. List Devices
    print("\nListing devices...")
    try:
        r = requests.get(f"{BASE_URL}/api/v1/devices/", headers=headers)
        if r.status_code == 200:
            json_response = r.json()
            if isinstance(json_response, dict):
                devices = json_response.get('results', [])
            elif isinstance(json_response, list):
                devices = json_response
            else:
                print(f"Unknown response format: {json_response}")
                return

            if not devices:
                print("⚠️ No devices found in database.")
                return
            
            print(f"Found {len(devices)} devices.")
            
            # 3. Test Connection for each device
            for device in devices:
                dev_id = device.get('id')
                name = device.get('name')
                ip = device.get('ip')
                print(f"\nTesting connection for device: {name} ({ip})...")
                
                # Try sync endpoint first for immediate feedback
                print("--- SYNC TEST ---")
                try:
                    r_test = requests.get(f"{BASE_URL}/api/v1/devices/{dev_id}/test-connection-sync/", headers=headers)
                    print(f"Sync Test Status: {r_test.status_code}")
                    print(f"Response: {r_test.text}")
                except Exception as e:
                    print(f"Sync Test Failed: {e}")
                
                # Check asynchronous endpoint
                print("\n--- ASYNC TEST ---")
                try:
                    r_async = requests.post(f"{BASE_URL}/api/v1/devices/{dev_id}/test-connection/", headers=headers)
                    print(f"Async Job Start Status: {r_async.status_code}")
                    
                    if r_async.status_code == 200:
                        job_data = r_async.json()
                        job_id = job_data.get('job_id')
                        print(f"Job Started: {job_id}")
                        
                        # Poll status
                        import time
                        for i in range(10): # Wait up to 10 seconds
                            time.sleep(1)
                            r_job = requests.get(f"{BASE_URL}/api/v1/jobs/{job_id}/", headers=headers)
                            if r_job.status_code == 200:
                                job_status = r_job.json().get('status')
                                print(f"Job Status: {job_status}")
                                if job_status in ['completed', 'failed']:
                                    # Get logs
                                    r_logs = requests.get(f"{BASE_URL}/api/v1/jobs/{job_id}/logs/", headers=headers)
                                    print(f"Job Logs: {r_logs.text}")
                                    break
                            else:
                                print(f"Failed to get job status: {r_job.status_code}")
                    else:
                        print(f"Async Job Failed to Start: {r_async.text}")

                except Exception as e:
                    print(f"Async Test Failed: {e}")

                # Check Download Users (Data Transfer)
                print("\n--- DOWNLOAD USERS TEST ---")
                try:
                    r_dl = requests.post(f"{BASE_URL}/api/v1/devices/{dev_id}/download-users/", headers=headers)
                    print(f"Download Job Start Status: {r_dl.status_code}")
                    
                    if r_dl.status_code == 200:
                        job_id = r_dl.json().get('job_id')
                        print(f"Job Started: {job_id}")
                        
                        # Poll status
                        import time
                        for i in range(20): # Wait up to 20 seconds
                            time.sleep(1)
                            r_job = requests.get(f"{BASE_URL}/api/v1/jobs/{job_id}/", headers=headers)
                            if r_job.status_code == 200:
                                job_status = r_job.json().get('status')
                                print(f"Job Status: {job_status}")
                                if job_status in ['completed', 'failed']:
                                    # Get logs
                                    r_logs = requests.get(f"{BASE_URL}/api/v1/jobs/{job_id}/logs/", headers=headers)
                                    print(f"Job Logs: {r_logs.text}")
                                    break
                            else:
                                print(f"Failed to get job status: {r_job.status_code}")
                    else:
                        print(f"Download Users Failed to Start: {r_dl.text}")
                except Exception as e:
                    print(f"Download Users Test Failed: {e}")

        else:
            print(f"❌ Failed to list devices: {r.status_code} {r.text}")

    except Exception as e:
        print(f"❌ Error listing devices: {e}")

if __name__ == "__main__":
    reproduce()
