#!/usr/bin/env python
"""Verificar que los seeds se grabaron correctamente."""

from core.models import AttendanceLog, Employee, Device

print("\n" + "="*70)
print("VERIFICACION DE SEEDS")
print("="*70)

print(f"\nTotal Devices: {Device.objects.count()}")
print(f"Total Employees: {Employee.objects.count()}")
print(f"Total AttendanceLogs: {AttendanceLog.objects.count()}")

print("\n" + "-"*70)
print("DEVICES")
print("-"*70)
for device in Device.objects.all():
    print(f"  {device.name} ({device.ip}:{device.port}) - Logs: {device.logs.count()}")

print("\n" + "-"*70)
print("EMPLOYEES")
print("-"*70)
for emp in Employee.objects.all().order_by('user_id'):
    print(f"  {emp.user_id}: {emp.name} (active={emp.active})")

print("\n" + "-"*70)
print("ATTENDANCE LOGS (ordenados por timestamp)")
print("-"*70)
print(f"{'user_id':8} | {'timestamp':19} | punch | status | workstate")
print("-" * 70)
for log in AttendanceLog.objects.all().order_by('timestamp'):
    ws = log.workstate if log.workstate is not None else "NULL"
    print(f"{log.user_id:8} | {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | {log.punch:5} | {log.status:6} | {ws}")

print("\n" + "-"*70)
print("RESUMEN POR ESCENARIO")
print("-"*70)

scenarios = [
    (200, "2026-02-10", "ESCENARIO A: Basico (entrada/salida)"),
    (201, "2026-02-11", "ESCENARIO B: Con break"),
    (202, "2026-02-12", "ESCENARIO C: Incompleto"),
    (203, "2026-02-13", "ESCENARIO D: Doble entrada"),
]

for user_id, date_str, description in scenarios:
    logs = AttendanceLog.objects.filter(
        user_id=str(user_id),
        timestamp__date=date_str
    ).order_by('timestamp')
    
    print(f"\n{description}")
    print(f"  User ID: {user_id}")
    print(f"  Fecha: {date_str}")
    print(f"  Total logs: {logs.count()}")
    for i, log in enumerate(logs, 1):
        punch_desc = "ENTRADA" if log.punch == 0 else "SALIDA" if log.punch == 1 else f"??{log.punch}"
        print(f"    [{i}] {log.timestamp.strftime('%H:%M:%S')} punch={log.punch} ({punch_desc})")

print("\n" + "="*70)
print("VERIFICACION COMPLETADA")
print("="*70 + "\n")
