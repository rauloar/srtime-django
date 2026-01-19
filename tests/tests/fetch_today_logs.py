
import sys
import datetime

sys.path.append("c:\\Proyectos\\pyzk")

from zk import ZK

def fetch_today_logs():
    ip = "192.168.1.201"
    port = 4370
    
    # User said "today", let's assume local server date.
    today = datetime.date.today()
    print(f"Fetching logs for TODAY: {today}...")

    print(f"Connecting to {ip}:{port}...")
    zk = ZK(ip, port=port, timeout=5)
    
    try:
        conn = zk.connect()
        print("Connected!")
        
        print("Fetching attendance logs...")
        logs = conn.get_attendance()
        print(f"Total logs on device: {len(logs)}")
        
        # Filter for today
        todays_logs = [log for log in logs if log.timestamp.date() == today]
        
        if not todays_logs:
            print("No logs found for today.")
            # Fallback: Show last 10 logs generally if today is empty, just in case device time is wrong
            print("Showing last 10 logs instead (to check device time):")
            todays_logs = logs[-10:]

        print("\n" + "=" * 80)
        print(f"{'Time':<20} | {'User ID':<10} | {'Status (pyzk)':<15} | {'Punch (pyzk)':<15} | {'Raw String'}")
        print("=" * 80)
        
        for log in todays_logs:
            print(f"{str(log.timestamp):<20} | {log.user_id:<10} | {log.status:<15} | {log.punch:<15} | {str(log)}")
            
        print("=" * 80)
        print("NOTE: 'Status (pyzk)' is usually expected to be the check-in/out state.")
        print("NOTE: 'Punch (pyzk)' was previously thought to be Verify Mode, but User suspects it is State.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.disconnect()

if __name__ == "__main__":
    fetch_today_logs()
