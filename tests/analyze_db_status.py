
import pymysql
import pymysql.cursors
from sqlalchemy.engine.url import make_url

def analyze_db():
    print("Analyzing Attendance Logs in MySQL...")
    from backend.database import settings
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
    
    try:
        # Check distribution of status vs verify_mode
        print("\n--- Status vs Verify Mode ---")
        cursor.execute("""
            SELECT status, verify_mode, count(*) as count 
            FROM attendance_logs 
            GROUP BY status, verify_mode
        """)
        for row in cursor.fetchall():
            print(f"Status: {row['status']} | Verify Mode: {row['verify_mode']} | Count: {row['count']}")
            
        print("\n--- Sample of 'Broken' Logs (Status=0) ---")
        cursor.execute("SELECT * FROM attendance_logs WHERE status=0 LIMIT 5")
        for row in cursor.fetchall():
            print(row)
            
    finally:
        conn.close()

if __name__ == "__main__":
    analyze_db()
