
import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

print("Importing models...")
try:
    from backend import models
    print("Models imported successfully.")
    
    from backend.database import engine
    print("Engine imported.")
    
    # Try to inspect
    from sqlalchemy import inspect
    insp = inspect(models.EmployeeShift)
    print("EmployeeShift inspected.", insp)
    
except Exception as e:
    print(f"FAILED to import: {e}")
    import traceback
    traceback.print_exc()
