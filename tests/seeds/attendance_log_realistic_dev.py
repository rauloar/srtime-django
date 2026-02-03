"""
SEEDS DE DATOS REALISTAS PARA DESENVOLVIMENTO LOCAL

Proposito: Simular flujos reales de fichaje sin hardcodear logica de negocio.

SUPUESTOS DOCUMENTADOS:
- punch=0: Entrada (SIMULADO - no representa mapping real ZKTeco)
- punch=1: Salida (SIMULADO - no representa mapping real ZKTeco)
- status=1: Evento normal (SIMULADO)
- Estos valores son SOLO para desarrollo local y permitir flujo end-to-end

PROHIBIDO:
- Inferir logica de negocio desde estos seeds
- Usar como verdad del sistema
- Mergear valores como comportamiento productivo

PERMITIDO:
- Testear que Timeline/Explanation renderizan datos
- Validar queries funcionan
- Verificar frontend recibe datos

===== ESTRUCTURA DE MODELOS =====

Device (required para AttendanceLog):
  - id (PK, auto)
  - name (CharField, max_length=100)
  - ip (CharField, max_length=50)
  - port (IntegerField, default=4370)
  - password (IntegerField, default=0)
  - enabled (BooleanField, default=True)
  - serialnumber (CharField, null/blank)
  - device_name (CharField, null/blank)
  - firmware_version (CharField, null/blank)
  - created_at (DateTimeField, auto_now_add=True)

Employee (informativo, NO requerido para AttendanceLog):
  - id (PK, auto)
  - user_id (CharField, max_length=50, unique=True, db_index=True)
  - name (CharField, max_length=100, null/blank)
  - active (BooleanField, default=True)
  - email, phone, address, etc (todos null/blank)

AttendanceLog (objeto principal):
  - id (PK, auto)
  - device (FK a Device, required, on_delete=CASCADE)
  - user_id (CharField, max_length=50, db_index=True)
  - timestamp (DateTimeField, db_index=True)
  - status (IntegerField, required)
  - punch (IntegerField, required)
  - verify_mode (IntegerField, null/blank)
  - workstate (IntegerField, null/blank)
  - workcode (IntegerField, null/blank)
  - punch_source (CharField, max_length=50, null/blank)
  - raw_json (JSONField, null/blank)
  - Constraint: UNIQUE(device, user_id, timestamp)

Ubicacion: tests/seeds/attendance_log_realistic_dev.py

ZONA HORARIA: UTC-3 (Argentina) - configurada en Django settings
"""

from datetime import datetime
from django.utils import timezone
from core.models import Device, Employee, AttendanceLog

def make_timestamp(year, month, day, hour, minute):
    """Crear timestamp con zona horaria de Argentina (UTC-3).

    Usa la zona configurada en Django settings (America/Argentina/Buenos_Aires).
    """
    dt_naive = datetime(year, month, day, hour, minute)
    return timezone.make_aware(dt_naive)

def setup_base_data():
    """Crear o recuperar Device y Employee base para seeds."""
    print("\n" + "="*70)
    print("🔧 SETUP: Preparando datos base...")
    print("="*70)
    
    # Crear o obtener Device
    device, device_created = Device.objects.get_or_create(
        ip="192.168.1.100",  # IP simulada para DEV
        defaults={
            "name": "ZKTeco DEV Simulator",
            "port": 4370,
            "enabled": True,
            "serialnumber": "SIM-DEV-001",
            "firmware_version": "v1.0-dev",
        }
    )
    if device_created:
        print(f"✅ Device creado: {device.name} ({device.ip}:{device.port})")
    else:
        print(f"✅ Device existe: {device.name} ({device.ip}:{device.port})")
    
    # Crear Employees para seeds si no existen
    employees = {}
    test_employees = [
        {"user_id": 200, "name": "Empleado A"},
        {"user_id": 201, "name": "Empleado B (con break)"},
        {"user_id": 202, "name": "Empleado C (incompleto)"},
        {"user_id": 203, "name": "Empleado D (doble entrada)"},
    ]
    
    for emp_data in test_employees:
        emp, emp_created = Employee.objects.get_or_create(
            user_id=emp_data["user_id"],
            defaults={"name": emp_data["name"]}
        )
        employees[emp_data["user_id"]] = emp
        status = "✅ Creado" if emp_created else "✅ Existe"
        print(f"{status}: Employee id={emp.id} user_id={emp.user_id} ({emp.name})")
    
    return device, employees


# ============================================================================
# ESCENARIO A: Entrada / Salida básica
# ============================================================================

def seed_scenario_a(device, employees):
    """
    ESCENARIO A: Jornada normal (entrada 09:00, salida 18:00)
    
    Empleado 200 - 2026-02-10
    Timeline esperado: 1 bloque WORK 09:00→18:00 (540 min)
    Day View esperado: status=Normal, worked_minutes=540
    """
    print("\n" + "-"*70)
    print("📋 ESCENARIO A: Entrada / Salida básica")
    print("-"*70)
    
    employee = employees[200]
    date = datetime(2026, 2, 10).date()
    
    # Limpiar logs anteriores de este empleado en esta fecha
    AttendanceLog.objects.filter(
        user_id=str(employee.user_id),
        timestamp__date=date
    ).delete()
    
    # Entrada a las 09:00
    entrada = AttendanceLog.objects.create(
        device=device,
        user_id=str(employee.user_id),
        timestamp=make_timestamp(2026, 2, 10, 9, 0),
        status=1,
        punch=0,  # SIMULADO: Entrada
        verify_mode=None,
        workstate=None,
        workcode=None,
        punch_source=None,
    )
    print(f"  ✅ Entrada: {entrada.timestamp.strftime('%Y-%m-%d %H:%M:%S')} (punch=0)")
    
    # Salida a las 18:00
    salida = AttendanceLog.objects.create(
        device=device,
        user_id=str(employee.user_id),
        timestamp=make_timestamp(2026, 2, 10, 18, 0),
        status=1,
        punch=1,  # SIMULADO: Salida
        verify_mode=None,
        workstate=None,
        workcode=None,
        punch_source=None,
    )
    print(f"  ✅ Salida:  {salida.timestamp.strftime('%Y-%m-%d %H:%M:%S')} (punch=1)")
    print(f"  📊 Duración simulada: 9 horas (540 minutos)")
    print(f"  🎯 Timeline esperado: 1 bloque WORK 09:00→18:00")
    
    return [entrada, salida]


# ============================================================================
# ESCENARIO B: Jornada con break
# ============================================================================

def seed_scenario_b(device, employees):
    """
    ESCENARIO B: Entrada → Break → Retorno → Salida
    
    Empleado 201 - 2026-02-11
    09:00 Entrada
    12:00 Salida (por break)
    13:00 Entrada (retorno break)
    18:00 Salida
    
    Timeline esperado: 2 bloques WORK
      - 09:00→12:00 (180 min)
      - 13:00→18:00 (300 min)
    Total: 480 min (8 horas efectivas)
    
    Day View esperado: status=Normal, worked_minutes=480
    """
    print("\n" + "-"*70)
    print("📋 ESCENARIO B: Jornada con break")
    print("-"*70)
    
    employee = employees[201]
    date = datetime(2026, 2, 11).date()
    
    # Limpiar logs anteriores
    AttendanceLog.objects.filter(
        user_id=str(employee.user_id),
        timestamp__date=date
    ).delete()
    
    events = []
    timestamps = [
        (9, 0, "Entrada"),
        (12, 0, "Break OUT"),
        (13, 0, "Break IN"),
        (18, 0, "Salida"),
    ]
    
    for hour, minute, description in timestamps:
        log = AttendanceLog.objects.create(
            device=device,
            user_id=str(employee.user_id),
            timestamp=make_timestamp(2026, 2, 11, hour, minute),
            status=1,
            punch=0 if hour in [9, 13] else 1,  # SIMULADO: pares alternados
            verify_mode=None,
            workstate=None,
            workcode=None,
            punch_source=None,
        )
        punch_type = "IN" if log.punch == 0 else "OUT"
        print(f"  ✅ {description:20} {log.timestamp.strftime('%H:%M')} (punch={log.punch})")
        events.append(log)
    
    print(f"  📊 Duración simulada: 09:00-12:00 (3h) + 13:00-18:00 (5h) = 8 horas netas")
    print(f"  🎯 Timeline esperado: 2 bloques WORK")
    
    return events


# ============================================================================
# ESCENARIO C: Jornada incompleta (1 solo evento)
# ============================================================================

def seed_scenario_c(device, employees):
    """
    ESCENARIO C: Entrada sin salida registrada
    
    Empleado 202 - 2026-02-12
    09:00 Entrada
    (Sin salida)
    
    Timeline esperado: [] (sin bloques - evento impar se ignora)
    Day View esperado: status=Partial, worked_minutes=0
    """
    print("\n" + "-"*70)
    print("📋 ESCENARIO C: Jornada incompleta")
    print("-"*70)
    
    employee = employees[202]
    date = datetime(2026, 2, 12).date()
    
    # Limpiar logs anteriores
    AttendanceLog.objects.filter(
        user_id=str(employee.user_id),
        timestamp__date=date
    ).delete()
    
    # Solo entrada
    entrada = AttendanceLog.objects.create(
        device=device,
        user_id=str(employee.user_id),
        timestamp=make_timestamp(2026, 2, 12, 9, 0),
        status=1,
        punch=0,  # SIMULADO: Entrada
        verify_mode=None,
        workstate=None,
        workcode=None,
        punch_source=None,
    )
    print(f"  ✅ Entrada: {entrada.timestamp.strftime('%Y-%m-%d %H:%M:%S')} (punch=0)")
    print(f"  ⚠️  SIN salida registrada (evento impar)")
    print(f"  📊 Duración simulada: INDETERMINADA")
    print(f"  🎯 Timeline esperado: [] (vacío)")
    print(f"  🎯 Day View esperado: status=Partial")
    
    return [entrada]


# ============================================================================
# ESCENARIO D: Error de dispositivo (doble entrada)
# ============================================================================

def seed_scenario_d(device, employees):
    """
    ESCENARIO D: Doble entrada (error de sensor)
    
    Empleado 203 - 2026-02-13
    09:00 Entrada 1
    09:01 Entrada 2 (error de dispositivo - marca 2 veces)
    18:00 Salida
    
    Alternancia NAIVE genera:
      Bloque 1: 09:01 → 18:00 (INCORRECTO - debería ser 09:00 → 18:00)
    
    Timeline actual (NAIVE): 1 bloque 09:01→18:00 (BUGGY)
    Timeline ideal (con punch): 1 bloque 09:00→18:00 (CORRECTO)
    
    ⚠️ Este escenario expone limitación de alternancia NAIVE.
    """
    print("\n" + "-"*70)
    print("📋 ESCENARIO D: Error de dispositivo (doble entrada)")
    print("-"*70)
    
    employee = employees[203]
    date = datetime(2026, 2, 13).date()
    
    # Limpiar logs anteriores
    AttendanceLog.objects.filter(
        user_id=str(employee.user_id),
        timestamp__date=date
    ).delete()
    
    # Entrada 1 (correcta)
    entrada1 = AttendanceLog.objects.create(
        device=device,
        user_id=str(employee.user_id),
        timestamp=make_timestamp(2026, 2, 13, 9, 0),
        status=1,
        punch=0,  # SIMULADO: Entrada
        verify_mode=None,
        workstate=None,
        workcode=None,
        punch_source=None,
    )
    print(f"  ✅ Entrada 1: {entrada1.timestamp.strftime('%Y-%m-%d %H:%M:%S')} (punch=0)")
    
    # Entrada 2 (error - se repite 1 minuto después)
    entrada2 = AttendanceLog.objects.create(
        device=device,
        user_id=str(employee.user_id),
        timestamp=make_timestamp(2026, 2, 13, 9, 1),
        status=1,
        punch=0,  # SIMULADO: Entrada (error)
        verify_mode=None,
        workstate=None,
        workcode=None,
        punch_source=None,
    )
    print(f"  ⚠️  Entrada 2: {entrada2.timestamp.strftime('%Y-%m-%d %H:%M:%S')} (punch=0) [ERROR]")
    
    # Salida
    salida = AttendanceLog.objects.create(
        device=device,
        user_id=str(employee.user_id),
        timestamp=make_timestamp(2026, 2, 13, 18, 0),
        status=1,
        punch=1,  # SIMULADO: Salida
        verify_mode=None,
        workstate=None,
        workcode=None,
        punch_source=None,
    )
    print(f"  ✅ Salida:  {salida.timestamp.strftime('%Y-%m-%d %H:%M:%S')} (punch=1)")
    
    print(f"\n  ⚠️  OBSERVACIÓN DE ALTERNANCIA NAIVE:")
    print(f"      Con índice par/impar:")
    print(f"      - Índice 0 (09:00 punch=0) → ENTRADA ✓")
    print(f"      - Índice 1 (09:01 punch=0) → SALIDA (interpretado como OUT!) ✗")
    print(f"      - Índice 2 (18:00 punch=1) → ENTRADA (ignorado, no hay par)")
    print(f"      Resultado: Bloque WORK 09:01→18:00 INCORRECTO")
    print(f"\n  🎯 Timeline esperado (NAIVE): 1 bloque 09:01→18:00 (BUGGY)")
    print(f"  🎯 Timeline ideal (con punch): 1 bloque 09:00→18:00 (CORRECTO)")
    print(f"  📌 Este escenario valida necesidad de mapeo punch/status en FASE C")
    
    return [entrada1, entrada2, salida]


# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================

def main():
    """Ejecutar todos los scenarios."""
    print("\n" + "="*70)
    print("🌱 SEEDS REALISTAS DE DESARROLLO LOCAL")
    print("="*70)
    
    # Setup
    device, employees = setup_base_data()
    
    # Escenarios
    scenario_a = seed_scenario_a(device, employees)
    scenario_b = seed_scenario_b(device, employees)
    scenario_c = seed_scenario_c(device, employees)
    scenario_d = seed_scenario_d(device, employees)
    
    # Resumen
    print("\n" + "="*70)
    print("✅ SEEDS COMPLETADOS")
    print("="*70)
    print(f"\nDatos cargados en BD:")
    print(f"  Escenario A: 2 logs (Emp 200, 2026-02-10) → Jornada normal")
    print(f"  Escenario B: 4 logs (Emp 201, 2026-02-11) → Con break")
    print(f"  Escenario C: 1 log  (Emp 202, 2026-02-12) → Incompleto")
    print(f"  Escenario D: 3 logs (Emp 203, 2026-02-13) → Doble entrada (error)")
    
    print(f"\n📌 VALORES SIMULADOS (NO son mapping real de ZKTeco):")
    print(f"  punch=0 → Entrada (simulado)")
    print(f"  punch=1 → Salida (simulado)")
    print(f"  status=1 → Evento normal (simulado)")
    
    print(f"\n🧪 TESTEO MANUAL:")
    print(f"\n  Timeline A (básico):")
    print(f"    curl http://127.0.0.1:9000/api/v1/attendance/{employees[200].id}/timeline/2026-02-10/")
    print(f"    Esperado: 1 bloque WORK 09:00→18:00")
    
    print(f"\n  Timeline B (con break):")
    print(f"    curl http://127.0.0.1:9000/api/v1/attendance/{employees[201].id}/timeline/2026-02-11/")
    print(f"    Esperado: 2 bloques WORK (09:00→12:00, 13:00→18:00)")
    
    print(f"\n  Timeline C (incompleto):")
    print(f"    curl http://127.0.0.1:9000/api/v1/attendance/{employees[202].id}/timeline/2026-02-12/")
    print(f"    Esperado: [] (vacío)")
    
    print(f"\n  Timeline D (doble entrada - EXPONE BUG NAIVE):")
    print(f"    curl http://127.0.0.1:9000/api/v1/attendance/{employees[203].id}/timeline/2026-02-13/")
    print(f"    Actual:   1 bloque WORK 09:01→18:00 (INCORRECTO)")
    print(f"    Correcto: 1 bloque WORK 09:00→18:00")
    
    print(f"\n  Day View A:")
    print(f"    curl http://127.0.0.1:9000/api/v1/attendance/day/?employee_id={employees[200].id}&date=2026-02-10")
    print(f"    Esperado: status=Normal, worked_minutes=540")
    
    print(f"\n  Explanation A:")
    print(f"    curl http://127.0.0.1:9000/api/v1/attendance/{employees[200].id}/explanation/2026-02-10/")
    print(f"    Esperado: Narrativa describiendo 9 horas de trabajo")
    
    print("\n" + "="*70)
    print("📝 DOCUMENTACIÓN IMPORTANTE")
    print("="*70)
    print("\n❌ PROHIBIDO:")
    print("  - Inferir que punch=0/1 es mapping real de ZKTeco")
    print("  - Usar estos datos para validar lógica de negocio")
    print("  - Asumir que status=1 siempre significa lo mismo")
    
    print("\n✅ PERMITIDO:")
    print("  - Testear que Timeline/Explanation renderizan datos")
    print("  - Verificar que queries funcionan sin errores")
    print("  - Validar UI frontend recibe estructura esperada")
    
    print("\n📌 PRÓXIMOS PASOS:")
    print("  1. Ejecutar este script")
    print("  2. Testear endpoints con curl (arriba)")
    print("  3. Verificar que no rompen")
    print("  4. Luego: obtener datos REALES de ZKTeco para FASE C")
    
    print("\n" + "="*70)
    print("✅ FIN DE SEEDS")
    print("="*70 + "\n")


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    main()
else:
    # Si se ejecuta interactivo desde shell
    print("\n🚀 Ejecutando seeds...")
    main()
