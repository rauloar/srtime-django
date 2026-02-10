#!/usr/bin/env python
"""
Test script for intelligent attendance calculation with skip reporting
"""
import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.services import calculate_period
from core import models

# Abril 2025 - periodo con buenos datos
start = datetime(2025, 4, 1).date()
end = datetime(2025, 4, 30).date()

results, skipped = calculate_period(start, end)

print("\n" + "="*60)
print("ATTENDANCE CALCULATION REPORT")
print("="*60)
print(f"\nPeriod: {start} to {end}")
print(f"\n✅ Processed: {len(results)} daily records")
print(f"❌ Skipped: {len(skipped)} records/employees")

# Agrupar por razón
skipped_by_reason = {}
for skip in skipped:
    reason = skip['reason']
    if reason not in skipped_by_reason:
        skipped_by_reason[reason] = []
    skipped_by_reason[reason].append({
        'id': skip['employee_id'],
        'name': skip['name']
    })

print("\n--- SKIPPED BY REASON ---")
for reason, employees in skipped_by_reason.items():
    print(f"\n{reason}: {len(employees)} employees")
    for emp in employees[:5]:  # Show first 5
        print(f"  - ID {emp['id']}: {emp['name']}")
    if len(employees) > 5:
        print(f"  ... and {len(employees) - 5} more")

# Mostrar sample de resultados procesados
print("\n--- SAMPLE OF PROCESSED RECORDS ---")
for record in results[:5]:
    emp = models.Employee.objects.get(id=record.employee_id)
    print(f"📅 {record.date} - {emp.name}: status={record.status}, worked_minutes={record.worked_minutes}")

print("\n" + "="*60)
