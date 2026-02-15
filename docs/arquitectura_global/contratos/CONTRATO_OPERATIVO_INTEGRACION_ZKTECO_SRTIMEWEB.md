# CONTRATO OPERATIVO DE INTEGRACIÓN ZKTeco ↔ SRTimeWeb

**Versión**: 1.0.0  
**Fecha de Emisión**: 2026-02-12  
**Estado**: VIGENTE - Beta Ready  
**Clasificación**: Documento Técnico Interno - Arquitectura de Sistemas  
**Ámbito**: Integración Hardware-Software en Sistema de Gestión de Asistencia  

---

## REGISTRO DE AUTORIZACIÓN

| Rol | Nombre | Firma Digital | Fecha |
|-----|--------|---------------|-------|
| Arquitecto Senior de Sistemas HR | [FIRMA REQUERIDA] | [HASH] | 2026-02-12 |
| Responsable Técnico Backend | [FIRMA REQUERIDA] | [HASH] | 2026-02-12 |
| Responsable Base de Datos | [FIRMA REQUERIDA] | [HASH] | 2026-02-12 |
| Líder de Proyecto SRTimeWeb | [FIRMA REQUERIDA] | [HASH] | 2026-02-12 |

---

## GLOSARIO DE TÉRMINOS

- **Employee**: Registro maestro de empleado en el sistema de recursos humanos. Única fuente de verdad de identidad.
- **Device**: Terminal biométrico ZKTeco físico conectado a la red corporativa.
- **User**: Registro espejo técnico que representa un usuario enrollado en un dispositivo específico. No es fuente de verdad.
- **Attendance Log**: Evento crudo de marcación capturado por el dispositivo. Inmutable.
- **Daily Attendance**: Registro calculado de asistencia diaria. Recalculable.
- **Biometric Template**: Plantilla biométrica (huella dactilar, rostro, palma) almacenada en dispositivo y opcionalmente en base de datos.
- **Ingesta**: Proceso de importación de eventos desde dispositivo hacia base de datos.
- **Sincronización**: Proceso unidireccional de replicación de empleados desde HR hacia dispositivo.

---

## 1. PRINCIPIOS RECTORES

### 1.1 Principio de Fuente Única de Verdad

La tabla `employees` es la única y exclusiva fuente de verdad para identidad de personas en el sistema SRTimeWeb. Ningún otro sistema, dispositivo o componente puede crear, modificar o eliminar registros de empleados sin pasar por el subsistema de recursos humanos.

**Corolario**: Los dispositivos ZKTeco, por diseño arquitectónico, son consumidores de información de identidad, no productores.

### 1.2 Principio de Flujo Unidireccional

Todos los flujos de datos relacionados con identidad deben seguir la dirección:

```
Sistema HR → Dispositivo ZKTeco
```

Está estrictamente prohibida la dirección inversa para datos de identidad:

```
Dispositivo ZKTeco → Sistema HR [PROHIBIDO]
```

Los dispositivos pueden ser fuente de eventos de asistencia, pero no de identidad.

### 1.3 Principio de Inmutabilidad de Eventos

Los eventos de asistencia capturados por dispositivos son registros históricos inmutables. Una vez ingresados en la tabla `attendance_logs`, no deben ser modificados. Solo pueden ser marcados como editados manualmente con auditoría completa.

### 1.4 Principio de Separación de Dominios

El sistema SRTimeWeb opera bajo una arquitectura de dominios separados:

- **Dominio HR**: Gestión de empleados, departamentos, puestos.
- **Dominio Device**: Configuración de terminales, enrollments biométricos.
- **Dominio Ingesta**: Importación cruda de eventos de asistencia.
- **Dominio Motor**: Cálculo y procesamiento de reglas de asistencia.
- **Dominio Horarios**: Configuración de turnos, excepciones, licencias.

Cada dominio tiene responsabilidades claramente delimitadas sin superposición.

### 1.5 Principio de Idempotencia

Todas las operaciones de ingesta y sincronización deben ser idempotentes. La ejecución múltiple de una operación con los mismos parámetros debe producir el mismo resultado sin efectos no deseados.

### 1.6 Principio de Validación en Ingreso

La validación de integridad referencial lógica (Employee existe) debe realizarse en el momento de ingesta, no durante el cálculo. Los registros que no cumplen validación deben ser rechazados con logging explícito.

### 1.7 Principio de Abstracción de Hardware

El sistema debe estructurarse de forma que permita futuras integraciones con otras marcas de dispositivos biométricos sin alterar la lógica de negocio ni el modelo de datos.

---

## 2. MODELO DE DATOS INVOLUCRADO

### 2.1 Diagrama de Entidades y Relaciones

```
DOMINIO HR (Fuente de Verdad)
============================
employees (id, user_id UNIQUE, name, department_id, position_id, active, ...)
    ├─ user_id: VARCHAR(50) - Identificador único del empleado
    ├─ active: BOOLEAN - Estado actual del empleado
    └─ ÍNDICE: user_id (UNIQUE, indexed)

departments (id, name, code, company_id, parent_id)
positions (id, name, code, description)
companies (id, name, code, address, website, logo_path)


DOMINIO DEVICE (Configuración Hardware)
=======================================
devices (id, name, ip, port, password, zone_rel_id, enabled, serialnumber, ...)
    ├─ enabled: BOOLEAN - Estado operativo del terminal
    ├─ last_seen: TIMESTAMP - Última conexión exitosa
    └─ user_count, face_count, fp_count, transaction_count

users (id, device_id, uid, name, privilege, user_id, card, ...)
    ├─ device_id: FK → devices (CASCADE)
    ├─ uid: INTEGER - ID interno del dispositivo
    ├─ user_id: VARCHAR(50) - Referencia lógica a employees.user_id (NO FK)
    └─ CONSTRAINT: UNIQUE(device_id, uid)

biometric_templates (id, user_id, type, index, valid, data, version, ...)
    ├─ user_id: FK → users (CASCADE)
    ├─ type: ENUM (FINGER, FACE, PALM)
    └─ CONSTRAINT: UNIQUE(user_id, type, index)


DOMINIO INGESTA (Eventos Crudos)
=================================
attendance_logs (id, device_id, user_id, timestamp, status, punch, ...)
    ├─ device_id: FK → devices (CASCADE)
    ├─ user_id: VARCHAR(50) - Referencia lógica a employees.user_id (NO FK)
    ├─ timestamp: TIMESTAMP - Momento exacto del evento
    ├─ status: INTEGER - Estado del evento
    ├─ punch: INTEGER - Tipo de marcación
    ├─ raw_json: JSONB - Datos originales del dispositivo
    ├─ is_manual: BOOLEAN - Indica si fue editado manualmente
    └─ CONSTRAINT: UNIQUE(device_id, user_id, timestamp)

import_batches (id, device_id, imported_at, count)
    └─ Metadata de lotes de importación


DOMINIO HORARIOS (Configuración Laboral)
========================================
att_timetables (id, name, on_duty_time, off_duty_time, late_allow_minutes, ...)
att_shifts (id, name, cycle_days)
att_shift_timetables (id, shift_id, timetable_id, day_index)
att_employee_shifts (id, scope, employee_id, department_id, shift_id, start_date, end_date)
att_schedule_overrides (id, employee_id, date, timetable_id)
att_leaves (id, employee_id, leave_type, start_time, end_time, reason, status)
att_holidays (id, name, start_date, end_date)


DOMINIO MOTOR (Resultados Calculados)
======================================
att_daily_attendance (id, employee_id, date, timetable_id, check_in, check_out, ...)
    ├─ employee_id: FK → employees (CASCADE)
    ├─ timetable_id: FK → att_timetables (SET_NULL)
    ├─ date: DATE - Día de la asistencia
    ├─ worked_minutes, late_minutes, overtime_minutes, ...
    ├─ status: ENUM (Normal, Late, Early, Absent, Leave, ...)
    └─ Recalculable en cualquier momento


DOMINIO SISTEMA (Infraestructura)
==================================
jobs (id, type, device_id, status, progress, started_at, finished_at, error)
job_logs (id, job_id, device_id, level, message, timestamp)
settings (key PRIMARY KEY, value, description)
zones (id, name, code, description)
```

### 2.2 Restricciones de Integridad Críticas

#### 2.2.1 Constraint Físico (Base de Datos)

```sql
-- Tabla: attendance_logs
ALTER TABLE attendance_logs 
ADD CONSTRAINT uix_att_log 
UNIQUE (device_id, user_id, timestamp);

-- Garantiza: Un empleado solo puede tener una marcación por dispositivo por timestamp exacto
-- Idempotencia: Reimportación actualiza, no duplica
```

#### 2.2.2 Constraint Lógico (Aplicación)

```python
# Validación obligatoria en ingesta:
if not Employee.objects.filter(user_id=log.user_id).exists():
    logger.warning(f"Attendance skipped: Employee {log.user_id} not found")
    continue  # Rechazar evento

# Garantiza: Solo se ingresan eventos de empleados que existen en HR
# Prevención: Datos huérfanos que no pueden procesarse por el motor
```

### 2.3 Campos de Auditoría

Todas las tablas de dominio transaccional deben incluir:

- `created_at`: Timestamp de creación (auto)
- `updated_at`: Timestamp de última modificación (auto)

Tablas críticas adicionalmente:

- `edited_by`: Usuario que realizó edición manual
- `edited_at`: Timestamp de edición manual
- `edited_reason`: Justificación de edición manual

---

## 3. FLUJOS OPERATIVOS OFICIALES

### 3.1 Flujo 1: Sincronización HR → Device

**Nombre Técnico**: `run_sync_users_job()`  
**Dirección**: Sistema HR → Dispositivo ZKTeco  
**Frecuencia**: Bajo demanda o programada (típicamente diaria)  
**Criticidad**: MEDIA (afecta enrollment en dispositivos)  

#### 3.1.1 Descripción

Proceso unidireccional mediante el cual los empleados activos del sistema HR son replicados hacia los dispositivos ZKTeco para permitir su identificación biométrica.

#### 3.1.2 Secuencia de Operaciones

```
1. INICIO
   └─ Validar: Device existe y está activo

2. LECTURA HR
   └─ SELECT * FROM employees WHERE active = TRUE ORDER BY user_id

3. CONEXIÓN DEVICE
   ├─ Conectar a Device (IP:Puerto)
   ├─ Autenticar con password
   └─ Deshabilitar device (modo mantenimiento)

4. ITERACIÓN POR EMPLEADO
   Para cada employee en employees_activos:
       ├─ Normalizar datos:
       │  ├─ uid = hash(employee.user_id) % 65535
       │  ├─ name = employee.name[:100].strip()
       │  ├─ privilege = 0 (user-level)
       │  ├─ password = "" (no password sync)
       │  ├─ group_id = "0"
       │  ├─ user_id = employee.user_id
       │  └─ card = 0
       │
       ├─ Enviar: device.set_user(uid, name, privilege, ...)
       │
       └─ Registrar resultado:
          ├─ Si exitoso: synced_count++
          └─ Si fallido: failed_count++, logger.warning()

5. HABILITACIÓN DEVICE
   └─ Habilitar device (modo operativo)

6. DESCONEXIÓN
   └─ Cerrar conexión con device

7. REPORTE
   └─ JobLog: {synced_count, failed_count, duration}

8. FIN
```

#### 3.1.3 Reglas de Negocio

- Solo empleados con `active = TRUE` son sincronizados.
- Si un empleado ya existe en el dispositivo con el mismo `user_id`, se actualiza (no duplica).
- Si un empleado ha sido desactivado (`active = FALSE`), NO se elimina del dispositivo automáticamente. La eliminación es una operación manual separada.
- La sincronización NO modifica ningún registro en la tabla `employees`.
- La sincronización NO crea registros en la tabla `users` (espejo técnico). Esto es opcional y manual.

#### 3.1.4 Validaciones

- El dispositivo debe estar en estado `enabled = TRUE`.
- El dispositivo debe ser alcanzable en la red.
- Cada empleado debe tener `user_id` no nulo y no vacío.

#### 3.1.5 Manejo de Errores

| Error | Acción | Logging |
|-------|--------|---------|
| Device inalcanzable | STOP job, estado FAILED | ERROR con IP/Port |
| Device rechaza usuario | SKIP usuario, continuar | WARNING con user_id |
| Timeout de conexión | RETRY 3 veces, luego STOP | ERROR con detalles |
| Credenciales inválidas | STOP job, estado FAILED | ERROR de autenticación |

#### 3.1.6 Postcondiciones

- Dispositivo contiene lista actualizada de empleados activos.
- JobLog contiene registro completo de operación.
- Sistema no ha modificado tabla `employees`.

---

### 3.2 Flujo 2: Ingesta Device → DB (Attendance Logs)

**Nombre Técnico**: `run_import_attendance_job()`  
**Dirección**: Dispositivo ZKTeco → Base de Datos  
**Frecuencia**: Bajo demanda o programada (típicamente cada 15-30 minutos)  
**Criticidad**: ALTA (datos primarios para nómina)  

#### 3.2.1 Descripción

Proceso de extracción de eventos de asistencia desde dispositivos ZKTeco e ingesta cruda en la tabla `attendance_logs` sin preprocesamiento ni transformación de datos.

#### 3.2.2 Secuencia de Operaciones

```
1. INICIO
   └─ Validar: Device existe

2. CONEXIÓN DEVICE
   ├─ Conectar a Device (IP:Puerto)
   ├─ Autenticar con password
   └─ Deshabilitar device (modo mantenimiento)

3. DESCARGA EVENTOS
   ├─ Obtener: device.get_attendance()
   │  └─ Parámetros opcionales: start_date (si overwrite = FALSE)
   │
   └─ Resultado: List[AttendanceRecord]
      Cada record contiene:
      ├─ user_id: VARCHAR
      ├─ timestamp: DATETIME
      ├─ status: INTEGER
      ├─ punch: INTEGER
      ├─ verify_mode: INTEGER (opcional)
      ├─ workstate: INTEGER (opcional)
      └─ workcode: INTEGER (opcional)

4. VALIDACIÓN PRE-INGESTA
   Para cada attendance_record:
       ├─ Validar: Employee.objects.filter(user_id=record.user_id).exists()
       │
       ├─ Si NO existe:
       │  ├─ logger.warning("Attendance skipped: Employee not found", 
       │  │                extra={user_id, timestamp, device_id})
       │  ├─ skipped_count++
       │  └─ SKIP record
       │
       └─ Si SÍ existe:
          └─ Continuar a ingesta

5. INGESTA ATÓMICA
   BEGIN TRANSACTION
       Para cada attendance_record válido:
           AttendanceLog.objects.update_or_create(
               device_id=device_id,
               user_id=record.user_id,
               timestamp=record.timestamp,
               defaults={
                   'status': record.status,
                   'punch': record.punch,
                   'verify_mode': record.verify_mode,
                   'workstate': record.workstate,
                   'workcode': record.workcode,
                   'punch_source': 'DEVICE',
                   'raw_json': record.to_dict(),
                   'is_manual': False
               }
           )
           ├─ Si created: saved_count++
           └─ Si updated: updated_count++
   COMMIT TRANSACTION

6. HABILITACIÓN DEVICE
   └─ Habilitar device (modo operativo)

7. DESCONEXIÓN
   └─ Cerrar conexión con device

8. REPORTE
   └─ JobLog: {saved_count, updated_count, skipped_count, duration}

9. FIN
```

#### 3.2.3 Reglas de Negocio

- Los eventos se ingresan CRUDOS, sin modificación de timestamp ni campos.
- El constraint `UNIQUE(device_id, user_id, timestamp)` controla automáticamente duplicados exactos.
- Si un evento ya existe (mismo device, user_id, timestamp), se actualiza (comportamiento `update_or_create`).
- Solo se ingresan eventos cuyo `user_id` corresponde a un `Employee` existente.
- Los eventos rechazados (Employee no existe) se registran en logs pero NO en base de datos.
- El campo `raw_json` preserva el evento original completo del dispositivo para auditoría.

#### 3.2.4 Validaciones

- Device debe existir en tabla `devices`.
- Cada evento debe tener `user_id`, `timestamp`, `status` y `punch` no nulos.
- Timestamp debe estar en formato ISO 8601 válido.
- Employee correspondiente a `user_id` debe existir en tabla `employees`.

#### 3.2.5 Manejo de Errores

| Error | Acción | Logging |
|-------|--------|---------|
| Device inalcanzable | STOP job, estado FAILED | ERROR con IP/Port |
| Employee no existe | SKIP evento, continuar | WARNING con user_id y timestamp |
| Timestamp inválido | SKIP evento, continuar | WARNING con raw data |
| DB constraint violation | SKIP evento (duplicado), continuar | DEBUG (duplicado esperado) |
| Transacción falla | ROLLBACK, STOP job | ERROR con stacktrace |

#### 3.2.6 Postcondiciones

- Tabla `attendance_logs` contiene todos los eventos válidos.
- Eventos rechazados están documentados en `job_logs`.
- Dispositivo permanece en modo operativo.
- Constraint de unicidad garantiza idempotencia.

---

### 3.3 Flujo 3: Descarga Device → DB (Biometric Templates)

**Nombre Técnico**: `get_device_templates()`  
**Dirección**: Dispositivo ZKTeco → Base de Datos  
**Frecuencia**: Bajo demanda (típicamente post-enrollment)  
**Criticidad**: MEDIA (metadata de enrollments)  

#### 3.3.1 Descripción

Proceso de extracción de plantillas biométricas desde dispositivos ZKTeco y almacenamiento opcional en base de datos como respaldo. Las plantillas permanecen en el dispositivo como fuente primaria.

#### 3.3.2 Secuencia de Operaciones

```
1. INICIO
   └─ Validar: Device existe

2. CONEXIÓN DEVICE
   ├─ Conectar a Device (IP:Puerto)
   └─ Autenticar con password

3. DESCARGA TEMPLATES
   ├─ Obtener: device.get_templates()
   │
   └─ Resultado: List[BiometricTemplate]
      Cada template contiene:
      ├─ uid: INTEGER (device user ID)
      ├─ fid: INTEGER (template index / finger ID)
      ├─ template: BYTES (blob biométrico)
      ├─ valid: INTEGER (0/1 flag)
      └─ size: INTEGER (template size)

4. BÚSQUEDA DE USER
   Para cada template:
       ├─ Buscar: User.objects.filter(device_id=device_id, uid=template.uid).first()
       │
       ├─ Si NO encontrado:
       │  ├─ logger.warning("Template skipped: User not found", 
       │  │                extra={device_id, uid, fid})
       │  ├─ skipped_count++
       │  └─ SKIP template
       │
       └─ Si encontrado:
          └─ Continuar a ingesta

5. DETERMINACIÓN DE TIPO
   Para cada template válido:
       ├─ Si fid < 10: type = 'FINGER'
       ├─ Si fid >= 10: type = 'FACE'
       └─ Else: type = 'UNKNOWN'

6. INGESTA ATÓMICA
   Para cada template con User válido:
       BiometricTemplate.objects.update_or_create(
           user_id=user.id,
           type=type,
           index=template.fid,
           defaults={
               'valid': template.valid,
               'data': str(template.template),
               'version': str(template.size)
           }
       )
       ├─ Si created: saved_count++
       └─ Si updated: updated_count++

7. DESCONEXIÓN
   └─ Cerrar conexión con device

8. REPORTE
   └─ Response: {saved, skipped, errors, message}

9. FIN
```

#### 3.3.3 Reglas de Negocio

- Las plantillas solo se guardan en DB si existe un registro correspondiente en tabla `users`.
- La tabla `users` no se auto-poblará desde templates. Debe pre-existir (via seed o creación manual).
- Las plantillas son metadata; el dispositivo es la fuente primaria.
- El constraint `UNIQUE(user_id, type, index)` controla duplicados.
- Las plantillas inválidas (`valid = 0`) se guardan como metadata pero marcadas como inválidas.

#### 3.3.4 Validaciones

- Device debe existir en tabla `devices`.
- Para cada template, debe existir `User` con matching `device_id` y `uid`.
- Template blob debe ser no nulo.

#### 3.3.5 Manejo de Errores

| Error | Acción | Logging |
|-------|--------|---------|
| Device inalcanzable | STOP, retornar error | ERROR con IP/Port |
| User no encontrado | SKIP template, continuar | WARNING con uid y fid |
| Template corrupto | SKIP template, continuar | ERROR con detalles |
| DB constraint violation | SKIP (duplicado), continuar | DEBUG |

#### 3.3.6 Postcondiciones

- Tabla `biometric_templates` contiene metadata de templates para Users existentes.
- Templates sin User correspondiente están documentados como skipped.
- Dispositivo permanece inalterado.

---

## 4. POLÍTICA DE DUPLICADOS CONFIGURABLE

### 4.1 Definición del Problema

Los dispositivos ZKTeco pueden generar múltiples eventos de asistencia en un corto período de tiempo debido a:

- Lecturas biométricas múltiples (retry automático del dispositivo)
- Usuario marcando dos veces accidentalmente
- Problemas de conectividad que causan buffering y envío duplicado

Los duplicados EXACTOS (mismo device, user_id, timestamp al segundo) son bloqueados automáticamente por el constraint `UNIQUE(device_id, user_id, timestamp)`.

Sin embargo, eventos CUASI-DUPLICADOS (mismo device, user_id, timestamps dentro de N minutos) pueden ser válidos o inválidos dependiendo del contexto del negocio.

### 4.2 Estrategia Implementada

**Principio**: No realizar deduplicación lógica en la capa de ingesta.

**Justificación**:
- La ingesta debe ser cruda y neutral.
- La definición de "duplicado" varía por regla de negocio (N minutos, mismo punch type, etc.).
- La deduplicación es responsabilidad del motor de cálculo, no de la ingesta.

### 4.3 Configuración en UI (Futuro)

Se recomienda implementar configuración por empresa/departamento:

```
Setting: duplicate_tolerance_minutes
Values: 0, 1, 3, 5, 10, 15
Default: 5

Behavior:
- Motor de cálculo ignora eventos dentro de la ventana de tolerancia.
- Ejemplo: Si tolerance = 5, y hay eventos a las 08:00:00 y 08:03:00, 
  solo el primero se usa para check_in.
```

```
Setting: duplicate_detection_scope
Values: same_punch_only, all_events
Default: same_punch_only

Behavior:
- same_punch_only: Solo deduplica si punch type es igual (IN con IN, OUT con OUT)
- all_events: Deduplica cualquier evento dentro de ventana
```

### 4.4 Implementación Recomendada (Motor, no Ingesta)

```python
# En motor de cálculo (core/engines/v2.py):

def filter_duplicate_events(logs, tolerance_minutes=5, scope='same_punch_only'):
    """
    Filtra eventos cuasi-duplicados según política configurada.
    
    Args:
        logs: QuerySet de AttendanceLog ordenado por timestamp
        tolerance_minutes: Ventana de tolerancia en minutos
        scope: 'same_punch_only' o 'all_events'
    
    Returns:
        List de logs deduplicados
    """
    if tolerance_minutes == 0:
        return list(logs)
    
    filtered = []
    last_event = None
    
    for log in logs:
        if last_event is None:
            filtered.append(log)
            last_event = log
            continue
        
        time_diff = (log.timestamp - last_event.timestamp).total_seconds() / 60
        
        if time_diff > tolerance_minutes:
            filtered.append(log)
            last_event = log
        elif scope == 'all_events':
            # Skip: dentro de ventana
            continue
        elif scope == 'same_punch_only' and log.punch == last_event.punch:
            # Skip: dentro de ventana Y mismo punch type
            continue
        else:
            # Diferente punch type, agregar
            filtered.append(log)
            last_event = log
    
    return filtered
```

### 4.5 Tabla de Configuración

```sql
-- Agregar a tabla settings (ya existe):
INSERT INTO settings (key, value, description) VALUES 
('duplicate_tolerance_minutes', '5', 'Ventana de tolerancia para eventos cuasi-duplicados (minutos)'),
('duplicate_detection_scope', 'same_punch_only', 'Scope de deduplicación: same_punch_only | all_events');
```

### 4.6 Responsabilidades

| Componente | Responsabilidad | Justificación |
|------------|-----------------|---------------|
| Ingesta (`run_import_attendance_job`) | NO deduplica eventos lógicamente | Debe ser neutral y cruda |
| DB Constraint `UNIQUE(...)` | Previene duplicados EXACTOS | Garantía de integridad |
| Motor (`resolve_schedule_unified`) | Deduplica según política | Lógica de negocio |
| UI Configuración | Permite ajuste de tolerancia | Flexibilidad por empresa |

---

## 5. AISLAMIENTO DE DOMINIOS

### 5.1 Matriz de Responsabilidades

| Dominio | Responsables | Lectura | Escritura | Prohibiciones |
|---------|--------------|---------|-----------|---------------|
| **HR** | Módulo RRHH, Admin | employees, departments, positions, companies | employees, departments, positions, companies | NO leer desde device, NO escribir desde ingesta |
| **Device** | Módulo Devices, Admin | devices, users (espejo), biometric_templates | devices | NO escribir employees, NO escribir attendance_logs |
| **Ingesta** | `run_import_attendance_job`, Adapters | devices, employees (validación) | attendance_logs, import_batches | NO escribir employees, NO escribir users, NO modificar timestamps |
| **Motor** | `resolve_schedule_unified`, Engines | attendance_logs, employees, att_timetables, att_shifts, att_leaves, att_holidays | att_daily_attendance | NO escribir attendance_logs, NO escribir employees |
| **Horarios** | Módulo Timetables, Admin | att_*, employees | att_timetables, att_shifts, att_employee_shifts, att_schedule_overrides, att_leaves, att_holidays | NO escribir attendance_logs, NO escribir employees directamente |
| **Sistema** | Background Workers, Scheduler | jobs, settings | jobs, job_logs | Acceso transversal para logging |

### 5.2 Fronteras de Dominio

```
┌─────────────────────────────────────────────────────────────────┐
│                         DOMINIO HR                              │
│  Responsabilidad: Master data de empleados                      │
│  Tablas: employees, departments, positions, companies           │
│  Operaciones: CRUD de empleados, organizaciones                 │
│  Input: UI Admin, importación CSV/Excel, APIs externas          │
│  Output: Lista de empleados activos para sincronización         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    [Sincronización HR → Device]
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       DOMINIO DEVICE                            │
│  Responsabilidad: Configuración de terminales                   │
│  Tablas: devices, users (espejo), biometric_templates           │
│  Operaciones: Configurar devices, enrollments biométricos       │
│  Input: Sincronización desde HR, enrollment manual en terminal  │
│  Output: Eventos de asistencia, templates biométricos           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    [Descarga Device → DB]
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       DOMINIO INGESTA                           │
│  Responsabilidad: Importación cruda de eventos                  │
│  Tablas: attendance_logs, import_batches                        │
│  Operaciones: Validar employee, ingresar eventos sin procesar   │
│  Input: Eventos desde dispositivos ZKTeco                       │
│  Output: Tabla attendance_logs poblada                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    [Cálculo Motor]
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        DOMINIO MOTOR                            │
│  Responsabilidad: Cálculo de asistencia diaria                  │
│  Tablas: att_daily_attendance (escritura)                       │
│  Operaciones: Aplicar reglas, calcular métricas, determinar     │
│               estados (Late, Absent, Normal, etc.)              │
│  Input: attendance_logs, employees, horarios, licencias         │
│  Output: Tabla att_daily_attendance con resultados calculados   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    [Consulta para Reportes]
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      DOMINIO REPORTES                           │
│  Responsabilidad: Visualización y exportación                   │
│  Tablas: att_daily_attendance (lectura)                         │
│  Operaciones: Generar reportes, exportar Excel/PDF, dashboards  │
│  Input: Filtros de usuario (fecha, empleado, departamento)      │
│  Output: Archivos de reporte, gráficos, datasets para nómina   │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 Flujos Prohibidos

Los siguientes flujos están arquitectónicamente prohibidos:

1. **Device → HR (Employee)**
   ```
   ❌ Dispositivo crea o modifica Employee
   Razón: Device no es fuente de verdad de identidad
   ```

2. **Ingesta → HR (Employee)**
   ```
   ❌ run_import_attendance_job() crea Employee
   Razón: Ingesta es neutral, no crea master data
   ```

3. **Motor → HR (Employee)**
   ```
   ❌ resolve_schedule_unified() modifica Employee
   Razón: Motor calcula, no gestiona identidad
   ```

4. **Motor → Ingesta (AttendanceLog)**
   ```
   ❌ Motor modifica attendance_logs
   Razón: Eventos son inmutables (solo vía edición manual con auditoría)
   ```

5. **Device → Ingesta (directo a DB)**
   ```
   ❌ Device escribe directamente en DB
   Razón: Device solo produce eventos; ingesta valida y persiste
   ```

### 5.4 Dependencias Permitidas

| Dominio Origen | Dominio Destino | Tipo | Justificación |
|----------------|-----------------|------|---------------|
| HR | Device | WRITE (sync) | Replicar empleados para enrollment |
| Device | Ingesta | READ (eventos) | Importar eventos de asistencia |
| Device | Ingesta | READ (templates) | Importar templates biométricos |
| HR | Motor | READ (empleados) | Identificar empleados en cálculo |
| Ingesta | Motor | READ (logs) | Datos crudos para procesamiento |
| Horarios | Motor | READ (config) | Reglas para cálculo |
| Motor | Reportes | READ (resultados) | Datos procesados para visualización |
| Cualquiera | Sistema | WRITE (logs) | Auditoría transversal |

---

## 6. MATRIZ DE RIESGOS Y MITIGACIONES

### 6.1 Riesgos Identificados

| ID | Riesgo | Severidad | Probabilidad | Impacto | Estado |
|----|--------|-----------|--------------|---------|--------|
| R01 | Employee no existe al ingresar attendance | ALTA | MEDIA | Datos huérfanos, cálculo imposible | MITIGADO |
| R02 | User no existe al descargar templates | MEDIA | MEDIA | Templates no guardados en DB | MITIGADO |
| R03 | Duplicados cuasi-exactos (dentro de N minutos) | MEDIA | ALTA | Eventos múltiples, cálculo incorrecto | CONFIGURADO |
| R04 | Device inalcanzable durante sync/import | MEDIA | MEDIA | Operación fallida, datos desactualizados | MANEJADO |
| R05 | Sincronización parcial (conexión cae mid-sync) | MEDIA | BAJA | Device con datos parciales | DETECTADO |
| R06 | Timezone inconsistente entre device y DB | ALTA | BAJA | Cálculos incorrectos de horario | DOCUMENTADO |
| R07 | Edición manual de attendance sin auditoría | ALTA | BAJA | Pérdida de trazabilidad | PREVENIDO |
| R08 | Schema change rompe integración | CRÍTICA | BAJA | Sistema inoperante | CONGELADO |

### 6.2 Detalle de Mitigaciones

#### R01: Employee no existe al ingresar attendance

**Descripción**: Un evento de asistencia llega desde el dispositivo con `user_id = "EMP999"` pero no existe ningún empleado con ese `user_id` en la tabla `employees`.

**Impacto**: 
- El evento no puede asociarse a ningún empleado.
- El motor de cálculo no puede procesar el evento.
- Datos huérfanos en `attendance_logs` sin utilidad.

**Mitigación Implementada**:
```python
# En run_import_attendance_job():
try:
    employee = Employee.objects.get(user_id=log.user_id)
except Employee.DoesNotExist:
    logger.warning(
        f"Attendance skipped: Employee not found",
        extra={'device_id': device_id, 'user_id': log.user_id, 'timestamp': log.timestamp}
    )
    skipped_count += 1
    continue  # NO insertar en attendance_logs
```

**Status**: MITIGADO - Validación obligatoria en ingesta.

---

#### R02: User no existe al descargar templates

**Descripción**: Un template biométrico es descargado desde el dispositivo con `uid = 99` pero no existe ningún registro en la tabla `users` con ese `uid` para ese `device_id`.

**Impacto**:
- El template no puede guardarse en base de datos (falta FK a User).
- Metadata de enrollment se pierde.
- No afecta funcionamiento del dispositivo (template permanece allí).

**Mitigación Implementada**:
```python
# En get_device_templates():
user = User.objects.filter(device_id=device_id, uid=template.uid).first()
if not user:
    logger.warning(
        f"Template skipped: User not found",
        extra={'device_id': device_id, 'uid': template.uid, 'fid': template.fid}
    )
    skipped_count += 1
    continue  # NO insertar template
```

**Mejora Propuesta**: Opcionalmente, ofrecer UI para auto-crear User desde template descargado (requiere confirmación del administrador).

**Status**: MITIGADO - Logging explícito y skip controlado.

---

#### R03: Duplicados cuasi-exactos

**Descripción**: Dos eventos de asistencia con timestamps 08:00:00 y 08:02:30 (mismo user, device, punch type) son ingresados en `attendance_logs`. Ambos son válidos según constraint, pero pueden representar el mismo evento lógico.

**Impacto**:
- Motor puede interpretar 08:00:00 como check-in y 08:02:30 como check-out (incorrecto).
- Cálculo de horas trabajadas incorrectas.
- Reportes de asistencia inconsistentes.

**Mitigación Configurada**:
- Ingesta: NO deduplica (mantiene eventos crudos).
- Motor: Aplica política de deduplicación según configuración.
- Setting `duplicate_tolerance_minutes` (default: 5 minutos).
- Setting `duplicate_detection_scope` (default: `same_punch_only`).

**Responsable**: Motor de cálculo (`resolve_schedule_unified`).

**Status**: CONFIGURADO - Política definida y configurable.

---

#### R04: Device inalcanzable

**Descripción**: Durante operación de sync o import, el dispositivo no responde (red caída, dispositivo apagado, IP incorrecta).

**Impacto**:
- Operación no completa.
- Datos no actualizados (sync) o no importados (import).

**Mitigación Implementada**:
```python
# En todos los workers:
try:
    zk_service.connect()
except Exception as e:
    JobManager.finish_job(job_id, status="failed", error=str(e))
    logger.error(f"Device unreachable", extra={'device_id': device_id, 'error': str(e)})
    return  # STOP job
```

**Política de Retry**:
- Retry automático: 3 intentos con backoff exponencial (1s, 2s, 4s).
- Si todos fallan: Job marcado como FAILED.
- Usuario notificado vía UI (Job status).

**Status**: MANEJADO - Error handling robusto con logging y retry.

---

#### R05: Sincronización parcial

**Descripción**: Durante `run_sync_users_job()`, se envían 50 de 100 empleados al dispositivo, luego la conexión se pierde. El dispositivo queda con datos parciales.

**Impacto**:
- Device no tiene lista completa de empleados.
- Algunos empleados no pueden marcar asistencia.
- Inconsistencia entre HR y dispositivo.

**Mitigación Propuesta**:
```python
# Agregar post-sync validation:
device_users = zk_service.get_users()
device_user_ids = {u.user_id for u in device_users}

for emp in synced_employees:
    if emp.user_id not in device_user_ids:
        logger.warning(f"Sync verification failed: {emp.user_id}")
```

**Requisito**: Implementar validación post-sync (ver PROPUESTAS_CAMBIOS_CODIGO.md).

**Status**: DETECTADO - Mitigación propuesta pendiente de implementación.

---

#### R06: Timezone inconsistente

**Descripción**: Dispositivo opera en timezone A (ej: UTC-3), base de datos en timezone B (ej: UTC-5), servidor en timezone C (ej: UTC). Los timestamps de eventos pueden interpretarse incorrectamente.

**Impacto**:
- Empleado marca a las 08:00 (hora local), pero se registra como 11:00 (UTC).
- Cálculo de late/early incorrecto.
- Reportes muestran horarios equivocados.

**Mitigación Documentada**:
```python
# Configuración Django (settings.py):
TIME_ZONE = 'America/Argentina/Buenos_Aires'  # Zona del negocio
USE_TZ = True  # Siempre usar timezone-aware datetimes

# En ingesta:
# Los timestamps desde pyzk library ya vienen como naive datetime (hora local del device).
# Se debe convertir explícitamente a timezone-aware:
from django.utils import timezone
from datetime import datetime
import pytz

device_tz = pytz.timezone('America/Argentina/Buenos_Aires')
timestamp_aware = device_tz.localize(timestamp_naive)
timestamp_utc = timestamp_aware.astimezone(pytz.UTC)
```

**Recomendación**: Validar durante setup que dispositivo y servidor estén en mismo timezone, o documentar conversión explícita.

**Status**: DOCUMENTADO - Configuración existente correcta, requiere validación en deployment.

---

#### R07: Edición manual sin auditoría

**Descripción**: Un administrador modifica un registro de `attendance_logs` directamente en base de datos (SQL) sin registrar quién, cuándo y por qué.

**Impacto**:
- Pérdida de trazabilidad.
- Imposibilidad de auditar cambios.
- Riesgo de fraude o error no detectable.

**Mitigación Implementada**:
```python
# Tabla attendance_logs incluye:
- edited_by: CharField(100) - Usuario que editó
- edited_at: DateTimeField - Timestamp de edición
- edited_reason: CharField(255) - Justificación
- is_manual: BooleanField - Flag de edición manual

# UI debe obligar formulario de edición:
if editing_attendance_log:
    require(edited_by, edited_reason)
    set(edited_at = now(), is_manual = True)
```

**Política**: Edición manual SOLO via UI con autenticación. Acceso directo a DB prohibido excepto DBA con aprobación.

**Status**: PREVENIDO - Schema soporta auditoría completa.

---

#### R08: Schema change rompe integración

**Descripción**: Un desarrollador modifica tabla `employees` agregando FK o constraint que rompe flujo de sincronización o ingesta.

**Impacto**:
- Sistema inoperante.
- Workflows críticos fallan.
- Requiere rollback urgente.

**Mitigación Establecida**:
- Congelar schema en versión Beta Ready (este documento).
- Cambios futuros requieren:
  - Revisión de arquitectura.
  - Actualización de este contrato.
  - Testing exhaustivo en staging.
  - Aprobación de comité técnico.

**Política de Cambios**:
```
PROHIBIDO (sin aprobación formal):
- Agregar FK entre attendance_logs.user_id y employees.user_id
- Modificar constraint UNIQUE de attendance_logs
- Cambiar tipo de datos de user_id
- Eliminar columnas existentes
- Renombrar tablas

PERMITIDO (con testing):
- Agregar columnas nullable
- Agregar índices
- Modificar defaults
```

**Status**: CONGELADO - Schema protegido por contrato arquitectónico.

---

### 6.3 Matriz de Contingencia

| Escenario | Acción Inmediata | Tiempo de Respuesta | Responsable |
|-----------|------------------|---------------------|-------------|
| Device offline durante sync | Marcar job como FAILED, alertar admin vía UI | Inmediato (automático) | Sistema |
| Employee eliminado pero tiene attendance_logs | Mantener logs (no cascade delete), marcar employee como inactive | 24 horas | Admin HR |
| Duplicados excesivos (>10% de eventos) | Ajustar `duplicate_tolerance_minutes` vía UI Settings | 1 hora | Admin Sistema |
| Timezone mismatch detectado | Documentar conversión explícita en código, validar config | 4 horas | DevOps + Backend |
| Schema change propuesto | Convocar comité técnico, evaluar impacto, actualizar contrato | 1 semana | Arquitecto |

---

## 7. PREPARACIÓN FUTURA PARA MULTI-MARCA

### 7.1 Objetivo Estratégico

Diseñar la arquitectura actual de forma que permita futuras integraciones con otros fabricantes de dispositivos biométricos (ZKFace, Suprema, Anviz, Hikvision, etc.) sin alterar la lógica de negocio ni el modelo de datos.

### 7.2 Principio de Abstracción

Todos los dispositivos biométricos, independientemente del fabricante, deben exponerse al sistema SRTimeWeb mediante una interfaz unificada (DeviceAdapter) que normaliza:

- Enrollments de usuarios
- Eventos de asistencia
- Templates biométricos
- Metadata de dispositivos

### 7.3 Diseño de DeviceAdapter

#### 7.3.1 Interfaz Base

```python
# core/adapters/base.py

from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class NormalizedDeviceUser:
    """Usuario normalizado independiente de fabricante."""
    uid: int  # ID interno del dispositivo
    name: str  # Nombre completo
    privilege: int  # Nivel de privilegio
    user_id: str  # ID del empleado (mapea a Employee.user_id)
    card: str  # Número de tarjeta (opcional)
    face_count: int = 0
    finger_count: int = 0


@dataclass
class NormalizedAttendanceRecord:
    """Evento de asistencia normalizado."""
    user_id: str  # ID del empleado
    timestamp: datetime  # Momento exacto del evento (timezone-aware)
    status: int  # Estado (0=check-in, 1=check-out, etc.)
    punch: int  # Tipo de marcación
    verify_mode: Optional[int] = None  # Modo de verificación (finger, face, password, card)
    workstate: Optional[int] = None
    workcode: Optional[int] = None


@dataclass
class NormalizedBiometricTemplate:
    """Template biométrico normalizado."""
    uid: int  # ID de usuario en dispositivo
    type: str  # FINGER, FACE, PALM
    index: int  # Índice del template (0-9 fingers, 10+ faces)
    data: bytes  # Blob del template
    valid: bool  # Validez del template
    version: Optional[str] = None


@dataclass
class NormalizedDeviceInfo:
    """Información del dispositivo normalizada."""
    serialnumber: str
    platform: str  # ZKTeco, ZKFace, Suprema, etc.
    firmware_version: str
    mac: str
    user_count: int
    face_count: int
    fp_count: int
    transaction_count: int


class DeviceAdapter(ABC):
    """
    Interfaz abstracta para adaptadores de dispositivos biométricos.
    
    Todos los fabricantes deben implementar esta interfaz para integrarse
    con SRTimeWeb.
    """
    
    def __init__(self, ip: str, port: int, password: str = '', timeout: int = 10):
        self.ip = ip
        self.port = port
        self.password = password
        self.timeout = timeout
        self.conn = None
    
    @abstractmethod
    def connect(self) -> bool:
        """Conectar al dispositivo."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Desconectar del dispositivo."""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Probar conectividad sin establecer sesión persistente."""
        pass
    
    @abstractmethod
    def get_users(self) -> List[NormalizedDeviceUser]:
        """Obtener lista de usuarios enrollados."""
        pass
    
    @abstractmethod
    def set_user(self, user: NormalizedDeviceUser) -> bool:
        """Enrollar o actualizar usuario en dispositivo."""
        pass
    
    @abstractmethod
    def delete_user(self, uid: int) -> bool:
        """Eliminar usuario del dispositivo."""
        pass
    
    @abstractmethod
    def get_attendance(self, start_date: Optional[datetime] = None) -> List[NormalizedAttendanceRecord]:
        """Obtener eventos de asistencia desde dispositivo."""
        pass
    
    @abstractmethod
    def get_templates(self) -> List[NormalizedBiometricTemplate]:
        """Obtener templates biométricos desde dispositivo."""
        pass
    
    @abstractmethod
    def clear_attendance(self) -> bool:
        """Limpiar logs de asistencia del dispositivo."""
        pass
    
    @abstractmethod
    def enable_device(self) -> bool:
        """Habilitar dispositivo (modo operativo)."""
        pass
    
    @abstractmethod
    def disable_device(self) -> bool:
        """Deshabilitar dispositivo (modo mantenimiento)."""
        pass
    
    @abstractmethod
    def get_device_info(self) -> NormalizedDeviceInfo:
        """Obtener información del dispositivo."""
        pass
```

#### 7.3.2 Implementación ZKTeco

```python
# core/adapters/zkteco.py

from zk import ZK
from core.adapters.base import (
    DeviceAdapter, 
    NormalizedDeviceUser, 
    NormalizedAttendanceRecord,
    NormalizedBiometricTemplate,
    NormalizedDeviceInfo
)


class ZKTecoAdapter(DeviceAdapter):
    """Adaptador para dispositivos ZKTeco usando biblioteca pyzk."""
    
    def connect(self) -> bool:
        zk = ZK(self.ip, port=self.port, timeout=self.timeout, password=self.password)
        self.conn = zk.connect()
        return self.conn is not None
    
    def disconnect(self) -> None:
        if self.conn:
            self.conn.disconnect()
            self.conn = None
    
    def get_users(self) -> List[NormalizedDeviceUser]:
        if not self.conn:
            self.connect()
        
        try:
            users = self.conn.get_users()
            return [
                NormalizedDeviceUser(
                    uid=u.uid,
                    name=u.name,
                    privilege=u.privilege,
                    user_id=u.user_id,
                    card=str(u.card) if u.card else '',
                    face_count=0,  # pyzk no expone este campo directamente
                    finger_count=0
                )
                for u in users
            ]
        finally:
            if self.conn:
                self.disconnect()
    
    def set_user(self, user: NormalizedDeviceUser) -> bool:
        if not self.conn:
            self.connect()
        
        try:
            self.conn.set_user(
                uid=user.uid,
                name=user.name,
                privilege=user.privilege,
                password='',
                group_id='0',
                user_id=user.user_id,
                card=int(user.card) if user.card else 0
            )
            return True
        except Exception:
            return False
        finally:
            if self.conn:
                self.disconnect()
    
    def get_attendance(self, start_date=None) -> List[NormalizedAttendanceRecord]:
        if not self.conn:
            self.connect()
        
        try:
            attendances = self.conn.get_attendance()
            return [
                NormalizedAttendanceRecord(
                    user_id=a.user_id,
                    timestamp=a.timestamp,
                    status=a.status,
                    punch=a.punch,
                    verify_mode=getattr(a, 'verify_mode', None),
                    workstate=getattr(a, 'workstate', None),
                    workcode=getattr(a, 'workcode', None)
                )
                for a in attendances
            ]
        finally:
            if self.conn:
                self.disconnect()
    
    def get_templates(self) -> List[NormalizedBiometricTemplate]:
        if not self.conn:
            self.connect()
        
        try:
            templates = self.conn.get_templates()
            return [
                NormalizedBiometricTemplate(
                    uid=t.uid,
                    type='FINGER' if t.fid < 10 else 'FACE',
                    index=t.fid,
                    data=t.template,
                    valid=bool(t.valid),
                    version=str(t.size) if hasattr(t, 'size') else None
                )
                for t in templates
            ]
        finally:
            if self.conn:
                self.disconnect()
    
    def get_device_info(self) -> NormalizedDeviceInfo:
        if not self.conn:
            self.connect()
        
        try:
            return NormalizedDeviceInfo(
                serialnumber=self.conn.get_serialnumber() or '',
                platform='ZKTeco',
                firmware_version=self.conn.get_firmware_version() or '',
                mac=self.conn.get_mac() or '',
                user_count=len(self.conn.get_users()),
                face_count=self.conn.get_face_count() or 0,
                fp_count=self.conn.get_fp_count() or 0,
                transaction_count=len(self.conn.get_attendance())
            )
        finally:
            if self.conn:
                self.disconnect()
    
    # Implementar métodos restantes: delete_user, clear_attendance, enable_device, disable_device
```

#### 7.3.3 Factory Pattern

```python
# core/adapters/factory.py

from core.adapters.base import DeviceAdapter
from core.adapters.zkteco import ZKTecoAdapter
# Futuras importaciones:
# from core.adapters.zkface import ZKFaceAdapter
# from core.adapters.suprema import SupremaAdapter


def get_device_adapter(device_type: str, ip: str, port: int, password: str = '') -> DeviceAdapter:
    """
    Factory para crear instancia de DeviceAdapter según tipo de dispositivo.
    
    Args:
        device_type: Tipo de dispositivo ('ZKTECO', 'ZKFACE', 'SUPREMA', etc.)
        ip: Dirección IP del dispositivo
        port: Puerto del dispositivo
        password: Contraseña del dispositivo
    
    Returns:
        Instancia de DeviceAdapter correspondiente
    
    Raises:
        ValueError: Si device_type no es soportado
    """
    adapters = {
        'ZKTECO': ZKTecoAdapter,
        # 'ZKFACE': ZKFaceAdapter,  # Futuro
        # 'SUPREMA': SupremaAdapter,  # Futuro
    }
    
    adapter_class = adapters.get(device_type.upper())
    if not adapter_class:
        raise ValueError(f"Unsupported device type: {device_type}")
    
    return adapter_class(ip, port, password)
```

### 7.4 Modificación de Modelo Device

Para soportar multi-marca, agregar campo `device_type` a tabla `devices`:

```python
# core/models.py (futuro, NO implementar ahora)

class Device(models.Model):
    DEVICE_TYPE_CHOICES = [
        ('ZKTECO', 'ZKTeco'),
        ('ZKFACE', 'ZKFace'),
        ('SUPREMA', 'Suprema BioStar'),
        ('ANVIZ', 'Anviz'),
        ('HIKVISION', 'Hikvision'),
    ]
    
    # Campos existentes...
    device_type = models.CharField(
        max_length=20, 
        choices=DEVICE_TYPE_CHOICES, 
        default='ZKTECO',
        verbose_name='Tipo de Dispositivo'
    )
```

**NOTA**: Esta modificación NO se implementa en versión actual (Beta Ready). Es preparación arquitectónica para futuro (v1.1+).

### 7.5 Uso en Workers

```python
# core/services/zk_workers.py (futuro)

from core.adapters.factory import get_device_adapter

def run_import_attendance_job(job_id: str, device_id: int, ...):
    device = models.Device.objects.get(id=device_id)
    
    # En lugar de:
    # zk_service = get_zk_service(device.ip, device.port)
    
    # Usar factory:
    device_adapter = get_device_adapter(
        device_type=device.device_type,  # 'ZKTECO', 'ZKFACE', etc.
        ip=device.ip,
        port=device.port,
        password=str(device.password)
    )
    
    device_adapter.connect()
    attendance_records = device_adapter.get_attendance()
    
    # El resto del código NO cambia - ya trabaja con datos normalizados
    for record in attendance_records:
        # record es NormalizedAttendanceRecord, independiente de marca
        AttendanceLog.objects.update_or_create(...)
```

### 7.6 Ventajas de la Abstracción

1. **Extensibilidad**: Agregar nueva marca = crear nuevo adapter, no modificar lógica de negocio.
2. **Testabilidad**: Mock de DeviceAdapter facilita testing sin hardware.
3. **Consistencia**: Todos los dispositivos exponen misma interfaz.
4. **Migración gradual**: Refactoring puede hacerse por fases sin romper sistema actual.
5. **Documentación**: Contrato claro de qué debe implementar cada adapter.

### 7.7 Plan de Implementación (Futuro)

**Fase 1 (v1.1)**: Crear abstracciones sin modificar código actual
- Implementar DeviceAdapter base
- Implementar ZKTecoAdapter como wrapper de código actual
- Validar que ZKTecoAdapter funciona idénticamente

**Fase 2 (v1.2)**: Refactorizar workers para usar adapters
- Modificar zk_workers.py para usar factory
- Migrar gradualmente de get_zk_service a get_device_adapter
- Mantener compatibilidad con código legacy

**Fase 3 (v1.3)**: Agregar segunda marca (ej: ZKFace)
- Implementar ZKFaceAdapter
- Agregar campo device_type a Device model (migración)
- Testing end-to-end con ambas marcas

**Fase 4 (v2.0)**: Eliminar código legacy
- Deprecar get_zk_service
- Unificar completamente en adapters

---

## 8. CONCLUSIÓN FORMAL

### 8.1 Declaración de Estado

Este documento constituye el **CONTRATO OPERATIVO DE INTEGRACIÓN** entre dispositivos biométricos ZKTeco y el sistema SRTimeWeb, versión 1.0.0, vigente a partir del 2026-02-12.

### 8.2 Ámbito de Vigencia

Este contrato define de forma vinculante:

1. **Principios arquitectónicos** que rigen la integración.
2. **Modelo de datos** y relaciones entre tablas.
3. **Flujos operativos** oficiales para sincronización y ingesta.
4. **Políticas de validación** y manejo de duplicados.
5. **Aislamiento de dominios** y responsabilidades.
6. **Matriz de riesgos** y mitigaciones implementadas.
7. **Preparación futura** para extensibilidad multi-marca.

### 8.3 Cumplimiento Obligatorio

Todos los desarrollos, modificaciones o extensiones del sistema SRTimeWeb que involucren interacción con dispositivos biométricos deben cumplir estrictamente con los principios y flujos establecidos en este contrato.

**Queda expresamente prohibido**:

- Crear flujos bidireccionales HR ↔ Device para datos de identidad.
- Modificar el schema de base de datos sin actualizar este contrato.
- Implementar lógica de negocio en la capa de ingesta.
- Preprocesar eventos de asistencia antes de persistencia.
- Agregar ForeignKey entre `attendance_logs.user_id` y `employees.user_id`.
- Modificar el comportamiento del motor de cálculo sin documentar.

### 8.4 Proceso de Modificación

Cualquier propuesta de modificación a este contrato debe seguir el proceso:

1. **Solicitud formal** con justificación técnica y de negocio.
2. **Revisión de arquitectura** por comité técnico.
3. **Evaluación de impacto** en sistema, datos y usuarios.
4. **Aprobación por mayoría** de firmantes originales.
5. **Actualización del contrato** con nueva versión y changelog.
6. **Testing exhaustivo** en staging antes de producción.
7. **Deployment coordinado** con rollback plan.

### 8.5 Garantías del Sistema

Con la implementación de este contrato, el sistema SRTimeWeb garantiza:

1. **Integridad de identidad**: Única fuente de verdad en tabla `employees`.
2. **Inmutabilidad de eventos**: `attendance_logs` preserva eventos crudos.
3. **Idempotencia**: Operaciones repetidas no causan duplicados ni inconsistencias.
4. **Trazabilidad completa**: Auditoría de ediciones manuales.
5. **Separación de concerns**: Dominios independientes sin acoplamiento.
6. **Extensibilidad futura**: Arquitectura preparada para multi-marca.

### 8.6 Declaración Beta Ready

Se declara que el sistema SRTimeWeb, en su versión actual, cumple con todos los requisitos arquitectónicos documentados en este contrato y se encuentra en estado **Beta Ready** para:

- Deployment en entornos productivos controlados.
- Evaluación por early adopters.
- Testing de stress y carga.
- Auditoría de cumplimiento normativo.

El sistema NO requiere modificaciones de schema ni de arquitectura para entrar en fase Beta.

### 8.7 Responsabilidades Post-Contractuales

Una vez firmado este contrato:

- **Arquitecto de Sistemas**: Custodio del contrato, revisor de cambios propuestos.
- **Equipo Backend**: Implementación fiel de flujos y validaciones.
- **Equipo Base de Datos**: Protección del schema contra cambios no autorizados.
- **Líder de Proyecto**: Comunicación de contrato a stakeholders, priorización de compliance.

### 8.8 Vigencia y Revisión

Este contrato tiene vigencia indefinida hasta que sea formalmente reemplazado por una versión posterior.

**Revisión obligatoria** en los siguientes casos:

- Cambio de fabricante de dispositivos biométricos.
- Agregación de nueva marca de dispositivos.
- Modificación de normativa laboral que impacte cálculo de asistencia.
- Detección de riesgo no contemplado en matriz de riesgos.
- Cambio de versión mayor del sistema (v2.0+).

**Revisión recomendada** cada 6 meses para:

- Evaluar cumplimiento efectivo.
- Identificar gaps o mejoras.
- Actualizar estrategia de mitigación de riesgos.

---

## ANEXOS

### Anexo A: Referencias Técnicas

- Tabla de 21 tablas de base de datos (ver ESPECIFICACION_FORMAL_SRTIMEWEB_ZKTECO.md).
- Diagrama de flujos detallado (ver ESPECIFICACION_FORMAL_SRTIMEWEB_ZKTECO.md sección 3).
- Checklist de validación (ver CHECKLIST_VALIDACION_SRTIMEWEB.md).
- Propuestas de mejora (ver PROPUESTAS_CAMBIOS_CODIGO.md).

### Anexo B: Glosario Extendido

- **pyzk**: Biblioteca Python para comunicación con dispositivos ZKTeco.
- **Punch**: Evento de marcación (IN, OUT, break, etc.).
- **Verify Mode**: Método de verificación (fingerprint, face, password, card).
- **Work State**: Estado laboral en momento de marcación.
- **Work Code**: Código de actividad laboral.
- **Constraint**: Restricción de integridad en base de datos.
- **Idempotencia**: Propiedad de operación que produce mismo resultado al ejecutarse múltiples veces.

### Anexo C: Contactos Clave

| Rol | Responsabilidad | Contacto |
|-----|-----------------|----------|
| Arquitecto Senior | Diseño y validación | [EMAIL] |
| Líder Backend | Implementación workflows | [EMAIL] |
| DBA | Protección schema | [EMAIL] |
| DevOps | Deployment y monitoreo | [EMAIL] |
| QA Lead | Testing y validación | [EMAIL] |

---

**FIN DEL CONTRATO OPERATIVO DE INTEGRACIÓN**

**Documento Técnico Interno - SRTimeWeb v1.0 Beta Ready**  
**Fecha de Emisión**: 2026-02-12  
**Próxima Revisión**: 2026-08-12  
**Estado**: VIGENTE - Awaiting Signatures  

---

**REGISTRO DE VERSIONES**

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0.0 | 2026-02-12 | Arquitecto Senior Backend | Emisión inicial - Beta Ready |
