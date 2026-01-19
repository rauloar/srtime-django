
import sys
import os

sys.path.append("c:\\Proyectos\\pyzk")

from zk import ZK, const

def save_raw_logs():
    ip = "192.168.1.201"
    port = 4370
    output_file = "raw_attendance_logs.txt"
    
    print(f"Connecting to {ip}:{port}...")
    zk = ZK(ip, port=port, timeout=5)
    
    try:
        conn = zk.connect()
        print("Connected!")
        
        print("Fetching attendance logs...")
        logs = conn.get_attendance()
        print(f"Got {len(logs)} logs.")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Raw Attendance Logs from {ip}\n")
            f.write("=" * 60 + "\n")
            f.write(f"{'User ID':<10} | {'Timestamp':<25} | {'Status':<6} | {'Punch':<6} | {'Raw String'}\n")
            f.write("-" * 60 + "\n")
            
            for log in logs:
                # log.__str__() usually returns something like <Attendance>: 1 : 2023-01-01 10:00:00 (1, 0)
                f.write(f"{log.user_id:<10} | {str(log.timestamp):<25} | {log.status:<6} | {log.punch:<6} | {str(log)}\n")
        
        print(f"✅ Successfully saved {len(logs)} logs to {output_file}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.disconnect()

if __name__ == "__main__":
    save_raw_logs()
