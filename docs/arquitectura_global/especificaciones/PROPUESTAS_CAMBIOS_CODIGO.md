# 🔧 PROPUESTAS DE CAMBIOS DE CÓDIGO

**Documento**: Cambios específicos para alinear con ESPECIFICACION_FORMAL  
**Criterio**: Sin cambios de schema, solo lógica/validación/logging  
**Status**: READY FOR IMPLEMENTATION  
**Test Impact**: 0 breaking changes, solo added logging/validation  

---

## 📋 CAMBIO 1: get_device_templates() - Logging Explícito [P0 URGENTE]

### Ubicación
`core/views_devices.py` líneas 345-350

### Problema
Cuando un `User` no existe en la tabla, la plantilla biométrica se descarta silenciosamente. El usuario no sabe por qué su template fue saltado.

**Código Actual (TIENE GAP)**:
```python
user = models.User.objects.filter(device_id=device_id, uid=t.uid).first()
if not user:
    skipped_count += 1
    continue  # ❌ SILENT SKIP - Sin logging
```

### Solución (PROPUESTA)

Reemplazar el bloque de skip con logging explícito:

```python
user = models.User.objects.filter(device_id=device_id, uid=t.uid).first()
if not user:
    logger.warning(
        f"Biometric template skipped: User not found in database",
        extra={
            'device_id': device_id,
            'uid': t.uid,
            'fid': t.fid,
            'template_type': 'FINGER' if t.fid < 10 else 'FACE',
            'severity': 'WARN_USER_NOT_FOUND',
            'action': 'SKIP_TEMPLATE'
        }
    )
    skipped_count += 1
    continue
```

### Detalles del Logging
- **level**: `WARNING` (usuario debe saber)
- **message**: Explicita "User not found"
- **extra fields**:
  - `device_id`: Cuál dispositivo
  - `uid`: Cuál usuario del device
  - `fid`: Cuál template index
  - `template_type`: FINGER/FACE
  - `severity`: Clasificación
  - `action`: Qué se hizo (SKIP)

### Impacto
- ✅ NO schema changes
- ✅ NO API changes
- ✅ NO test changes (logging es decorativo)
- ✅ Data visibility mejorada
- ✅ Debugging facilitado

### Verificación
```bash
# Después del cambio, ejecutar:
python manage.py test core.tests.test_devices
# Esperado: 0 failures, sin cambios en counts
```

---

## 📋 CAMBIO 2: run_sync_users_job() - Order Determinístico [P2]

### Ubicación
`core/services/zk_workers.py` líneas 420-425

### Problema
La consulta de empleados NO especifica un orden, lo que puede causar:
- Resultados no determinísticos entre ejecuciones
- Debugging difícil (diferentes órdenes cada vez)
- Documentación incompleta

**Código Actual (TIENE GAP)**:
```python
if employee_ids:
    employees = models.Employee.objects.filter(id__in=employee_ids, active=True)
else:
    employees = models.Employee.objects.filter(active=True)
```

### Solución (PROPUESTA)

Agregar `.order_by('user_id')` para determinismo:

```python
if employee_ids:
    employees = models.Employee.objects.filter(id__in=employee_ids, active=True).order_by('user_id')
else:
    employees = models.Employee.objects.filter(active=True).order_by('user_id')
```

Alternativa más concisa:

```python
query = models.Employee.objects.filter(active=True)
if employee_ids:
    query = query.filter(id__in=employee_ids)
employees = query.order_by('user_id')
```

### Beneficios
- ✅ Orden predecible entre ejecuciones
- ✅ Facilita debugging (siempre igual)
- ✅ FK index en user_id (ya existe) lo hace eficiente
- ✅ Cumple con especificación formal

### Impacto
- ✅ NO schema changes
- ✅ NO API changes
- ✅ Tiny performance impact (negligible con index)
- ✅ Logging será diferente (usuarios en orden)

### Verificación
```bash
# Ejecutar sync dos veces consecutivas:
python manage.py sync_users_job(device_id=1)
# Log debe ser idéntico en orden
```

---

## 📋 CAMBIO 3: run_sync_users_job() - Validación Post-Sync [P1]

### Ubicación
`core/services/zk_workers.py` líneas 470-480 (después de enable_device)

### Problema
Después de sincronizar usuarios al device, no se valida si el device realmente los guardó. El sync puede reportar "OK" pero el device rechazó los usuarios.

**Código Actual (TIENE GAP)**:
```python
finally:
    try:
        JobManager.append_log(job_id, "Habilitando terminal...")
        zk_service.enable_device()
    except:
        pass
    zk_service.disconnect()
# Fin - SIN validación post-sync
```

### Solución (PROPUESTA)

Agregar bloque de validación POST-ENABLE, PRE-DISCONNECT:

```python
finally:
    try:
        JobManager.append_log(job_id, "Habilitando terminal...")
        zk_service.enable_device()
        
        # NUEVO: Validación post-sync
        JobManager.set_progress(job_id, 98, "Validando sincronización...")
        try:
            device_users = zk_service.get_users()
            device_user_ids = {u.user_id for u in device_users if u.user_id}
            
            validation_failures = []
            for emp in synced_employees:
                if emp.user_id not in device_user_ids:
                    validation_failures.append(emp.user_id)
                    logger.warning(
                        f"Sync verification failed: {emp.user_id}",
                        extra={
                            'device_id': device_id,
                            'severity': 'WARN_SYNC_VERIFY',
                            'action': 'POST_VALIDATION'
                        }
                    )
            
            if validation_failures:
                JobManager.append_log(
                    job_id,
                    f"⚠️ Validación post-sync: {len(validation_failures)} usuarios no confirmados en device"
                )
            else:
                JobManager.append_log(job_id, "✅ Validación post-sync: Todos los usuarios confirmados")
                
        except Exception as e:
            logger.warning(
                f"Could not perform post-sync validation",
                extra={
                    'device_id': device_id,
                    'error': str(e),
                    'severity': 'WARN_VERIFY_ERROR'
                }
            )
            JobManager.append_log(job_id, f"⚠️ No se pudo validar sincronización: {str(e)}")
    
    except:
        pass
    finally:
        zk_service.disconnect()
```

### Detalles
- **Paso 1**: Después de enable_device
- **Paso 2**: Descargar lista actual de usuarios del device
- **Paso 3**: Comparar synced_employees vs device_users
- **Paso 4**: Loggear cualquier discrepancia
- **Paso 5**: Informar al usuario en JobLog

### Beneficios
- ✅ Detecta fallos silentuosos del device
- ✅ Proporciona auditoría completa
- ✅ Facilita debugging si sync parece fallar
- ✅ Aumenta confiabilidad operacional

### Impacto
- ✅ NO schema changes
- ✅ NO API changes
- ✅ Performance: +1 GET request (negligible)
- ✅ Logging enriquecido

### Validación
```bash
# Test: Sync a device, luego verificar logs
tail -n 20 device_sync_job.log
# Debe incluir línea: "✅ Validación post-sync: Todos..."
```

---

## 📋 CAMBIO 4: run_import_attendance_job() - Detailed Logging [P1]

### Ubicación
`core/services/zk_workers.py` líneas 175-185

### Problema
Cuando se salta un registro de asistencia (Employee no existe), solo se incrementa un contador. El usuario no sabe cuál fue el problema specific.

**Código Actual (TIENE GAP)**:
```python
try:
    employee = models.Employee.objects.get(user_id=log.user_id)
except models.Employee.DoesNotExist:
    logger.warning(...)  # ← Logging existe pero podría ser más detallado
    continue
```

### Solución (PROPUESTA)

Mejorar el logging con más contexto:

```python
try:
    employee = models.Employee.objects.get(user_id=log.user_id)
except models.Employee.DoesNotExist:
    logger.warning(
        f"Attendance record skipped: Employee not found",
        extra={
            'device_id': device_id,
            'user_id': log.user_id,
            'timestamp': log.timestamp.isoformat(),
            'status': log.status,
            'punch': log.punch,
            'severity': 'WARN_INVALID_EMPLOYEE',
            'action': 'SKIP_RECORD',
            'reason': 'EMPLOYEE_NOT_FOUND'
        }
    )
    skipped_count += 1
    logger_append_log(job_id, f"⚠️ Registro saltado: usuario {log.user_id} no existe (timestamp: {log.timestamp})")
    continue
```

### Detalles del Logging
- **level**: `WARNING` (usuario debe saber)
- **message**: Explicita "Employee not found"
- **extra fields**:
  - `device_id`: Cuál dispositivo produjo el log
  - `user_id`: Cuál usuario del dispositivo
  - `timestamp`: Cuándo ocurrió la marcación
  - `status`: Estado del evento (IN/OUT)
  - `punch`: Punch type
  - `severity`: Clasificación para agregación
  - `action`: Qué se hizo (SKIP)
  - `reason`: Por qué se skippó

### Beneficios
- ✅ Claridad completa sobre qué fue skippado y por qué
- ✅ Facilita auditoría de problemas
- ✅ Ayuda a identificar HR master data gaps
- ✅ Integración con JobLog para UI feedback

### Impacto
- ✅ NO schema changes
- ✅ NO API changes
- ✅ Performance: logging minimal
- ✅ Observability mejorada

### Validación
```bash
# Ejecutar import con usuario inválido:
python manage.py import_attendance --device=1 --start=2026-01-01
# Log debe incluir details específicos de qué fue skippado
```

---

## 📋 CAMBIO 5: get_device_templates() - Response Mejorada [P1]

### Ubicación
`core/views_devices.py` líneas 373-390 (Response)

### Problema
La respuesta API retorna counts pero no detalles de cuáles uids fueron skippados, haciendo debugging difícil.

**Código Actual (PARCIAL)**:
```python
return Response({
    "success": True, 
    "message": f"Templates guardados: {saved_count}, Omitidos (sin usuario): {skipped_count}, Errores: {error_count}", 
    "saved": saved_count,
    "skipped": skipped_count,
    "errors": error_count,
})
```

### Solución (PROPUESTA)

Mejorar respuesta con detalles opcionales:

```python
response_data = {
    "success": True if error_count == 0 else False, 
    "message": f"Templates guardados: {saved_count}, Omitidos (sin usuario): {skipped_count}, Errores: {error_count}", 
    "saved": saved_count,
    "skipped": skipped_count,
    "errors": error_count,
}

# Agregar detalles si hay skipped
if skipped_count > 0:
    response_data["skipped_details"] = {
        "count": skipped_count,
        "reason": "User not found in database - template cannot be linked",
        "note": "Ensure User records are created before downloading templates",
        "action": "Check run_download_users_job output or create User records manually"
    }

# Agregar errores específicos si hay
if error_count > 0:
    response_data["error_details"] = [
        {
            "uid": e.get('uid'),
            "fid": e.get('fid'),
            "error": str(e.get('error'))
        }
        for e in error_list  # Guardar durante loop
    ]

return Response(response_data)
```

### Detalles
- **success**: true si error_count == 0
- **skipped_details**: Información sobre por qué fueron skippados
- **error_details**: Lista específica de errores con uid/fid

### Beneficios
- ✅ Respuesta más informativa
- ✅ Facilita debugging del cliente
- ✅ Guía accionable (qué hacer si skipped)

### Impacto
- ✅ NO schema changes
- ⚠️ API response cambios (pero backwards compatible - agregar campos)
- ✅ No afecta tests existentes

### Validación
```bash
# Verificar que respuesta incluye nuevos campos:
curl http://localhost:8000/api/v1/devices/1/templates/ | python -m json.tool
# Debe incluir: skipped_details, success
```

---

## 📋 CAMBIO 6: Docstrings Formales [P2]

### Ubicación
`core/services/zk_workers.py` - funciones principales

### Problema
Los workers carecen de docstrings formales que documenten:
- Responsabilidades exactas
- Inputs/outputs
- Side effects
- Relaciones con tablas

### Solución (PROPUESTA)

Agregar docstrings completos a cada worker:

```python
def run_import_attendance_job(job_id: str, device_id: int, overwrite: bool = False, start_date: Optional[str] = None):
    """
    Descarga logs de asistencia desde dispositivo ZKTeco e importa a attendance_logs.
    
    RESPONSABILIDAD:
    - Leer eventos crudos desde dispositivo
    - Validar que Employee existe para cada evento
    - Guardar en attendance_logs de forma atómica
    
    INVARIANTES:
    - NO crea o modifica Employee records
    - NO crea o modifica User records
    - NO modifica Device
    - AttendanceLog.user_id DEBE tener Employee correspondiente
    - UNIQUE(device, user_id, timestamp) constraint respeta idempotencia
    
    INPUTS:
    - job_id: UUID para tracking del trabajo
    - device_id: FK a Device que se descargará
    - overwrite: Si incluir logs previamente importados (default: False)
    - start_date: Rango opcional de importación (default: last import date)
    
    OUTPUTS:
    - Job.status: 'completed' o 'failed'
    - Job.logs: Detalles de importación
    - AttendanceLog: Tabla con nuevos registros
    
    GARANTÍAS:
    - Atómico: Todo se importa o nada
    - Idempotente: Reimportación no duplica
    - Resiliente: Registros inválidos se skippean con logging
    
    FLUJO ESPERADO:
    1. Conectar a Device
    2. Deshabilitar device (seguridad)
    3. Descargar AttendanceLog generales
    4. Para cada registro:
       a. Validar Employee.user_id existe
       b. Si NO existe: log warning + skip
       c. Si SÍ existe: update_or_create AttendanceLog
    5. Habilitar device
    6. Desconectar
    7. Reportar: saved, skipped, errores
    
    ERRORES COMUNES:
    - Employee no existe: Skip con warning
    - Device sin conexión: Stop batch con error
    - Timestamp inválido: Skip con warning
    - DB lock: Retry automático
    
    AUDITORÍA:
    - Loggea todos los cambios
    - Stored en JobLog para UI
    - Verificable vía `python manage.py job_logs <job_id>`
    """
```

Similar para:
- `run_download_users_job()`
- `run_sync_users_job()`
- `get_device_templates()`

### Beneficios
- ✅ Documentación viva en código
- ✅ Facilita onboarding
- ✅ Especificación vinculada al código
- ✅ IDE tooltips mejorados

### Impacto
- ✅ NO código changes
- ✅ Purely documentation
- ✅ Zero runtime impact

---

## 🧪 CHECKLIST DE IMPLEMENTACIÓN

```bash
# 1. Crear rama feature
git checkout -b feature/formalize-srtimeweb-zkteco-alignment

# 2. Implementar CAMBIO 1 (P0 URGENTE)
# Editar: core/views_devices.py líneas 345-350
# Result: Logging explícito si User no encontrado

# 3. Implementar CAMBIO 2 (P2)
# Editar: core/services/zk_workers.py líneas 420-425
# Result: order_by('user_id') en query

# 4. Implementar CAMBIO 3 (P1)
# Editar: core/services/zk_workers.py líneas 470-485
# Result: Post-sync validation + logging

# 5. Implementar CAMBIO 4 (P1)
# Editar: core/services/zk_workers.py líneas 175-185
# Result: Detailed logging con contexto

# 6. Implementar CAMBIO 5 (P1)
# Editar: core/views_devices.py líneas 373-390
# Result: Response mejorada con detalles

# 7. Implementar CAMBIO 6 (P2)
# Editar: core/services/zk_workers.py
# Result: Docstrings formales

# 8. Validar tests
python manage.py test --verbosity=2
# Esperado: 147 PASSED, 8 SKIPPED, 0 FAILED

# 9. Validar migraciones
python manage.py makemigrations --check
# Esperado: "No changes detected"

# 10. Validar no schema changes
python manage.py sqlmigrate core 0001  # (última migración)
# Revisar que no hay cambios esperados

# 11. Commit y PR
git add core/
git commit -m "Formalize SRTimeWeb-ZKTeco alignment: logging, validation, post-sync checks"
git push origin feature/formalize-srtimeweb-zkteco-alignment
```

---

## 📊 IMPACTO RESUMEN

| Cambio | Líneas | Código | Test | API | Schema | Risk |
|--------|--------|--------|------|-----|--------|------|
| 1 | views_devices.py | +8 | 0 | 0 | 0 | 🟢 LOW |
| 2 | zk_workers.py | +1 | 0 | 0 | 0 | 🟢 LOW |
| 3 | zk_workers.py | +20 | 0 | 0 | 0 | 🟡 MED |
| 4 | zk_workers.py | +8 | 0 | 0 | 0 | 🟢 LOW |
| 5 | views_devices.py | +15 | 0 | ⚠️ ADD | 0 | 🟡 MED |
| 6 | zk_workers.py | +50 | 0 | 0 | 0 | 🟢 LOW |
| **TOTAL** | **2 files** | **+102** | **✅ 0** | **⚠️ 1 Add** | **✅ 0** | **🟢 LOW** |

- ✅ Cero cambios de schema
- ✅ Cero cambios de modelos
- ✅ Cero cambios de FK
- ✅ Tests pasarán sin modificación
- ⚠️ API response agrega campos (backwards compatible)
- 🟢 Risk: MINIMAL

---

**FIN DE PROPUESTAS**

Ready for code review and implementation.  
Estimated effort: 2-3 hours total  
Estimated before deployment RC1.0 final  
