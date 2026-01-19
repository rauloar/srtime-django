import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SRTimeWeb.settings')
django.setup()

from django.db import connection

tables = {
    'employees': ['mobile_phone', 'country', 'birthday'],
    'devices': ['zone_id'],
    'att_employee_shifts': ['scope', 'department_id'],
    'att_daily_attendance': ['schedule_type', 'source_logs_count', 'is_absent']
}

with connection.cursor() as cursor:
    for table_name, expected_columns in tables.items():
        cursor.execute('''
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s 
            ORDER BY ordinal_position
        ''', [table_name])
        
        columns = [row[0] for row in cursor.fetchall()]
        
        print(f"\n{table_name}:")
        print(f"  Total columns: {len(columns)}")
        print(f"  Columns: {', '.join(columns)}")
        
        missing = []
        for col in expected_columns:
            if col in columns:
                print(f"  ✅ {col} presente")
            else:
                print(f"  ❌ {col} FALTANTE")
                missing.append(col)
        
        if missing:
            print(f"  FALTAN: {', '.join(missing)}")
