import sys
import platform
import shutil
import os
import socket
import logging

try:
    import psutil
except ImportError:
    psutil = None

try:
    from sqlalchemy import create_engine, text
    from dotenv import load_dotenv
    # Flexible import path
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from backend import database
except ImportError as e:
    print(f"Import Error (Checking Environment): {e}")

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

def check_python_version():
    valid = sys.version_info >= (3, 9)
    current = sys.version.split()[0]
    return {
        "name": "Python Version",
        "current": current,
        "min": "3.9+",
        "ideal": "3.11+",
        "status": "OK" if valid else "FAIL",
        "note": "Required for FastAPI async features."
    }

def check_memory():
    # Fallback if psutil not installed
    total_gb = 0
    if psutil:
        mem = psutil.virtual_memory()
        total_gb = round(mem.total / (1024.0 ** 3), 2)
    else:
        return {"name": "RAM", "current": "Unknown (psutil missing)", "min": "4GB", "ideal": "8GB", "status": "WARN"}
        
    status = "OK"
    if total_gb < 4:
        status = "FAIL"
    elif total_gb < 8:
        status = "OK (Minimum)"
    else:
        status = "OK (Ideal)"
        
    return {
        "name": "System RAM",
        "current": f"{total_gb} GB",
        "min": "4 GB",
        "ideal": "8 GB",
        "status": status
    }

def check_disk_space():
    total, used, free = shutil.disk_usage(".")
    free_gb = round(free / (1024.0 ** 3), 2)
    
    status = "OK"
    if free_gb < 2:
        status = "FAIL"
    elif free_gb < 10:
        status = "WARN"
        
    return {
        "name": "Disk Space (Free)",
        "current": f"{free_gb} GB",
        "min": "2 GB",
        "ideal": "10 GB+",
        "status": status
    }

def check_database():
    error_msg = ""
    try:
        # Import internally to contain errors
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from backend import database
        
        db_url = "Unknown"
        if hasattr(database, 'SQLALCHEMY_DATABASE_URL'):
            db_url = database.SQLALCHEMY_DATABASE_URL
            
        # Check connection
        engine = database.engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            
        db_type = "MySQL" if "mysql" in str(db_url).lower() else "SQLite"
        
        return {
            "name": "Database Connection",
            "current": f"Connected ({db_type})",
            "min": "SQLite/MySQL",
            "ideal": "MySQL 8.0+",
            "status": "OK"
        }
    except Exception as e:
        error_msg = str(e)
        # Simplify error for display
        display_err = error_msg[:30] + "..." if len(error_msg) > 30 else error_msg
        return {
            "name": "Database Connection",
            "current": f"Error: {display_err}",
            "min": "Working DB",
            "ideal": "MySQL",
            "status": "FAIL"
        }

def check_port_availability(port=8000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    # If result is 0, port is OPEN (in use). That might be good if we expect app to be running, 
    # but strictly for "requirements" we might want it free to start. 
    # Let's just report status.
    
    msg = "Free" if result != 0 else "In Use (App Running?)"
    return {
        "name": f"Port {port} Availability",
        "current": msg,
        "min": "Available",
        "ideal": "-",
        "status": "INFO"
    }

def run_checks():
    print("="*60)
    print(f" SR-Bio System Requirements Check")
    print("="*60)
    print(f"{'Check Item':<25} | {'Current':<20} | {'Status':<10}")
    print("-" * 60)
    
    checks = [
        check_python_version(),
        check_memory(),
        check_disk_space(),
        check_database(),
        check_port_availability(8000)
    ]
    
    overall_pass = True
    
    for c in checks:
        print(f"{c['name']:<25} | {c['current']:<20} | {c['status']:<10}")
        if "FAIL" in c['status']:
            overall_pass = False
            
    print("-" * 60)
    print(f"Platform: {platform.system()} {platform.release()} ({platform.machine()})")
    print("-" * 60)
    
    if overall_pass:
        print("\n[SUCCESS] The system meets the requirements to run user SR-Bio.")
    else:
        print("\n[WARNING] Some requirements were not met. Check the table above.")

if __name__ == "__main__":
    run_checks()
