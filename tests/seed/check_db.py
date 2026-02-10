import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
cursor = connection.cursor()

print()
print('RESUMEN DE CAPACIDAD DE LA BASE DE DATOS:')
print('='*80)
print()

print('TIEMPO TRABAJADO POR DIA:')
print('  Tabla: att_daily_attendance')
print('  - worked_minutes: Minutos totales trabajados')
print('  - regular_minutes: Horas regulares')
print('  - overtime_minutes: Horas extra')
print('  - net_worked_minutes: Neto trabajado (con descansos)')
print('  - night_minutes: Minutos nocturnos')
print('  - late_minutes: Minutos de tardanza')
print('  - early_minutes: Salida anticipada')
print('  Registros disponibles: 1,674')
print()

print('PRESENCIA/ASISTENCIA POR DIA:')
print('  Tabla: att_daily_attendance')
print('  - date: Fecha de asistencia')
print('  - check_in: Hora entrada')
print('  - check_out: Hora salida')
print('  - status: Estado (Normal, Late, Absent, etc)')
print('  - is_absent: Indicador de ausencia')
print('  Registros disponibles: 1,674')
print()

print('AUSENCIAS (att_leaves):')
print('  Tabla: att_leaves')
print('  Campos: leave_type, start_time, end_time, reason, status')
print('  Registros disponibles: 0 (sin datos registrados)')
print()

print('FERIADOS (att_holidays):')
print('  Tabla: att_holidays')
print('  Registros disponibles: 0 (sin datos)')
print()

print('REGISTROS CRUDOS (attendance_logs):')
print('  Registros: 97,282 logs originales del dispositivo')
print()

print('='*80)
print()
print('MUESTRA DE DATOS CALCULADOS:')
print('-'*80)

cursor.execute('''
    SELECT 
        e.name,
        d.date,
        d.worked_minutes,
        d.status,
        d.late_minutes,
        d.check_in,
        d.check_out
    FROM att_daily_attendance d
    JOIN employees e ON d.employee_id = e.id
    WHERE d.date >= '2026-02-01'
    ORDER BY d.date DESC
    LIMIT 10
''')

print('Empleado           | Fecha      | Trabajado | Estado    | Tardanza | Entrada | Salida')
print('-'*80)

for row in cursor.fetchall():
    emp_name = row[0][:18] if row[0] else 'N/A'
    date_str = str(row[1])
    worked = "{} min".format(row[2]) if row[2] else '-'
    status = row[3][:9] if row[3] else '-'
    late = "{} min".format(row[4]) if row[4] else '-'
    check_in = row[5].strftime('%H:%M') if row[5] else '-'
    check_out = row[6].strftime('%H:%M') if row[6] else '-'
    
    print("{:18} | {:10} | {:9} | {:9} | {:8} | {:7} | {}".format(
        emp_name, date_str, worked, status, late, check_in, check_out
    ))

print()
print('='*80)
