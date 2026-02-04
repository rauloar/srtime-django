# 🧪 AUDITORÍA: INFRAESTRUCTURA DE TEST PARA punch/workstate

**Fecha:** 2026-02-03  
**Objetivo:** Mapear qué falta para poder testear punch/workstate correctamente  
**Status:** BLOQUEADO - Datos insuficientes  

---

## 📊 ESTADO ACTUAL DE DATOS

### En BD ahora (production DB):
```
Total registros: 2
Empleados: 1 (user_id=100, "Test User")
Fechas: 1 (2026-02-02)
Dispositivos: 1

Registro 1:
  timestamp: 2026-02-02 11:00:00 UTC
  punch: 1
  workstate: NULL
  status: 1
  punch_source: NULL

Registro 2:
  timestamp: 2026-02-02 20:00:00 UTC
  punch: 1
  workstate: NULL
  status: 1
  punch_source: NULL
```

### Problema:
- `punch=1` para AMBOS eventos (entrada y salida)
- `status=1` para AMBOS eventos
- Sin diferenciación clara de IN vs OUT
- Datos no representativos de caso real

---

## ❌ QUÉ FALTA PARA TESTEAR

### 1. DATOS REALES DE DISPOSITIVO ZKTeco

**Necesario:**
- Capturar logs REALES de un dispositivo ZKTeco en producción
- Múltiples empleados
- Múltiples días
- Múltiples tipos de jornada (entrada, salida, permisos, break)

**Por qué:**
- Solo 2 registros de test no son representativos
- No sabemos qué valores punch/status envía ZKTeco realmente
- Podrían haber ambigüedades o casos especiales

**Método sugerido:**
```bash
# Conectar a dispositivo real
# Ejecutar: python manage.py shell
# from core.services.zk import ZKService
# zk = ZKService(device_ip, device_port, device_password)
# logs = zk.get_attendance()
# for log in logs:
#   print(f"punch={log.punch} status={log.status} timestamp={log.timestamp}")
```

---

### 2. SEEDS DE TEST — TIPOS REQUERIDOS

#### 🔴 SEED TIPO A: Entrada/Salida básica

**Descripción:** Empleado llega a las 09:00, se va a las 18:00

**Datos:**
```json
{
  "user_id": "100",
  "date": "2026-02-10",
  "events": [
    {"time": "09:00", "punch": ?, "status": ?, "description": "Entrada"},
    {"time": "18:00", "punch": ?, "status": ?, "description": "Salida"}
  ]
}
```

**Incógnitas:**
- ¿Qué valor `punch` para entrada?
- ¿Qué valor `punch` para salida?
- ¿Cómo se diferencian en `status`?

**Validación esperada:**
```
Timeline debería retornar:
{
  "blocks": [
    {
      "type": "WORK",
      "start_time": "09:00",
      "end_time": "18:00",
      "duration_minutes": 540
    }
  ]
}
```

---

#### 🔴 SEED TIPO B: Con break

**Descripción:** Empleado entra 09:00, break 12:00-13:00, sale 18:00

**Datos:**
```json
{
  "user_id": "101",
  "date": "2026-02-10",
  "events": [
    {"time": "09:00", "punch": ?, "status": ?, "description": "Entrada"},
    {"time": "12:00", "punch": ?, "status": ?, "description": "Inicio break"},
    {"time": "13:00", "punch": ?, "status": ?, "description": "Fin break"},
    {"time": "18:00", "punch": ?, "status": ?, "description": "Salida"}
  ]
}
```

**Incógnitas:**
- ¿El break genera eventos con `punch` diferente?
- ¿Hay `workstate` especial para break?
- ¿La alternancia naive falla aquí (4 eventos = 2 bloques)?

**Validación esperada:**
```
Timeline debería retornar:
{
  "blocks": [
    {"type": "WORK", "start_time": "09:00", "end_time": "12:00", "duration_minutes": 180},
    {"type": "WORK", "start_time": "13:00", "end_time": "18:00", "duration_minutes": 300}
  ]
}
```

---

#### 🔴 SEED TIPO C: Sin salida registrada

**Descripción:** Empleado entra pero NO registra salida (olvidó marcar)

**Datos:**
```json
{
  "user_id": "102",
  "date": "2026-02-10",
  "events": [
    {"time": "09:00", "punch": ?, "status": ?, "description": "Entrada"},
    {"time": "13:00", "punch": ?, "status": ?, "description": "Entrada??"}
  ]
}
```

**Incógnitas:**
- ¿Cómo ZKTeco maneja entrada sin salida?
- ¿Envía evento de "fin de jornada" automático?
- ¿Puede haber evento suelto?

**Validación esperada:**
```
Timeline debería retornar:
{
  "blocks": []  # O 1 bloque si hay par incompleto?
}

Day View debería retornar:
{
  "status": "Partial"  # 1 solo evento
}
```

---

#### 🔴 SEED TIPO D: Entrada múltiple (error de dispositivo)

**Descripción:** Empleado marca entrada 2 veces (sensor falla, marca 2 veces)

**Datos:**
```json
{
  "user_id": "103",
  "date": "2026-02-10",
  "events": [
    {"time": "09:00", "punch": ?, "status": ?, "description": "Entrada 1"},
    {"time": "09:01", "punch": ?, "status": ?, "description": "Entrada 2 (error)"},
    {"time": "18:00", "punch": ?, "status": ?, "description": "Salida"}
  ]
}
```

**Incógnitas:**
- ¿Alternancia naive genera bloque (09:01→18:00)?
- ¿O lo ignora?
- ¿Hay deduplicación?

**Validación esperada:**
```
Hoy (naive):
{
  "blocks": [
    {"type": "WORK", "start_time": "09:01", "end_time": "18:00"}  # INCORRECTO
  ]
}

Ideal (con punch):
{
  "blocks": [
    {"type": "WORK", "start_time": "09:00", "end_time": "18:00"}  # CORRECTO
  ]
}
```

---

#### 🔴 SEED TIPO E: Trabajador nocturno (entrada posterior a salida)

**Descripción:** Turno nocturno: entra 22:00, sale 06:00 (día siguiente)

**Datos:**
```json
{
  "user_id": "104",
  "date": "2026-02-10",
  "events": [
    {"time": "22:00", "punch": ?, "status": ?, "description": "Entrada noche"}
  ]
}
{
  "user_id": "104",
  "date": "2026-02-11",
  "events": [
    {"time": "06:00", "punch": ?, "status": ?, "description": "Salida noche"}
  ]
}
```

**Incógnitas:**
- ¿Sistema maneja jornadas que cruzan medianoche?
- ¿Genera 2 registros en DailyAttendance o 1?
- ¿Timeline separa por fecha o agrupa jornada?

**Validación esperada:**
```
Timeline 2026-02-10:
{
  "blocks": [
    {"type": "WORK", "start_time": "22:00", "end_time": "23:59"}  # Parcial
  ]
}

Timeline 2026-02-11:
{
  "blocks": [
    {"type": "WORK", "start_time": "00:00", "end_time": "06:00"}  # Continuación?
  ]
}
```

---

#### 🟡 SEED TIPO F: Con workstate poblado

**Descripción:** Logs con `workstate` seteado (si ZKTeco lo envía)

**Datos:**
```json
{
  "user_id": "105",
  "date": "2026-02-10",
  "events": [
    {"time": "09:00", "punch": ?, "workstate": 0, "status": ?, "description": "Entrada con workstate"},
    {"time": "18:00", "punch": ?, "workstate": 1, "status": ?, "description": "Salida con workstate"}
  ]
}
```

**Incógnitas:**
- ¿Qué significan valores de workstate? (0=IN, 1=OUT?)
- ¿Son consistentes?
- ¿Podrían usarse para mapeo en FASE C?

---

#### 🟡 SEED TIPO G: Con punch_source poblado

**Descripción:** Logs con `punch_source` seteado

**Datos:**
```json
{
  "user_id": "106",
  "date": "2026-02-10",
  "events": [
    {"time": "09:00", "punch": ?, "punch_source": "FACE", "status": ?, "description": "Entrada por rostro"},
    {"time": "18:00", "punch": ?, "punch_source": "FINGER", "status": ?, "description": "Salida por huella"}
  ]
}
```

**Incógnitas:**
- ¿punch_source cambia con tipo de evento o solo con dispositivo?
- ¿Podría ser indicador alternativo?

---

## 📋 MATRIZ DE REQUERIMIENTOS

| Tipo | Descripción | Prioridad | Bloqueante | Datos necesarios |
|------|-------------|-----------|-----------|------------------|
| A | Entrada/Salida básica | 🔴 ALTA | ✅ SÍ | Valores punch para IN/OUT |
| B | Con break | 🔴 ALTA | ✅ SÍ | Mapeo de eventos múltiples |
| C | Sin salida | 🟠 MEDIA | ✅ SÍ | Manejo de eventos impares |
| D | Entrada múltiple (error) | 🟠 MEDIA | ⚠️ PARCIAL | Deduplicación, robustez |
| E | Turno nocturno | 🟡 BAJA | ⚠️ PARCIAL | Jornadas > 24h |
| F | Con workstate | 🟡 BAJA | ❌ NO | Validar si es útil |
| G | Con punch_source | 🟡 BAJA | ❌ NO | Validar si es útil |

---

## 🛠️ CÓMO CREAR SEEDS

### Opción 1: Script Python (Recomendado)

**Archivo:** `tests/seeds/attendance_log_seeds.py`

```python
from core.models import Device, Employee, AttendanceLog
from datetime import datetime, timedelta

def seed_basic_entry_exit():
    """Seed tipo A: Entrada/Salida básica"""
    device = Device.objects.first()
    employee = Employee.objects.first()
    
    AttendanceLog.objects.create(
        device=device,
        user_id=str(employee.user_id),
        timestamp=datetime(2026, 2, 10, 9, 0),
        status=0,  # Cambiar según investigación
        punch=0,   # Cambiar según investigación
    )
    AttendanceLog.objects.create(
        device=device,
        user_id=str(employee.user_id),
        timestamp=datetime(2026, 2, 10, 18, 0),
        status=1,  # Cambiar según investigación
        punch=1,   # Cambiar según investigación
    )

def seed_with_break():
    """Seed tipo B: Con break"""
    # Similar a A pero con 4 eventos

def seed_without_exit():
    """Seed tipo C: Sin salida"""
    # Similar a A pero solo 1 evento

# Ejecutar: python manage.py shell
# exec(open('tests/seeds/attendance_log_seeds.py').read())
# seed_basic_entry_exit()
```

### Opción 2: Fixture JSON

**Archivo:** `tests/fixtures/attendance_logs_seed.json`

```json
[
  {
    "model": "core.AttendanceLog",
    "pk": 100,
    "fields": {
      "device": 1,
      "user_id": "100",
      "timestamp": "2026-02-10T09:00:00Z",
      "status": 0,
      "punch": 0
    }
  },
  {
    "model": "core.AttendanceLog",
    "pk": 101,
    "fields": {
      "device": 1,
      "user_id": "100",
      "timestamp": "2026-02-10T18:00:00Z",
      "status": 1,
      "punch": 1
    }
  }
]
```

### Opción 3: Management Command

**Archivo:** `core/management/commands/seed_attendance.py`

```bash
python manage.py seed_attendance --type=basic --employee-id=100 --date=2026-02-10
```

---

## 🚦 PLAN DE TESTEO

### FASE 0: Obtener datos reales

**Bloqueante:** SÍ (toda la FASE C depende de esto)

**Tareas:**
1. Conectar a dispositivo ZKTeco REAL
2. Capturar 50-100 logs de producción
3. Documentar valores de `punch`, `status`, `workstate`
4. Identificar patrones IN/OUT

**Estimado:** 1-2 días (requiere acceso a dispositivo físico)

---

### FASE 1: Seeds de validación

**Bloqueante:** NO (puede paralelizarse con FASE 0)

**Tareas:**
1. Crear seeds tipos A-G (plantillas vacías)
2. Llenarlas CON DATOS DE FASE 0
3. Validar que Timeline/Day View funcionan

**Estimado:** 2-3 horas (una vez tenemos datos reales)

---

### FASE 2: Tests automatizados

**Bloqueante:** NO (después de seeds)

**Tareas:**
1. Test Timeline con seeds tipo A (básico)
2. Test Timeline con seeds tipo B (break)
3. Test Timeline con seeds tipo C (incompleto)
4. Test robustez (tipos D-E)
5. Test metadata (tipos F-G)

**Estimado:** 4-6 horas

---

### FASE 3: Mapeo punch/workstate

**Bloqueante:** SÍ (después de FASE 0 + 1)

**Tareas:**
1. Proponer mapping basado en datos reales
2. Implementar en Timeline/Explanation
3. Validar con todos los seeds

**Estimado:** 4-8 horas (depende de complejidad)

---

## 📌 BLOQUEANTES CRÍTICOS

| Bloqueante | Causa | Solución |
|-----------|-------|----------|
| **Datos ZKTeco reales faltando** | Solo 2 registros de test | Conectar dispositivo físico |
| **Valores punch ambiguos** | `punch=1` para entrada Y salida | Investigación con datos reales |
| **workstate nunca poblado** | Siempre NULL | Revisar si ZKTeco lo envía |
| **punch_source nunca poblado** | Siempre NULL | Revisar si ZKTeco lo envía |
| **Sin documentación ZKTeco** | pyzk no documenta mapping | Inferir de datos capturados |

---

## 🎯 RECOMENDACIÓN

### Status actual: ⛔ NO LISTO PARA FASE C

**Razón:** Falta información crítica sobre valores reales de `punch` y `status` desde dispositivo ZKTeco.

**Próximo paso:** 
1. Obtener logs reales de producción (BLOQUEANTE)
2. Documentarlos en este archivo
3. Crear seeds con esos valores
4. ENTONCES proceder con FASE C

**Sin esto:** Cualquier mapeo es especulación.

---

## 📍 DÓNDE DOCUMENTAR HALLAZGOS

Una vez obtenidos datos reales:

```markdown
### DATOS REALES DE PRODUCCIÓN (2026-02-03)

**Dispositivo:** [Modelo ZKTeco]
**IP:** [IP]
**Logs capturados:** N

**MAPPING OBSERVADO:**

Entrada (Check-In):
- punch: [valor]
- status: [valor]
- workstate: [valor o NULL]
- punch_source: [valor o NULL]

Salida (Check-Out):
- punch: [valor]
- status: [valor]
- workstate: [valor o NULL]
- punch_source: [valor o NULL]

**CASOS ESPECIALES:**

Break:
- [describir eventos]

Error de dispositivo:
- [describir eventos]

**CONFIANZA:** [% de confiabilidad del mapping]
**AMBIGÜEDADES:** [sí/no, describir]
**RECOMENDACIÓN:** [usar punch / usar status / usar workstate / combinar]
```

---

*Fin de auditoría de infraestructura de test.*  
*Documento vivo: actualizar con datos reales cuando se obtengan.*
