import sys
import os
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SRTimeWeb.settings')
django.setup()

from core.models import (
    Company, Department, Employee, User, Timetable,
    Shift, EmployeeShift, AttendanceLog, DailyAttendance,
    Device, Zone, Position, Holiday, Leave
)

print("--- Database Counts ---")
try:
    print(f"Companies: {Company.objects.count()}")
    print(f"Positions: {Position.objects.count()}")
    print(f"Zones: {Zone.objects.count()}")
    print(f"Departments: {Department.objects.count()}")
    print(f"Employees: {Employee.objects.count()}")
    print(f"Devices: {Device.objects.count()}")
    print(f"Users: {User.objects.count()}")
    print(f"Timetables: {Timetable.objects.count()}")
    print(f"Shifts: {Shift.objects.count()}")
    print(f"EmployeeShifts: {EmployeeShift.objects.count()}")
    print(f"AttendanceLogs: {AttendanceLog.objects.count()}")
    print(f"DailyAttendance: {DailyAttendance.objects.count()}")
    print(f"Holidays: {Holiday.objects.count()}")
    print(f"Leaves: {Leave.objects.count()}")
except Exception as e:
    print(f"Error checking counts: {e}")
    import traceback
    traceback.print_exc()
