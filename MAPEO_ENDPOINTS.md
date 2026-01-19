# Mapeo de Endpoints: Frontend React → Django Backend

## ✅ Auth (Ya implementados)
- `POST /api/v1/auth/login` → auth_views.auth_login
- `GET /api/v1/auth/users` → auth_views.auth_users_list
- `POST /api/v1/auth/users` → auth_views.auth_users_list
- `DELETE /api/v1/auth/users/{id}` → auth_views.auth_user_delete
- `PUT /api/v1/auth/users/{id}/password` → auth_views.auth_user_password_update

## ⚠️ Endpoints que necesitan alias o creación

### Devices
- `/devices/` → `/api/v1/devices/` ✅ (Ya existe en DRF router)
- `/devices/{id}` → `/api/v1/devices/{id}/` ✅
- `/devices/connection-status/all` → Crear endpoint personalizado
- `/devices/{id}/test-connection` → Crear endpoint personalizado (async job)
- `/devices/{id}/attendance/import` → Crear endpoint personalizado (async job)
- `/devices/{id}/clear-attendance` → Crear endpoint personalizado
- `/devices/{id}/users/download` → Crear endpoint personalizado
- `/devices/{id}/test-connection-sync` → Crear endpoint personalizado
- `/devices/{id}/restart` → Crear endpoint personalizado
- `/devices/{id}/poweroff` → Crear endpoint personalizado
- `/devices/{id}/sync-time` → Crear endpoint personalizado
- `/devices/{id}/test-voice` → Crear endpoint personalizado
- `/devices/{id}/memory` → Crear endpoint personalizado
- `/devices/{id}/clear-all-data` → Crear endpoint personalizado
- `/devices/{id}/attendance/recent` → Crear endpoint personalizado
- `/devices/{id}/templates` → Crear endpoint personalizado
- `/devices/{id}/info` → Crear endpoint personalizado
- `/devices/{id}/users` → Crear endpoint personalizado

### Attendance Logs
- `/attendance/` → `/api/v1/attendance-logs/` ✅ (Ya existe)

### Settings & Jobs
- `/settings/` → `/api/v1/settings/` ✅ (Ya existe)
- `/jobs/{id}` → `/api/v1/jobs/{id}/` ✅ (Ya existe)
- `/jobs/{id}/logs` → Crear endpoint personalizado para job logs filtrados

### Personnel - Departments
- `/departments/` → `/api/v1/departments/` ✅ (Ya existe)

### Personnel - Employees
- `/employees/` → `/api/v1/employees/` ✅ (Ya existe, pero necesita adaptar paginación)
- `/employees/{id}` → `/api/v1/employees/{id}/` ✅
- `/employees/import` → Crear endpoint personalizado para importación CSV/Excel

### Schedules (Attendance)
- `/schedules/timetables/` → `/api/v1/timetables/` ✅ (Ya existe)
- `/schedules/shifts/` → `/api/v1/shifts/` ✅ (Ya existe)
- `/schedules/shifts/{id}/timetables` → Crear endpoint personalizado
- `/schedules/assign/` → Crear endpoint personalizado
- `/schedules/assignments/` → Crear endpoint personalizado

### Attendance Calculation & Reports
- `/attendance/calculate` → Crear endpoint personalizado
- `/attendance/reports/daily` → `/api/v1/daily-attendance/` ✅ (Ya existe, pero necesita adaptar filtros)
- `/attendance/absences/` → `/api/v1/leaves/` ✅ (Ya existe)

### System Tools
- `/system/database/backup` → Crear endpoint personalizado
- `/system/database/backups` → Crear endpoint personalizado
- `/system/database/restore` → Crear endpoint personalizado
- `/system/database/test` → Crear endpoint personalizado
- `/system/database/import` → Crear endpoint personalizado

## 📋 Prioridad de Implementación

### P0 - Crítico (Login y navegación básica)
1. ✅ Auth endpoints

### P1 - Alta (Funcionalidad principal)
2. Device operations endpoints (con pyzk)
3. Employees CRUD + import
4. Departments CRUD

### P2 - Media (Schedules y reportes)
5. Schedules endpoints
6. Attendance calculation
7. Daily reports adaptados

### P3 - Baja (System tools)
8. Database backup/restore
9. System diagnostics

## 🔄 Estrategia de Implementación

1. Crear endpoints faltantes uno por uno
2. Reusar lógica de FastAPI cuando sea posible
3. Mantener compatibilidad de respuesta JSON exacta
4. No modificar frontend React
