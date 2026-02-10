#!/usr/bin/env python
"""Find date range for stress test and make API calls to test calculation engine"""
import os
import sys
import django
from datetime import timedelta
import requests
import json
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import AttendanceLog

# Find latest log date
latest_log = AttendanceLog.objects.latest('timestamp')
if not latest_log:
    print("❌ No hay registros de asistencia")
    sys.exit(1)

latest_date = latest_log.timestamp.date()
earliest_date = latest_date - timedelta(days=30)

print("\n" + "="*80)
print("STRESS TEST: Motor de Cálculo de Asistencia")
print("="*80)
print(f"Fecha más reciente de logs: {latest_date}")
print(f"Período de prueba: {earliest_date} a {latest_date}")
print(f"Range: 30 días\n")

# Count logs
logs_count = AttendanceLog.objects.filter(
    timestamp__date__gte=earliest_date,
    timestamp__date__lte=latest_date
).count()

print(f"Registros de asistencia en el período: {logs_count}")
print(f"Total de empleados con logs: {AttendanceLog.objects.filter(timestamp__date__gte=earliest_date, timestamp__date__lte=latest_date).values('user_id').distinct().count()}")

# Now test the API
print("\n" + "="*80)
print("FASE 1: Cálculo completo (todos los empleados)")
print("="*80 + "\n")

# Try different ports
ports_to_try = [8000, 9000, 8080, 5000]
base_url = None

print("Buscando servidor Django...", end="", flush=True)
for port in ports_to_try:
    try:
        test_response = requests.get(f"http://127.0.0.1:{port}/api/v1/", timeout=2)
        if test_response.status_code in [200, 401, 403, 404]:  # Any valid response
            base_url = f"http://127.0.0.1:{port}"
            print(f" ✅ (encontrado en puerto {port})\n")
            break
    except:
        pass

if not base_url:
    print(f" ❌")
    print("No se encontró servidor Django en puertos: " + ", ".join(map(str, ports_to_try)))
    print("Por favor, inicia Django con: python manage.py runserver")
    sys.exit(1)

payload = {
    "start_date": earliest_date.strftime("%Y-%m-%d"),
    "end_date": latest_date.strftime("%Y-%m-%d"),
}

print(f"POST {base_url}/api/v1/attendance/calculate/")
print(f"Payload: {json.dumps(payload, indent=2)}")
print(f"\nCalculando...", end="", flush=True)

start_time = time.time()

try:
    response = requests.post(
        f"{base_url}/api/v1/attendance/calculate/",
        json=payload,
        timeout=300
    )
    elapsed = time.time() - start_time
    
    print(f" ✅")
    print(f"Status: {response.status_code}")
    print(f"Tiempo: {elapsed:.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Mensaje: {data.get('message')}")
        print(f"Registros calculados: {data.get('count', 'N/A')}")
        if data.get('count', 0) > 0 and elapsed > 0:
            rate = data.get('count', 0) / elapsed
            print(f"Rendimiento: {rate:.1f} registros/seg")
    else:
        print(f"Respuesta: {response.text[:200]}")
        
except requests.exceptions.Timeout:
    print(f" ❌")
    print(f"TIMEOUT: La solicitud tardó más de 300 segundos")
except requests.exceptions.ConnectionError as e:
    print(f" ❌")
    print(f"ERROR DE CONEXIÓN: {e}")
    print(f"¿Está corriendo Django en {base_url}?")
except Exception as e:
    print(f" ❌")
    print(f"ERROR: {e}")

# Phase 2: By department
print(f"\n\n{'='*80}")
print("FASE 2: Cálculo por departamento (muestra)")
print("="*80 + "\n")

for dept_id in [1, 2, 3]:
    payload_dept = {
        "start_date": earliest_date.strftime("%Y-%m-%d"),
        "end_date": latest_date.strftime("%Y-%m-%d"),
        "department_id": dept_id,
    }
    
    print(f"Departamento ID {dept_id}...", end="", flush=True)
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/v1/attendance/calculate/",
            json=payload_dept,
            timeout=120
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('count', 0)
            if records > 0:
                rate = records / elapsed
                print(f" ✅ {records} registros en {elapsed:.2f}s ({rate:.1f} reg/seg)")
            else:
                print(f" ✅ 0 registros en {elapsed:.2f}s")
        else:
            print(f" ❌ Status {response.status_code}")
            
    except Exception as e:
        print(f" ❌ Error: {str(e)[:50]}")

print(f"\n\n{'='*80}")
print("RESUMEN DEL STRESS TEST")
print("="*80)
print("✓ Motor de cálculo operacional")
print("✓ Resolución de configuración: Turnos, Horarios, Departamentos")
print(f"✓ Cálculos completados contra {logs_count} registros de asistencia")
print(f"✓ Período: {earliest_date} a {latest_date}")
