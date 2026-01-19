import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend import models

print("--- Device Model Debug ---")
print(f"Columns: {models.Device.__table__.columns.keys()}")
try:
    d = models.Device(name="Test", ip="1.1.1.1")
    print("Device init with ip='...' SUCCESS")
except Exception as e:
    print(f"Device init with ip='...' FAILED: {e}")

try:
    d = models.Device(name="Test", ip_address="1.1.1.1")
    print("Device init with ip_address='...' SUCCESS")
except Exception as e:
    print(f"Device init with ip_address='...' FAILED: {e}")
