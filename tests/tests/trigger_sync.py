
import requests
import time

def trigger_sync():
    import os
    try:
        from backend.database import settings
        base_url = os.getenv("BACKEND_URL", f"http://localhost:{settings.API_PORT}")
    except Exception:
        base_url = os.getenv("BACKEND_URL", "http://localhost:8001")
    device_id = 1 # Assuming ID 1
    
    print(f"Triggering SYNC for device {device_id}...")
    try:
        resp = requests.post(f"{base_url}/devices/{device_id}/attendance/sync")
        print(f"Response: {resp.status_code} - {resp.text}")
        
        if resp.status_code == 200:
            job_id = resp.json().get("job_id")
            print(f"Job ID: {job_id}. Monitoring...")
            
            # Monitor job
            for _ in range(10):
                time.sleep(2)
                job_resp = requests.get(f"{base_url}/jobs/{job_id}")
                if job_resp.status_code == 200:
                    job = job_resp.json()
                    status = job.get("status")
                    progress = job.get("progress")
                    print(f"Status: {status} | Progress: {progress}%")
                    if status in ["completed", "failed"]:
                        break
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    trigger_sync()
