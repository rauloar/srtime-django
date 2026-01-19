import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend import models

print("--- Department Model Debug ---")
print(f"Columns: {models.Department.__table__.columns.keys()}")
try:
    d = models.Department(name="Test", company_id=1)
    print("Department init with company_id=1 SUCCESS")
except Exception as e:
    print(f"Department init with company_id=1 FAILED: {e}")
