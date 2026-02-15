# 📋 ESPECIFICACIÓN FORMAL: INTERACCIÓN SRTimeWeb ↔ ZKTeco

**Versión**: 1.0 RC1.0  
**Fecha**: 2026-02-11  
**Estado**: Definición Architecture-Locked (sin cambios de schema)  
**Base de Datos**: srtimeweb (PostgreSQL)  
**Motor DB**: 21 tablas, estructura inmutable  

---

## 🎯 OBJETIVO GENERAL

Formalizar el flujo completo de interacción entre:
- **SRTimeWeb** (Sistema HR + Cálculo de asistencia)
- **ZKTeco Device** (Terminales de control de asistencia)
- **PostgreSQL** (Almacenamiento persistente)

**Restricciones absolutas**:
- ✅ NO nuevas migraciones Django
- ✅ NO cambios de columnas existentes
- ✅ NO cambios de constraints
- ✅ NO cambios de ForeignKeys
- ✅ NO modificación de modelos
- ✅ Solo cambios de lógica/código/validaciones

---

## 📊 TABLA DE REFERENCIA RÁPIDA

| Tabla | Dominio | Rol | Fuente de Verdad | Mutable |
|-------|---------|-----|------------------|---------|
| **employees** | HR | Master datos | ✅ Sistema | ✅ Sí (HR) |
| **attendance_logs** | Dispositivo | Event store crudo | ❌ Device ZKTeco | ❌ No (inmutable) |
| **att_daily_attendance** | Motor | Resultado cálculo | ❌ Motor | ✅ Recalculable |
| **devices** | Hardware | Config terminal | ✅ Sistema | ✅ Sí |
| **users** | Espejo | Mirror device | ❌ Device ZKTeco | ❌ Manual/Seed |
| **biometric_templates** | Biometría | Enrollments | ❌ Device ZKTeco | ✅ Download only |
| **att_timetables** | Horarios | Config | ✅ Sistema | ✅ Sí |
| **att_shifts** | Horarios | Config | ✅ Sistema | ✅ Sí |
| **att_employee_shifts** | Horarios | Asignación | ✅ Sistema | ✅ Sí |
| **att_schedule_overrides** | Horarios | Excepciones | ✅ Sistema | ✅ Sí |
| **att_leaves** | Horarios | Licencias | ✅ Sistema | ✅ Sí |
| **att_holidays** | Horarios | Feriados | ✅ Sistema | ✅ Sí |

---

## 🔴 FLUJO 1: DESCARGA DE ATTENDANCE LOGS

### Componentes
- **Origen**: ZKTeco Device (terminal física)
- **Destino**: `attendance_logs` (tabla PostgreSQL)
- **Validación**: `employees.user_id`
- **Motor**: `run_import_attendance_job()` (zk_workers.py:60-190)

### Especificación

#### 1.1 Lectura desde Device

```
zk_service.get_attendance()
├─ Retorna: List[AttendanceRecord]
│  ├─ device_id: int
│  ├─ user_id: str (employee user_id)
│  ├─ timestamp: datetime
│  ├─ status: int
│  ├─ punch: int
│  ├─ verify_mode: int (optional)
│  ├─ workstate: int (optional)
│  ├─ workcode: int (optional)
│  └─ raw_json: dict (backup original)
│
└─ Garantías
   ├─ Sin deduplicación automática
   ├─ Sin modificación timestamps
   ├─ Sin preprocesamiento
   └─ Crudo desde device
```

#### 1.2 Validación Pre-Escritura

```python
# Paso 1: Validar que Employee existe
try:
    employee = Employee.objects.get(user_id=attendance_record.user_id)
except Employee.DoesNotExist:
    logger.warning(
        f"Attendance skipped: user_id={attendance_record.user_id} "
        f"no existe en employees table",
        extra={
            'device_id': attendance_record.device_id,
            'timestamp': attendance_record.timestamp,
            'severity': 'WARN_INVALID_USER'
        }
    )
    # SKIP - no crear Employee
    # SKIP - no actualizar Device.users
    continue
```

#### 1.3 Escritura Atómica

```python
from django.db import transaction

with transaction.atomic():
    attendance_log, created = AttendanceLog.objects.update_or_create(
        device_id=device_id,
        user_id=attendance_record.user_id,
        timestamp=attendance_record.timestamp,
        defaults={
            'status': attendance_record.status,
            'punch': attendance_record.punch,
            'verify_mode': attendance_record.verify_mode,
            'workstate': attendance_record.workstate,
            'workcode': attendance_record.workcode,
            'punch_source': 'DEVICE',
            'raw_json': attendance_record.to_dict(),
            'is_manual': False,
        }
    )
    if created:
        logger.info(
            f"Attendance record created: {attendance_record.user_id}",
            extra={'device_id': device_id}
        )
```

#### 1.4 Constraint Enforcement

```sql
-- Tabla: attendance_logs
-- UNIQUE constraint (automático)
UNIQUE(device_id, user_id, timestamp)

-- Meaning: Un employee solo puede tener un log por device por timestamp
-- -> Idempotencia: Si se reimporta el mismo log, se actualiza (no duplica)
```

#### 1.5 Reglas de Decisión

| Condición | Acción | Logging |
|-----------|--------|---------|
| Employee existe | INSERT/UPDATE log | ✅ INFO |
| Employee NO existe | SKIP record | ⚠️ WARN_INVALID_USER |
| Device no existe | SKIP batch | 🚨 ERROR_DEVICE_NOT_FOUND |
| Timestamp inválido | SKIP record | ⚠️ WARN_INVALID_TS |
| DB error | STOP batch | 🚨 ERROR_DB_EXCEPTION |

#### 1.6 Salida Esperada

```
run_import_attendance_job(
    job_id="abc123",
    device_id=1,
    overwrite=False,
    start_date="2026-01-01"
)

Resultado:
├─ attendance_logs: 1245 records written (new: 893, updated: 352)
├─ skipped: 23 records (Employee no existe)
├─ errors: 0
└─ transaction: COMMITTED
```

---

## 🔵 FLUJO 2: SINCRONIZACIÓN HR → DEVICE

### Componentes
- **Origen**: `employees` (table HR)
- **Destino**: ZKTeco Device (terminal física)
- **Dirección**: HR → Device ONLY (nunca inversa)
- **Motor**: `run_sync_users_job()` (zk_workers.py:394-480)

### Especificación

#### 2.1 Lectura desde employees

```python
# Leer SOLO empleados activos
employees = Employee.objects.filter(
    active=True
).order_by('user_id')

# Garantías:
# - Solo activos (inactive employees se ignoran)
# - Orden determinístico (user_id)
# - Sin modificación campos
```

#### 2.2 Preparación Datos

```python
# Para cada employee:
normalized_user = {
    'uid': int(emp.user_id) if emp.user_id.isdigit() else hash(emp.user_id) % 65535,
    'name': f"{emp.name or 'Unknown'}".strip()[:100],
    'privilege': 0,  # User-level privilege
    'password': '',  # No password sync
    'group_id': '0',  # Default group
    'user_id': emp.user_id or str(emp.id),
    'card': 0,  # No card enrollment
}
```

#### 2.3 Envío al Device

```python
with transaction.atomic():
    synced_count = 0
    failed_count = 0
    
    for emp in employees:
        try:
            result = zk_service.set_user(
                uid=normalized_user['uid'],
                name=normalized_user['name'],
                privilege=normalized_user['privilege'],
                password=normalized_user['password'],
                group_id=normalized_user['group_id'],
                user_id=normalized_user['user_id'],
                card=normalized_user['card']
            )
            
            if result:
                synced_count += 1
                logger.info(
                    f"User synced: {emp.user_id}",
                    extra={'device_id': device_id}
                )
            else:
                failed_count += 1
                logger.warning(
                    f"User sync failed: {emp.user_id}",
                    extra={
                        'device_id': device_id,
                        'reason': 'device_rejected'
                    }
                )
        except Exception as e:
            failed_count += 1
            logger.error(
                f"User sync error: {emp.user_id}",
                extra={
                    'device_id': device_id,
                    'error': str(e),
                    'exception': type(e).__name__
                }
            )
```

#### 2.4 Reglas Críticas

```
✅ DO:
├─ Leer employees.active == True
├─ Enviar campos normalizados
├─ Loggear éxitos/fallos
├─ Usar conexión persistente
└─ Hacer disable/enable del device

❌ DON'T:
├─ Modificar tabla employees
├─ Crear Employee desde device
├─ Actualizar Employee desde device
├─ Crear User en tabla users
├─ Actualizar User en tabla users
└─ Confiar en respuesta device sin validar
```

#### 2.5 Validación Post-Sync

```python
# Opcional: Verificar enrollment
# Descargar users desde device después de sync
device_users = zk_service.get_users()

for emp in synced_employees:
    device_user = next(
        (u for u in device_users if u.user_id == emp.user_id),
        None
    )
    
    if not device_user:
        logger.warning(
            f"Sync verification failed: {emp.user_id} no en device",
            extra={'device_id': device_id, 'severity': 'SYNC_VERIFY'}
        )
```

#### 2.6 Salida Esperada

```
run_sync_users_job(
    job_id="def456",
    device_id=1,
    employee_ids=None  # All active
)

Resultado:
├─ employees_read: 145
├─ employees_synced: 142 ✅
├─ employees_failed: 3 ⚠️
├─ device_connection: OK
├─ device_state: ENABLED
└─ transaction: COMMITTED
```

---

## 🟡 FLUJO 3: DESCARGA DE BIOMETRIC TEMPLATES

### Componentes
- **Origen**: ZKTeco Device (terminal física)
- **Destino**: `biometric_templates` (tabla PostgreSQL)
- **Validación**: `users` (debe existir)
- **Motor**: `get_device_templates()` (views_devices.py:325-375)

### Especificación

#### 3.1 Lectura desde Device

```python
templates = zk_service.get_templates()

# Retorna: List[BiometricTemplate]
#  ├─ uid: int (device user ID)
#  ├─ fid: int (template index/finger ID)
#  ├─ template: bytes (blob biométrico)
#  ├─ valid: int (0/1 valid flag)
#  └─ size: int (template size)
```

#### 3.2 Búsqueda de User

```python
# Paso 1: Buscar User en tabla users
user = User.objects.filter(
    device_id=device_id,
    uid=template.uid  # device uid, NOT employee user_id
).first()

if not user:
    logger.warning(
        f"Template skipped: device_id={device_id}, uid={template.uid}, "
        f"fid={template.fid} - User NOT FOUND en tabla users",
        extra={
            'device_id': device_id,
            'severity': 'WARN_USER_NOT_FOUND',
            'action': 'SKIP'
        }
    )
    # NO auto-crear User
    # NO auto-crear Employee
    skipped_count += 1
    continue
```

#### 3.3 Determinación de Tipo

```python
# Mapeo device-agnostic:
# fid 0-9 = Finger (0=thumb, 1=index, ..., 9=other)
# fid 10+ = Face (10=face1, 11=face2, ...)
# special = Palm (device-dependent)

if template.fid < 10:
    template_type = 'FINGER'
elif template.fid >= 10:
    template_type = 'FACE'
else:
    template_type = 'UNKNOWN'
```

#### 3.4 Escritura Atómica

```python
with transaction.atomic():
    biometric_template, created = BiometricTemplate.objects.update_or_create(
        user=user,
        type=template_type,
        index=template.fid,
        defaults={
            'valid': template.valid,
            'data': str(template.template_blob),
            'version': str(template.size) if hasattr(template, 'size') else None,
        }
    )
    
    if created:
        logger.info(
            f"Template created: uid={user.uid}, type={template_type}, fid={template.fid}",
            extra={'device_id': device_id}
        )
    else:
        logger.info(
            f"Template updated: uid={user.uid}, type={template_type}, fid={template.fid}",
            extra={'device_id': device_id}
        )
    
    saved_count += 1
```

#### 3.5 Constraint Enforcement

```sql
-- Tabla: biometric_templates
-- UNIQUE constraint (automático)
UNIQUE(user_id, type, index)

-- Meaning: Un user solo puede tener UN template por tipo y índice
-- -> Idempotencia: Si se reimporta, se actualiza (no duplica)
```

#### 3.6 Reglas de Decisión

| Condición | Acción | Logging |
|-----------|--------|---------|
| User existe | INSERT/UPDATE template | ✅ INFO |
| User NO existe | SKIP record | ⚠️ WARN_USER_NOT_FOUND |
| Template válido | Guardar con valid=1 | ✅ INFO |
| Template inválido | Guardar con valid=0 | ℹ️ DEBUG |
| Device error | STOP batch | 🚨 ERROR_DEVICE |

#### 3.7 Salida Esperada

```
GET /api/v1/devices/1/templates/

Resultado:
{
  "success": true,
  "message": "Templates guardados: 847, Omitidos (sin usuario): 12, Errores: 0",
  "saved": 847,
  "skipped": 12,
  "errors": 0,
  "details": {
    "skipped_uids": [15, 42, 99],  // users que no existen
    "error_details": []
  }
}
```

---

## 🟢 FLUJO 4: USERS (ESPEJO DEL DEVICE)

### Componentes
- **Tabla**: `users` (PostgreSQL)
- **Rol**: Mirror técnico del estado del device
- **NO es**: Fuente de verdad
- **NO es**: Controlado por HR

### Especificación

#### 4.1 Ciclo de Vida

```
Device ENROLLMENT → User MANUAL SEED / DOWNLOAD
     ↓
     User record en tabla (opcional)
     ↓
     Si User existe: BiometricTemplate puede crearse
     Si User NO existe: BiometricTemplate se skippea
     ↓
     attendance_logs usan Employee.user_id (no User)
```

#### 4.2 Poblamiento

```
Opción A: Manual seed (inicial)
  ├─ python manage.py seed_django
  └─ Crea users para test

Opción B: Download (opcional)
  ├─ run_download_users_job()
  ├─ Loggea users en device (no modifica tabla)
  └─ NO crea User records

Opción C: Manual API
  ├─ Admin panel
  └─ Crear User manualmente si necesario

NO Opción D: Auto-create
  ❌ Nunca auto-crear User desde device enrollment
  ❌ Nunca auto-crear User desde attendance
  ❌ Nunca auto-crear Employee
```

#### 4.3 Garantías

```
users.user_id (CharField):
├─ Mapea a employees.user_id
├─ Pero es VARCHAR, NO FK
├─ Nunca usar para JOIN automático
├─ Solo referencia lógica para logs
└─ Actualización manual si necesario

users.device_id (FK):
├─ CASCADE delete
├─ Si device se borra, users se borran
└─ Correcto

users.uid (unique per device):
├─ UNIQUE(device, uid)
├─ Espejo de device uid
└─ No racionalizables
```

#### 4.4 Flujo Correcto

```
HR decides: "Create employee Juan"
  ↓
Employee.create(user_id="EMP001", name="Juan")
  ↓
system admin: run_sync_users_job()
  ↓
Device now has user uid=X, user_id="EMP001"
  ↓
Option: Admin creates User record manually OR skips it
  ↓
attendance_logs.import: User arrives with user_id="EMP001"
  ↓
Motor calculates using Employee.user_id="EMP001"
  ↓
User record (if exists) is just for reference, NOT used
```

---

## 🟣 FLUJO 5: MOTOR DE CÁLCULO

### Componentes
- **Entrada**: `attendance_logs` (raw events)
- **Entrada**: `employees` (master data)
- **Entrada**: `att_*` tables (horarios, shifts, leaves)
- **Salida**: `att_daily_attendance` (resultados)
- **Motor**: `resolve_schedule_unified()` (core/engines/v2.py)

### Especificación

#### 5.1 Flujo Input

```python
# Para cada (employee, date) en rango:
daily_attendance = DailyAttendance.objects.filter(
    employee=emp,
    date=target_date
).first()

# Si no existe, CREAR nuevo (recalculable)
# Si existe y state=CALCULATED, SKIPPEAR (inmutable)
# Si existe y state=SUPERSEDED, REPLACEABLE
```

#### 5.2 Entrada de Datos

```python
# Paso 1: Cargar timetable para el día
timetable = resolve_employee_timetable(
    employee=emp,
    date=target_date,
    on_date=target_date
)

# Paso 2: Cargar attendance logs del día
logs = AttendanceLog.objects.filter(
    device__in=emp_devices,  # Múltiples dispositivos OK
    user_id=emp.user_id,
    timestamp__date=target_date
).order_by('timestamp')

# Paso 3: Cargar licencias del día
leaves = Leave.objects.filter(
    employee=emp,
    start_time__date=target_date,
    status='Approved'
)

# Paso 4: Cargar feriados
holidays = Holiday.objects.filter(
    start_date__lte=target_date,
    end_date__gte=target_date
)
```

#### 5.3 Cálculo

```python
# Motor: resolve_schedule_unified(
#     timetable=timetable,
#     logs=logs,
#     on_date=target_date
# )

# Outputs:
# ├─ status: "Normal", "Late", "Early", "Absent", "Leave", etc.
# ├─ check_in: datetime
# ├─ check_out: datetime
# ├─ worked_minutes: int
# ├─ late_minutes: int
# ├─ overtime_minutes: int
# ├─ break_minutes: int
# └─ net_worked_minutes: int
```

#### 5.4 Escritura Resultado

```python
with transaction.atomic():
    daily_attendance, created = DailyAttendance.objects.update_or_create(
        employee=emp,
        date=target_date,
        defaults={
            'timetable': timetable,
            'check_in': calculated.check_in,
            'check_out': calculated.check_out,
            'on_duty': calculated.on_duty,
            'off_duty': calculated.off_duty,
            'late_minutes': calculated.late_minutes,
            'early_minutes': calculated.early_minutes,
            'worked_minutes': calculated.worked_minutes,
            'overtime_minutes': calculated.overtime_minutes,
            'break_minutes': calculated.break_minutes,
            'net_worked_minutes': calculated.net_worked_minutes,
            'status': calculated.status,
            'is_absent': calculated.is_absent,
        }
    )
    
    logger.info(
        f"Attendance calculated: {emp.user_id} @ {target_date}",
        extra={
            'employee_id': emp.id,
            'status': calculated.status,
            'worked_minutes': calculated.worked_minutes
        }
    )
```

#### 5.5 Garantías

```
✅ attendance_logs: Completamente ignorados si Employee no existe
   └─ Ya validado en import_attendance

✅ employees: Fuente de verdad para cálculo
   └─ Solo ACTIVE employees

✅ att_daily_attendance: Resultados calculables
   └─ Pueden ser recalculados sin perder datos

❌ users: NUNCA usado en cálculo (es decorativo)
   └─ Motor usa employees SOLO

❌ biometric_templates: NUNCA usado en cálculo
   └─ No relevante para asistencia
```

---

## ⚪ CONSISTENCIA ENTRE TABLAS

### 5.1 Validaciones de Integridad

#### Cross-Table Constraints

```
1. AttendanceLog.user_id → Employee.user_id
   ├─ Type: VARCHAR → VARCHAR
   ├─ FK: NO (por diseño)
   ├─ Validación: En lógica de import
   └─ Garantía: Employee DEBE existir

2. BiometricTemplate.user_id → User.id
   ├─ Type: FK (real)
   ├─ Cascade: ON DELETE CASCADE
   ├─ Guarantee: User DEBE existir
   └─ Automatizado

3. User.device_id → Device.id
   ├─ Type: FK (real)
   ├─ Cascade: ON DELETE CASCADE
   ├─ Guarantee: Device DEBE existir
   └─ Automatizado

4. AttendanceLog.device_id → Device.id
   ├─ Type: FK (real)
   ├─ Cascade: ON DELETE CASCADE
   ├─ Guarantee: Device DEBE existir
   └─ Automatizado

5. DailyAttendance.employee_id → Employee.id
   ├─ Type: FK (real)
   ├─ Guarantee: Employee DEBE existir
   └─ Automatizado
```

#### Validación de Usuarios

```python
# Validación obligatoria en import_attendance:
if not Employee.objects.filter(user_id=log.user_id).exists():
    logger.warning(f"Skip: employee user_id={log.user_id} not found")
    continue  # NO crear Employee

# Validación en get_device_templates:
if not User.objects.filter(device_id=device_id, uid=template.uid).exists():
    logger.warning(f"Skip: user device_id={device_id}, uid={template.uid} not found")
    continue  # NO crear User

# Validación en resolve_employee_timetable:
if not Employee.objects.filter(id=emp.id, active=True).exists():
    raise ValueError(f"Employee {emp.id} must exist and be active")
```

### 5.2 No Circular Dependencies

```
Flujos VÁLIDOS:
  ├─ HR → Device: ✅ employees → set_user() → device
  ├─ Device → DB: ✅ device → get_attendance() → attendance_logs
  ├─ Device → DB: ✅ device → get_templates() → biometric_templates
  ├─ DB → Motor: ✅ attendance_logs → calculate → att_daily_attendance
  └─ Motor → Report: ✅ att_daily_attendance → export

Flujos INVÁLIDOS:
  ├─ Device → HR: ❌ NUNCA device → create/update Employee
  ├─ Device → HR: ❌ NUNCA run_download_users_job() → update Employee
  ├─ Attendance → HR: ❌ NUNCA attendance_logs → modify Employee
  └─ Motor → HR: ❌ NUNCA att_daily_attendance → update Employee
```

---

## 🧪 VALIDACIÓN EN CÓDIGO

### 6.1 Checklist de Cumplimiento

```python
# run_import_attendance_job()
def test_import_attendance_validates_employee():
    # Crear device
    device = Device.objects.create(name="TEST", ip="192.168.1.1")
    
    # Crear employee
    emp = Employee.objects.create(user_id="EMP001", name="Juan")
    
    # Mock attendance con user_id válido
    logs = [
        MockLog(user_id="EMP001", timestamp=now),  # ✅ Existe
        MockLog(user_id="INVALID", timestamp=now),  # ❌ No existe
    ]
    
    result = import_attendance(device, logs)
    
    # Assertions:
    assert result.saved == 1  # Solo EMP001
    assert result.skipped == 1  # INVALID fue skippado
    assert result.logs.filter(level='WARN').filter('INVALID').exists()


# run_sync_users_job()
def test_sync_users_never_creates_employee():
    emp = Employee.objects.create(user_id="EMP002", active=True)
    device = Device.objects.create(name="TEST")
    
    sync_users(device, [emp])
    
    # Assertions:
    assert Employee.objects.count() == 1  # No creó más
    assert User.objects.count() == 0  # No creó User
    assert device.last_sync_at is not None


# get_device_templates()
def test_get_templates_skips_missing_user():
    device = Device.objects.create(name="TEST")
    
    # Mock template de uid=99 que NO existe en Users
    templates = [
        MockTemplate(uid=99, fid=0),  # ❌ User no existe
    ]
    
    result = get_device_templates(device, templates)
    
    # Assertions:
    assert result.saved == 0
    assert result.skipped == 1
    assert result.logs.filter(level='WARN').filter('USER_NOT_FOUND').exists()
```

### 6.2 Regresión Test Suite

```bash
# Antes de cualquier cambio:
python manage.py test

# Esperado:
# ✅ 147 tests PASSED
# ⏭️ 8 tests SKIPPED (por diseño)
# ❌ 0 tests FAILED

# NO se permiten cambios que rompan esta línea base
```

---

## 📝 NO CAMBIAR BAJO NINGUNA CIRCUNSTANCIA

```
❌ core/models.py
   ├─ AttendanceLog schema
   ├─ Employee schema
   ├─ User schema
   ├─ Device schema
   ├─ BiometricTemplate schema
   └─ Cualquier FK existente

❌ core/migrations/
   ├─ NO nuevas migraciones
   ├─ NO cambios a existentes
   └─ Validación: python manage.py makemigrations --check

❌ Serializadores públicos
   ├─ AttendanceLogSerializer
   ├─ EmployeeSerializer
   ├─ DeviceSerializer
   └─ API contract

❌ Motores de cálculo
   ├─ resolve_schedule_unified()
   ├─ Lógica puntuación
   └─ Algoritmo asistencia

❌ API Endpoints (versión)
   ├─ POST /api/v1/devices/{id}/import-attendance/
   ├─ POST /api/v1/devices/{id}/sync-users/
   ├─ POST /api/v1/devices/{id}/templates/
   └─ GET /api/v1/devices/{id}/users/
```

---

## ✨ CAMBIOS PERMITIDOS (SOLO LÓGICA/LOGGING)

```
✅ zk_workers.py
   ├─ Validaciones mejoradas
   ├─ Logging más detallado
   ├─ Error handling
   └─ Transacciones

✅ views_devices.py
   ├─ Logging más explícito
   ├─ Validaciones pre-escritura
   ├─ Mejor manejo de errores
   └─ Sin cambios de respuesta API

✅ Services (core/services/)
   ├─ Normalizaciones de datos
   ├─ Validaciones
   ├─ Logging
   └─ Error resilience

✅ Logging/Diagnostics
   ├─ Nuevos campos de context
   ├─ Nuevos log levels
   ├─ Structured logging
   └─ Audit trails

✅ Tests
   ├─ Nuevos tests
   ├─ Validación de lógica
   ├─ Regresión checks
   └─ Coverage improvement
```

---

## 🎯 TABLA FINAL: RESPONSABILIDADES

| Componente | Pertenece a | Responsabilidad |
|-----------|------------|------------------|
| `employees` | HR System | Master data, single source of truth |
| `attendance_logs` | Device Import | Raw event store, immutable |
| `att_daily_attendance` | Motor | Calculated results, recalculable |
| `devices` | System Config | Terminal metadata |
| `users` | Device Mirror | Technical mirror, manual seed |
| `biometric_templates` | Device Mirror | Template cache, download only |
| `att_timetables` | HR Config | Shift templates |
| `att_shifts` | HR Config | Work schedules |
| `att_employee_shifts` | HR Config | Employee assignments |
| `att_schedule_overrides` | HR Config | Exceptions |
| `att_leaves` | HR Config | Approved leaves |
| `att_holidays` | HR Config | Company holidays |

---

## 📋 RESUMEN EJECUTIVO

### Regla de Oro 🏆

```
EMPLOYEES es la FUENTE DE VERDAD
    ↓
run_sync_users_job() replica a DEVICE
    ↓
DEVICE produce ATTENDANCE_LOGS
    ↓
Motor escribe DAILY_ATTENDANCE
    
Nunca en reversa ↗️
```

### Flujos Permitidos ✅

1. **HR → Device** via `run_sync_users_job()`
2. **Device → DB** via `run_import_attendance_job()`
3. **Device → DB** via `get_device_templates()`
4. **DB → Cálculo** via `resolve_schedule_unified()`

### Flujos Prohibidos ❌

1. Device → Employee (nunca)
2. Attendance → Employee (nunca)
3. Motor → Employee (nunca)
4. Circular sync (nunca)

### Validaciones Obligatorias ✅

1. Employee DEBE existir antes de usar attendance_log
2. User DEBE existir antes de usar biometric_template
3. Device DEBE existir antes de enrolled users
4. Horario DEBE existir antes de calcular asistencia

---

**FIN DE ESPECIFICACIÓN FORMAL**

Version: 1.0 RC1.0  
Lock: ARCHITECTURE-STABLE (no schema changes permitted)  
Review: Arquitecto Senior Backend  
Date: 2026-02-11
