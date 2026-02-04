# Auditoría Frontend ↔ Backend (Versión Alfa)

**Fecha:** 2026-02-04  
**Rol:** Senior Full-Stack Architect (modo auditoría)  
**Objetivo:** Documentar el acoplamiento actual entre frontend React y backend Django para la Versión Alfa, sin cambios de lógica ni de contratos.

---

## 1) Alcance

### Frontend
- Revisión de llamadas a APIs, manejo de respuestas, supuestos sobre datos y lógica en JS.

### Backend
- Revisión de endpoints consumidos por el frontend, payloads reales y consistencia de respuestas.

---

## 2) Mapa de llamadas Frontend → Backend

> **Nota:** Los endpoints listados provienen de [frontend/src/api.ts](../frontend/src/api.ts) y de páginas/componentes que los consumen. El backend se valida contra [core/urls.py](../core/urls.py), [core/viewsets.py](../core/viewsets.py), [core/views_attendance.py](../core/views_attendance.py), [core/views_devices.py](../core/views_devices.py), [core/views_system.py](../core/views_system.py) y [core/views_stubs.py](../core/views_stubs.py).

### 2.1 Dispositivos

| Endpoint | Frontend (uso) | Campos consumidos | Campos ignorados | Campos calculados en frontend (⚠️) | Backend | Observaciones |
|---|---|---|---|---|---|---|
| GET /devices/ | Lista dispositivos | id, name, ip, port, enabled, serialnumber, user_count, transaction_count, last_seen | otros campos del Device | last_seen formateado a local string | DeviceViewSet list | Devuelve array directo (sin paginación). |
| POST /devices/ | Crear dispositivo | payload completo Device | n/a | n/a | DeviceViewSet create | OK. |
| GET /devices/{id} | Detalle dispositivo | id, name, ip, port, enabled, serialnumber, etc. | n/a | n/a | DeviceViewSet retrieve | OK. |
| GET /devices/connection-status/all/ | Estado conexión | devices[]: device_id, name, enabled, connected, message | n/a | mapeo a dict por device_id | all_devices_status | OK. |
| POST /devices/{id}/test-connection/ | Job test conexión | job_id, status | n/a | n/a | test_connection | Async job. |
| GET /devices/{id}/test-connection-sync/ | Test sync | online, device_id, name, error? | n/a | n/a | test_connection_sync | OK. |
| POST /devices/{id}/import-attendance/ | Importación | job_id, status | n/a | n/a | import_attendance | Async job. |
| POST /devices/{id}/clear-attendance/ | Limpiar marcaciones | job_id, status | n/a | n/a | clear_attendance | Async job. |
| POST /devices/{id}/download-users/ | Descargar usuarios | job_id, status | n/a | n/a | download_users | Async job. |
| POST /devices/{id}/sync-users/ | Sincronizar usuarios | job_id, status | n/a | n/a | sync_users | Async job. |
| POST /devices/{id}/clear-all-data/ | Limpiar todo | job_id, status | n/a | n/a | clear_all_data | Async job. |
| POST /devices/{id}/restart | Reiniciar | success, message | n/a | n/a | restart_device | OK. |
| POST /devices/{id}/poweroff | Apagar | success, message | n/a | n/a | poweroff_device | OK. |
| POST /devices/{id}/sync-time | Sincronizar hora | success, message | n/a | n/a | sync_time | OK. |
| POST /devices/{id}/test-voice | Test voz | success, message | n/a | n/a | test_voice | OK. |
| GET /devices/{id}/memory | Memoria | users, users_cap, fingers, fingers_cap, records, records_cap | n/a | n/a | get_memory_info | OK. |
| GET /devices/{id}/attendance/recent | Marcaciones recientes | records[] (user_id, timestamp, status, punch) | n/a | n/a | get_recent_attendance | ⚠️ Método custom en zk_service. |
| POST /devices/{id}/templates | Plantillas | count, templates[] (uid,fid,size,valid) | n/a | n/a | get_device_templates | ⚠️ Método custom en zk_service. |
| GET /devices/{id}/users/ | Usuarios en device | uid, user_id, name, privilege, card, etc. | n/a | n/a | get_device_users | OK. |
| GET /devices/{id}/info/ | Info device | firmware_version, serial_number, platform, mac, device_name, users_count, fingers_count, records_count | n/a | n/a | get_device_info | OK. |

**Lógica frontend relevante:**
- Dashboard y DeviceList calculan estado UI (colores, badges) en base a `enabled` y `connected`.
- DeviceDetail encapsula lógica de jobs y espera `job_id` en responses async.

---

### 2.2 Asistencia - Day View / Timeline / Explanation

| Endpoint | Frontend (uso) | Campos consumidos | Campos ignorados | Campos calculados en frontend (⚠️) | Backend | Observaciones |
|---|---|---|---|---|---|---|
| GET /attendance/day/?employee_id=&date= | DayViewPage, Dashboard | status, worked_minutes, logs[] | otros campos potenciales | Formatea horas; badge color | get_simple_day_view | Endpoint mínimo, no usa Timetable. |
| GET /attendance/{id}/timeline/{date}/ | DayTimeline | blocks[]: type,start_time,end_time,duration_minutes | n/a | formatea hora, color por tipo | stub_timeline | Dev-only stub. |
| GET /attendance/{id}/explanation/{date}/ | DayExplanation | summary, anomalies[], recommendations[] | n/a | n/a | stub_explanation | Silencioso si falla. |

**Lógica frontend relevante:**
- DayTimeline interpreta `type` con mapping propio; tipos no conocidos quedan con estilo genérico.
- DayExplanation oculta la sección si falla la API o si no hay contenido.

---

### 2.3 Asistencia - Reports

| Endpoint | Frontend (uso) | Campos consumidos | Campos ignorados | Campos calculados en frontend (⚠️) | Backend | Observaciones |
|---|---|---|---|---|---|---|
| GET /attendance/reports/daily/?from_date=&to_date=&department_id= | Reports, AttentionList | status, worked_minutes, overtime_minutes, late_minutes, early_minutes, check_in, check_out, employee_name, employee_id | otros campos del DailyAttendance | totalHours, totales por depto, badges de severidad | daily_reports | Respuesta array. |

**Lógica frontend relevante:**
- Reports calcula totales por departamento (presentes, ausentes, horas).
- AttentionList filtra “problemáticos” si status != Normal y calcula severidad.

---

### 2.4 Asistencia - Schedules (Timetables/Shifts/Assignments)

| Endpoint | Frontend (uso) | Campos consumidos | Campos ignorados | Campos calculados en frontend (⚠️) | Backend | Observaciones |
|---|---|---|---|---|---|---|
| GET /schedules/timetables/ | Timetables | name, on_duty_time, off_duty_time, is_flexible, late_allow_minutes, early_leave_allow_minutes | otros campos | Render ‘-’ si flexible | TimetableViewSet list | Alias esperado por frontend. |
| POST /schedules/timetables/ | Timetables | payload Timetable | n/a | n/a | TimetableViewSet create | OK. |
| PUT /schedules/timetables/{id} | Timetables | payload Timetable | n/a | n/a | TimetableViewSet update | OK. |
| DELETE /schedules/timetables/{id} | Timetables | n/a | n/a | n/a | TimetableViewSet delete | OK. |
| GET /shifts/ | Shifts | id, name | n/a | n/a | ShiftViewSet list | OK. |
| POST /shifts/ | Shifts | name | n/a | n/a | ShiftViewSet create | OK. |
| DELETE /shifts/{id}/ | Shifts | n/a | n/a | n/a | ShiftViewSet delete | OK. |
| GET /shifts/{id}/timetables/ | Shifts | timetable_id, day_index | timetable_name si no viene | n/a | ShiftViewSet.timetables() | OK. |
| POST /shifts/{id}/timetables/ | Shifts | list de {timetable_id, day_index} | n/a | n/a | ShiftViewSet.timetables() | OK. |
| GET /employee-shifts/ | EmployeeSchedule | scope, employee_id, department_id, shift_id, start_date, end_date | n/a | n/a | EmployeeShiftViewSet list | OK. |
| POST /employee-shifts/ | EmployeeSchedule | payload con scope | n/a | n/a | EmployeeShiftViewSet create | OK. |

**Lógica frontend relevante:**
- EmployeeSchedule filtra empleados por depto en frontend si API no filtra.
- Timetables oculta campos evaluativos cuando is_flexible.

---

### 2.5 Personal / Organización

| Endpoint | Frontend (uso) | Campos consumidos | Campos ignorados | Campos calculados en frontend (⚠️) | Backend | Observaciones |
|---|---|---|---|---|---|---|
| GET /employees/ | Employees, EmployeeSchedule, Dashboard | id, user_id, name, department_id, department_name | otros campos | filtros locales, export CSV/XLSX | EmployeeViewSet list | Si hay skip/limit, retorna array directo. |
| POST /employees/ | Employees | payload completo Employee | n/a | n/a | EmployeeViewSet create | OK. |
| PUT /employees/{id} | Employees | payload completo Employee | n/a | n/a | EmployeeViewSet update | OK. |
| DELETE /employees/{id} | Employees | n/a | n/a | n/a | EmployeeViewSet delete | OK. |
| POST /employees/import | Employees | FormData file | n/a | n/a | ❌ No existe | Endpoint roto en frontend. |
| GET /departments/ | Departments, Employees, EmployeeSchedule | id, name, parent_id | children? | tree client-side | DepartmentViewSet list | OK. |
| POST /departments/ | Departments | payload | n/a | n/a | DepartmentViewSet create | OK. |
| PUT /departments/{id} | Departments | payload | n/a | n/a | DepartmentViewSet update | OK. |
| DELETE /departments/{id} | Departments | n/a | n/a | n/a | DepartmentViewSet delete | OK. |
| GET /positions/ | Positions | id, name, code | description? | n/a | PositionViewSet list | OK. |
| POST /positions/ | Positions | payload | n/a | n/a | PositionViewSet create | OK. |
| PUT /positions/{id} | Positions | payload | n/a | n/a | PositionViewSet update | OK. |
| DELETE /positions/{id} | Positions | n/a | n/a | n/a | PositionViewSet delete | OK. |
| GET /zones/ | Zones | id, name, code | description? | n/a | ZoneViewSet list | OK. |
| POST /zones/ | Zones | payload | n/a | n/a | ZoneViewSet create | OK. |
| PUT /zones/{id} | Zones | payload | n/a | n/a | ZoneViewSet update | OK. |
| DELETE /zones/{id} | Zones | n/a | n/a | n/a | ZoneViewSet delete | OK. |
| GET /companies/ | Company | id, name, code, address, website, logo_path | n/a | n/a | CompanyViewSet list | OK. |
| PUT /companies/{id} | Company | payload | n/a | n/a | CompanyViewSet update | OK. |

---

### 2.6 Ausencias

| Endpoint | Frontend (uso) | Campos consumidos | Campos ignorados | Campos calculados en frontend (⚠️) | Backend | Observaciones |
|---|---|---|---|---|---|---|
| GET /attendance/absences/ | Absences | id, employee_id, start_date, end_date, type, reason | approved? | filtra por texto local | LeaveViewSet list (alias) | OK (alias). |
| POST /attendance/absences/ | Absences | payload Absence | n/a | n/a | LeaveViewSet create | OK. |
| DELETE /attendance/absences/{id} | Absences | n/a | n/a | n/a | LeaveViewSet delete | ⚠️ Alias solo GET en urls.py. |

---

### 2.7 Auth (Frontend espera, backend deshabilitado)

| Endpoint | Frontend (uso) | Campos consumidos | Campos ignorados | Campos calculados en frontend (⚠️) | Backend | Observaciones |
|---|---|---|---|---|---|---|
| POST /auth/login | Login | access_token, token_type, username, role | extras | n/a | auth_login (comentado) | ❌ Disabled en urls.py. |
| GET /auth/users | System Users | id, username, role flags, email | n/a | n/a | auth_users_list (comentado) | ❌ Disabled. |
| POST /auth/users | System Users | payload user | n/a | n/a | auth_users_list (comentado) | ❌ Disabled. |
| DELETE /auth/users/{id} | System Users | n/a | n/a | n/a | auth_user_delete (comentado) | ❌ Disabled. |
| PUT /auth/users/{id}/password | System Users | password | n/a | n/a | auth_user_password_update (comentado) | ❌ Disabled. |

---

### 2.8 Settings y Jobs

| Endpoint | Frontend (uso) | Campos consumidos | Campos ignorados | Campos calculados en frontend (⚠️) | Backend | Observaciones |
|---|---|---|---|---|---|---|
| GET /settings/ | Settings | key, value, description | n/a | agrupación por prefijo | SettingViewSet list | OK. |
| PUT /settings/{key}/ | Settings | key, value | n/a | n/a | SettingViewSet update | OK. |
| GET /jobs/{id} | JobProgressModal | Job fields | n/a | n/a | get_job | OK. |
| GET /jobs/{id}/logs | JobProgressModal | log_output, status, progress | n/a | n/a | get_job_logs | OK. |
| POST /system/database/backup | Settings | success, message, file, size_mb | n/a | n/a | database_backup | OK. |
| GET /system/database/backups | Settings | backups[] | n/a | n/a | list_backups | OK. |
| POST /system/database/restore | Settings | success, message | n/a | n/a | database_restore | OK. |
| GET /system/database/test | Settings | database, tables_count, tables, size_mb, connection | n/a | n/a | database_test | OK. |
| POST /system/database/import | Settings | success, message | n/a | n/a | database_import | OK. |

---

## 3) Supuestos del Frontend y contratos implícitos

### 3.1 Supuestos de respuesta (arrays vs paginación)
- Frontend espera **arrays directos** en la mayoría de endpoints (getDevices, getDepartments, etc.).
- Backend adapta list() en varios ViewSets para devolver arrays sin paginación (compatibilidad FastAPI).

### 3.2 Contratos implícitos no documentados
- `/attendance/day/` devuelve **status**, **worked_minutes** y **logs[]** con alternancia naive.
- `/attendance/{id}/timeline/{date}/` y `/explanation/` son **stubs DEV** y se asumen como definitivos en UI.
- `/attendance/absences/` se usa como CRUD completo, pero en urls.py solo existe alias GET; DELETE directo usa ruta real de LeaveViewSet.

### 3.3 Lógica en frontend que debería vivir en backend (observación, no cambio)
- Cálculo de “presentes/ausentes/horas” por departamento en Reports.
- Severidad de “Requiere Atención” en AttentionList.
- Derivación de tipos IN/OUT por índice en DayViewPage (logs del endpoint mínimo ya vienen sin punch real).

---

## 4) Riesgos de desacople

1. **Auth deshabilitado**: el frontend llama `/auth/*`, pero backend no expone esos endpoints en urls.py.
2. **Endpoint de import empleados** (`/employees/import`) no existe; UI conserva función aunque import esté “disabled”.
3. **Stubs de Timeline/Explanation** son aceptados como contrato estable, pero son “DEV MODE”.
4. **Absences DELETE**: frontend asume `/attendance/absences/{id}` pero alias en urls.py solo GET.
5. **Device templates / recent attendance**: backend usa métodos custom en zk_service, riesgo de incompatibilidad con pyzk.

---

## 5) Ajustes mínimos necesarios (si los hay)

> **Sin implementar cambios, solo listado**

1. Documentar formalmente los contratos actuales de:
   - `/attendance/day/`
   - `/attendance/{id}/timeline/{date}/`
   - `/attendance/{id}/explanation/{date}/`

2. Alinear el endpoint de ausencias:
   - Confirmar si `/attendance/absences/{id}` debe existir como alias DELETE.

3. Confirmar decisión sobre Auth:
   - Si se mantiene DEV mode, documentar que `/auth/*` no está disponible.

4. Confirmar uso de `/employees/import`:
   - Si no existe, remover o documentar como deshabilitado.

---

## 6) Conclusión

- El frontend y backend están **mayormente alineados** para Alfa, con **contratos implícitos** y **stubs** en el flujo de Day View.
- Existen **desacoples conocidos** (auth, import empleados, alias ausencias, device methods custom). 
- No se requieren cambios de lógica para el cierre Alfa; se recomienda **documentar explícitamente** los contratos usados por UI y las limitaciones vigentes.

---

## 7) Referencias directas

- Frontend API: [frontend/src/api.ts](../frontend/src/api.ts)
- Day View: [frontend/src/pages/asistencia/DayViewPage.tsx](../frontend/src/pages/asistencia/DayViewPage.tsx)
- Timeline UI: [frontend/src/components/asistencia/DayTimeline.tsx](../frontend/src/components/asistencia/DayTimeline.tsx)
- Explanation UI: [frontend/src/components/asistencia/DayExplanation.tsx](../frontend/src/components/asistencia/DayExplanation.tsx)
- Reports UI: [frontend/src/pages/asistencia/Reports.tsx](../frontend/src/pages/asistencia/Reports.tsx)
- Attention List: [frontend/src/components/dashboard/AttentionList.tsx](../frontend/src/components/dashboard/AttentionList.tsx)
- Backend URLs: [core/urls.py](../core/urls.py)
- Attendance Views: [core/views_attendance.py](../core/views_attendance.py)
- Device Views: [core/views_devices.py](../core/views_devices.py)
- System Views: [core/views_system.py](../core/views_system.py)
- Viewsets: [core/viewsets.py](../core/viewsets.py)
- Stubs: [core/views_stubs.py](../core/views_stubs.py)
