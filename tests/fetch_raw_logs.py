
import sys
import os

# Add parent directory to path to find zk module if needed, 
# but here we assume pyzk is installed or available. 
# Since previous scripts failed finding 'zk', I will try to point to the local pyzk copy if possible
# or just rely on the python environment having it.
# Based on previous steps, 'zk' module wasn't found in standard path. 
# I will try to add c:\Proyectos\pyzk to sys.path

sys.path.append("c:\\Proyectos\\pyzk")

from zk import ZK, const

def fetch_raw_logs():
    ip = "192.168.1.201"
    port = 4370
    
    print(f"Connecting to {ip}:{port}...")
    zk = ZK(ip, port=port, timeout=5)
    
    try:
        conn = zk.connect()
        print("Connected!")
        
        print("Fetching attendance logs...")
        logs = conn.get_attendance()
        print(f"Got {len(logs)} logs.")
        
        print("-" * 60)
        print(f"{'User ID':<10} | {'Timestamp':<20} | {'Status':<6} | {'Punch':<6} | {'UID':<6}")
        print("-" * 60)
        
        # Show last 20 logs
        for log in logs[-20:]:
            print(f"{log.user_id:<10} | {str(log.timestamp):<20} | {log.status:<6} | {log.punch:<6} | {log.uid:<6}")
            
        print("-" * 60)
        print("Raw Object Sample (Last Log):")
        if logs:
            print(logs[-1])
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.disconnect()

if __name__ == "__main__":
    fetch_raw_logs()
