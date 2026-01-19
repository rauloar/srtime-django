
import sys
import os
from sqlalchemy import create_engine, text

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.database import settings

def inspect_schema():
    print(f"Connecting to: {settings.DB_URL}")
    engine = create_engine(settings.DB_URL)
    
    with engine.connect() as conn:
        print("\n--- att_employee_shifts ---")
        try:
            # MySQL syntax
            res = conn.execute(text("DESCRIBE att_employee_shifts"))
            for row in res:
                print(row)
        except Exception:
            # SQLite Syntax
            try:
                res = conn.execute(text("PRAGMA table_info(att_employee_shifts)"))
                rows = list(res)
                if not rows:
                    print("Table not found or empty info")
                for row in rows:
                    print(row)
            except Exception as e:
                print(f"Error inspecting: {e}")

if __name__ == "__main__":
    inspect_schema()
