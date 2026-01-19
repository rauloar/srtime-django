
import pymysql
import pymysql.cursors

def verify_logs():
    print("Verifying Logs in MySQL...")
    try:
        from backend.database import settings
        from sqlalchemy.engine.url import make_url
        url = make_url(settings.DB_URL)
        conn = pymysql.connect(
            user=url.username or "root",
            password=url.password or "",
            host=url.host or "localhost",
            database=url.database or "zk_webapp",
            port=url.port or 3306,
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        
        # Check last log
        cursor.execute("SELECT * FROM attendance_logs ORDER BY timestamp DESC LIMIT 10")
        rows = cursor.fetchall()
        
        if not rows:
            print("No logs found.")
            return

        print(f"Found {len(rows)} logs.")
        for row in rows:
            ts = row['timestamp']
            v_mode = row['verify_mode']
            status = row['status']
            print(f"User: {row['user_id']} | Time: {ts} | Status: {status} | Mode: {v_mode}")
            
            # Basic Verification
            # pyzk punch=15 usually means Face or similar
            # pyzk punch=1 usually means Finger
            # Time should be datetime object
            
            if ts.hour > 12:
                print(f"   -> 24h Check: Time {ts} is correctly afternoon/evening.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn.open:
            conn.close()

if __name__ == "__main__":
    verify_logs()
