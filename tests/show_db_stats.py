
import sys
import os
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SRTimeWeb.settings')
django.setup()

from core.models import Employee, AttendanceLog, DailyAttendance

def show_stats():
    try:
        print("📊 Database Persistence Check:")
        
        # 1. Inputs (Mock Data)
        emp_count = Employee.objects.count()
        log_count = AttendanceLog.objects.count()
        
        print(f"   - Inputs:")
        print(f"     ✅ Employees: {emp_count} (Saved in 'employees')")
        print(f"     ✅ Logs: {log_count} (Saved in 'attendance_logs')")
        
        # 2. Outputs (Calculation Results)
        daily_count = DailyAttendance.objects.count()
        print(f"   - Outputs:")
        if daily_count > 0:
            print(f"     ✅ Calculated Daily Reports: {daily_count} (Saved in 'att_daily_attendance')")
        else:
            print(f"     ⚠️ Calculated Daily Reports: 0 (Run calculation first!)")

        # 3. Sample
        if daily_count > 0:
            last = DailyAttendance.objects.select_related('employee').order_by('-id').first()
            print(f"\n   📝 Last Saved Calculation Record (ID: {last.id}):")
            print(f"      Employee: {last.employee.name}")
            print(f"      Date: {last.date}")
            print(f"      Status: {last.status}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    show_stats()
