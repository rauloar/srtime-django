import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SRTimeWeb.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute('SELECT COUNT(*) FROM att_employee_shifts')
    count = cursor.fetchone()[0]
    print(f"att_employee_shifts: {count} registros")
    
    cursor.execute('SELECT COUNT(*) FROM devices')
    count = cursor.fetchone()[0]
    print(f"devices: {count} registros")
    
    cursor.execute('SELECT COUNT(*) FROM employees')
    count = cursor.fetchone()[0]
    print(f"employees: {count} registros")
    
    cursor.execute('SELECT COUNT(*) FROM att_daily_attendance')
    count = cursor.fetchone()[0]
    print(f"att_daily_attendance: {count} registros")
