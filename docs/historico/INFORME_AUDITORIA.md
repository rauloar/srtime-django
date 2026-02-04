# 🔍 INFORME DE AUDITORÍA - SRTime Django
**Fecha:** 2026-02-02  
**Objetivo:** Detectar roturas, inconsistencias y código muerto post-migración frontend duplicado

---

## 1️⃣ FRONTEND – ESTRUCTURA Y DUPLICADOS

### ✅ Frontend Único Confirmado
- **Activo:** `frontend/` (React 18 + Vite)
- **Build target:** `frontend/dist/` ❌ **NO EXISTE** (debe generarse con `npm run build`)
- **Servido por Django:** `static/` (contiene build antiguo)
- **NO hay duplicados:** No existe `SRTimeWeb/`, `ui-stitch/` ni otros frontends en este proyecto

### 🔴 Problema Crítico: Build Desactualizado
- **`frontend/dist/`:** NO EXISTE (verificado con `Test-Path`)
- **`static/`:** Contiene build viejo con archivos:
  - `static/index.html` → referencia `index-DlLlJ3i4.js` y `index-CeOV9uu0.css`
  - Assets existen en `static/assets/` pero pueden estar desactualizados
- **Impacto:** 🔴 **PRODUCCIÓN ROTA** - Django sirve build viejo, cambios en `frontend/src/` no se reflejan
- **Dev Mode:** ✅ OK (Vite sirve directo desde `src/` en puerto 5173)

---

## 🔴 ERRORES CONFIRMADOS (Rompen ejecución)

### 1. **Stubs Timeline/Explanation NO REGISTRADOS**
- **Frontend usa:** 
  - `GET /attendance/${employeeId}/timeline/${date}/` (api.ts:562)
  - `GET /attendance/${employeeId}/explanation/${date}/` (api.ts:565)
- **Backend:** 
  - Stubs existen en `views_stubs.py`
  - ❌ **IMPORTADOS** en `urls.py:30` pero **NO REGISTRADOS** en `urlpatterns`
- **Usado en:** `DayTimeline.tsx:25`, `DayExplanation.tsx:24`
- **Impacto:** 🔴 Day View **404 NOT FOUND**

### 2. **Endpoint `/employees/import` NO EXISTE**
- **Frontend usa:** `POST /employees/import` (api.ts:330)
- **Backend:** ❌ NO EXISTE (búsqueda exhaustiva: no hay `import_employees` en views/viewsets)
- **Usado en:** `Employees.tsx:135`
- **Impacto:** 🔴 Botón "Importar CSV/Excel" ROTO

### 3. **Endpoints `/auth/*` DESHABILITADOS**
- **Frontend usa:** 
  - `POST /auth/login` (api.ts:534)
  - `GET /auth/users`, `POST /auth/users`, `DELETE /auth/users/{id}`, `PUT /auth/users/{id}/password`
- **Backend:** ❌ **COMENTADOS** en `core/urls.py:75-80` con nota "DISABLED FOR DEV MODE"
- **Impacto:** 🔴 Login y gestión de usuarios **DESHABILITADOS** (dev mode sin auth)

---

## 2️⃣ BUILD & STATIC FILES

### Estado Actual
```
frontend/
├── src/           ✅ Código fuente React activo
├── vite.config.ts ✅ Build configurado: outDir: '../static'
└── dist/          ❌ NO EXISTE (npm run build no ejecutado)

static/
├── index.html     ✅ Build antiguo
├── assets/
│   ├── index-DlLlJ3i4.js   ✅ Existe
│   └── index-CeOV9uu0.css  ✅ Existe
└── img/sr-logo.png ✅ Existe
```

### 🔴 CRÍTICO: Build Desactualizado
- **Vite config:** `build.outDir = '../static'` → sobrescribe `static/` directamente
- **Problema:** `npm run build` NO se ha ejecutado recientemente
- **Evidencia:** `frontend/dist/` no existe (Vite NO genera dist/, va directo a `static/`)
- **Impacto:** 
  - 🟢 Dev mode OK (Vite sirve desde `src/` en 5174)
  - 🔴 Prod mode ROTO (Django sirve build viejo de `static/`)

### Flujo Correcto
1. Editar código en `frontend/src/`
2. Ejecutar `npm run build` → genera assets en `static/`
3. Django sirve desde `static/index.html`

---

## 3️⃣ FRONTEND → BACKEND (Endpoints API)

## 3️⃣ FRONTEND → BACKEND (Endpoints API)

### Tabla de Endpoints Verificados

| Endpoint | Usado en Frontend | Backend | Estado |
|----------|-------------------|---------|--------|
| `POST /auth/login` | api.ts:534 | ❌ Comentado (urls.py:75) | 🔴 ROTO |
| `GET /auth/users` | api.ts:535 | ❌ Comentado (urls.py:76) | 🔴 ROTO |
| `POST /auth/users` | api.ts:536 | ❌ Comentado (urls.py:76) | 🔴 ROTO |
| `DELETE /auth/users/{id}` | api.ts:537 | ❌ Comentado (urls.py:77) | 🔴 ROTO |
| `PUT /auth/users/{id}/password` | api.ts:538 | ❌ Comentado (urls.py:78) | 🔴 ROTO |
| `POST /employees/import` | api.ts:330, Employees.tsx:135 | ❌ NO EXISTE | 🔴 ROTO |
| `GET /attendance/{id}/timeline/{date}/` | api.ts:562, DayTimeline.tsx:25 | ❌ Stub importado pero NO registrado | 🔴 404 |
| `GET /attendance/{id}/explanation/{date}/` | api.ts:565, DayExplanation.tsx:24 | ❌ Stub importado pero NO registrado | 🔴 404 |
| `GET /shifts/{id}/timetables/` | api.ts:381, Shifts.tsx | ✅ ShiftViewSet.timetables() @action | 🟢 OK |
| `POST /shifts/{id}/timetables/` | api.ts:376, Shifts.tsx:232 | ✅ ShiftViewSet.timetables() @action | 🟢 OK |
| `GET /devices/` | api.ts:115 | ✅ router.register (urls.py:44) | 🟢 OK |
| `POST /devices/` | api.ts:116 | ✅ DeviceViewSet | 🟢 OK |
| `GET /devices/connection-status/all/` | api.ts:118 | ✅ all_devices_status (urls.py:86) | 🟢 OK |
| `POST /devices/{id}/test-connection/` | api.ts:121 | ✅ test_connection (urls.py:88) | 🟢 OK |
| `GET /devices/{id}/test-connection-sync/` | api.ts:137 | ✅ test_connection_sync (urls.py:89) | 🟢 OK |
| `POST /devices/{id}/import-attendance/` | api.ts:122 | ✅ import_attendance (urls.py:90) | 🟢 OK |
| `POST /devices/{id}/restart` | api.ts:138 | ✅ restart_device (urls.py:105) | 🟢 OK |
| `POST /devices/{id}/poweroff` | api.ts:139 | ✅ poweroff_device (urls.py:106) | 🟢 OK |
| `POST /devices/{id}/sync-time` | api.ts:140 | ✅ sync_time (urls.py:107) | 🟢 OK |
| `POST /devices/{id}/test-voice` | api.ts:141 | ✅ test_voice (urls.py:108) | 🟢 OK |
| `GET /devices/{id}/memory` | api.ts:142 | ✅ get_memory_info (urls.py:109) | 🟢 OK |
| `GET /devices/{id}/attendance/recent` | api.ts:143 | ✅ get_recent_attendance (urls.py:110) | 🟡 Ver nota¹ |
| `POST /devices/{id}/templates` | api.ts:144 | ✅ get_device_templates (urls.py:111) | 🟡 Ver nota² |
| `GET /devices/{id}/info/` | api.ts:209 | ✅ get_device_info (urls.py:113) | 🟢 OK |
| `GET /devices/{id}/users/` | api.ts:210 | ✅ get_device_users (urls.py:112) | 🟢 OK |
| `GET /attendance/` | api.ts:238 | ✅ AttendanceLogViewSet (urls.py:45) | 🟢 OK |
| `GET /settings/` | api.ts:243 | ✅ SettingViewSet (urls.py:51) | 🟢 OK |
| `PUT /settings/{key}/` | api.ts:244 | ✅ SettingViewSet | 🟢 OK |
| `GET /jobs/{id}` | api.ts:245 | ✅ get_job (urls.py:115) | 🟢 OK |
| `GET /jobs/{id}/logs` | api.ts:246 | ✅ get_job_logs (urls.py:116) | 🟢 OK |
| `GET /companies/` | api.ts:255 | ✅ CompanyViewSet (urls.py:37) | 🟢 OK |
| `PUT /companies/{id}/` | api.ts:256 | ✅ CompanyViewSet | 🟢 OK |
| `GET /positions/` | api.ts:265 | ✅ PositionViewSet (urls.py:38) | 🟢 OK |
| `POST /positions/` | api.ts:266 | ✅ PositionViewSet | 🟢 OK |
| `PUT /positions/{id}/` | api.ts:267 | ✅ PositionViewSet | 🟢 OK |
| `DELETE /positions/{id}/` | api.ts:268 | ✅ PositionViewSet | 🟢 OK |
| `GET /zones/` | api.ts:277 | ✅ ZoneViewSet (urls.py:39) | 🟢 OK |
| `POST /zones/` | api.ts:278 | ✅ ZoneViewSet | 🟢 OK |
| `PUT /zones/{id}/` | api.ts:279 | ✅ ZoneViewSet | 🟢 OK |
| `DELETE /zones/{id}/` | api.ts:280 | ✅ ZoneViewSet | 🟢 OK |
| `GET /departments/` | api.ts:291 | ✅ DepartmentViewSet (urls.py:40) | 🟢 OK |
| `POST /departments/` | api.ts:292 | ✅ DepartmentViewSet | 🟢 OK |
| `PUT /departments/{id}` | api.ts:293 | ✅ DepartmentViewSet | 🟢 OK |
| `DELETE /departments/{id}` | api.ts:294 | ✅ DepartmentViewSet | 🟢 OK |
| `GET /employees/` | api.ts:296 | ✅ EmployeeViewSet (urls.py:41) | 🟢 OK |
| `GET /employees/{id}` | api.ts:298 | ✅ EmployeeViewSet | 🟢 OK |
| `POST /employees/` | api.ts:299 | ✅ EmployeeViewSet | 🟢 OK |
| `PUT /employees/{id}` | api.ts:300 | ✅ EmployeeViewSet | 🟢 OK |
| `DELETE /employees/{id}` | api.ts:301 | ✅ EmployeeViewSet | 🟢 OK |
| `GET /schedules/timetables/` | api.ts:366 | ✅ Alias en urls.py:128 | 🟢 OK |
| `POST /schedules/timetables/` | api.ts:367 | ✅ Alias en urls.py:128 | 🟢 OK |
| `PUT /schedules/timetables/{id}` | api.ts:368 | ✅ TimetableViewSet | 🟢 OK |
| `DELETE /schedules/timetables/{id}` | api.ts:369 | ✅ TimetableViewSet | 🟢 OK |
| `GET /shifts/` | api.ts:371 | ✅ ShiftViewSet (urls.py:57) | 🟢 OK |
| `POST /shifts/` | api.ts:372 | ✅ ShiftViewSet | 🟢 OK |
| `DELETE /shifts/{id}/` | api.ts:373 | ✅ ShiftViewSet | 🟢 OK |
| `POST /employee-shifts/` | api.ts:398 | ✅ EmployeeShiftViewSet (urls.py:60) | 🟢 OK |
| `GET /employee-shifts/` | api.ts:417 | ✅ EmployeeShiftViewSet | 🟢 OK |
| `POST /attendance/calculate` | api.ts:456 | ✅ calculate_attendance (urls.py:81) | 🟢 OK |
| `GET /attendance/reports/daily/` | api.ts:463 | ✅ daily_reports (urls.py:83) | 🟢 OK |
| `GET /attendance/absences/` | api.ts:476 | ✅ Alias LeaveViewSet (urls.py:141) | 🟢 OK |
| `POST /attendance/absences/` | api.ts:481 | ✅ LeaveViewSet | 🟢 OK |
| `DELETE /attendance/absences/{id}` | api.ts:482 | ✅ LeaveViewSet | 🟢 OK |
| `POST /system/database/backup` | api.ts:550 | ✅ database_backup (urls.py:118) | 🟢 OK |
| `GET /system/database/backups` | api.ts:551 | ✅ list_backups (urls.py:119) | 🟢 OK |
| `POST /system/database/restore` | api.ts:552 | ✅ database_restore (urls.py:120) | 🟢 OK |
| `GET /system/database/test` | api.ts:553 | ✅ database_test (urls.py:121) | 🟢 OK |
| `POST /system/database/import` | api.ts:554 | ✅ database_import (urls.py:122) | 🟢 OK |

**Notas:**
- ¹ `get_recent_attendance()`: Llama a `zk_service.get_recent_attendance()` que NO existe en librería pyzk (método custom)
- ² `get_templates()`: Llama a `zk_service.get_templates()` que NO existe en librería pyzk (método custom)

---

## 4️⃣ DJANGO URLS & SPA ROUTING

### 1. **`get_recent_attendance()` inexistente en pyzk**
- **Problema:** `zk.py:282` define `get_recent_attendance()` pero NO existe en librería `pyzk`
- **Evidencia:** Método custom, no parte de ZKService estándar
- **Impacto:** 🟡 Si se usa, fallará con AttributeError
- **Usado en:** `views_devices.py:311` → endpoint `/devices/{id}/attendance/recent`

### 2. **`get_templates()` inexistente en pyzk**
- **Problema:** `zk.py:308` define `get_templates()` pero NO existe en librería `pyzk`
- **Backend usa:** `views_devices.py:338` llama `zk_service.get_templates()`
- **Frontend usa:** `api.ts:146` → `POST /devices/{id}/templates`
- **Impacto:** 🟡 Si se ejecuta, fallará con AttributeError

### 3. **Permisos `@permission_classes([IsAuthenticated])` en DEV Mode**
- **Problema:** Todos los endpoints device tienen `IsAuthenticated` pero auth está deshabilitado
- **Evidencia:** `config/settings.py:111` → `DEFAULT_PERMISSION_CLASSES: AllowAny`
- **Impacto:** 🟢 Sin impacto real (AllowAny override global), pero inconsistente

### 4. **Frontend espera paginación manual (`skip`, `limit`)**
- **Frontend usa:** `getEmployees(skip, limit)` en `api.ts:319`
- **Backend:** `EmployeeViewSet.list()` en `viewsets.py:104` implementa lógica custom
- **Impacto:** 🟢 Funciona, pero raro (DRF tiene paginación nativa)

---

## 🟢 CÓDIGO MUERTO / LEGACY

### 1. **Módulo Forense Completo (NO usado por frontend actual)**

#### Archivos forenses:
```
core/api/forensic/          ← 6 archivos (views, serializers, permissions, urls)
core/api/adjustment_views.py
core/api/operational_views.py
core/api/snapshot_views.py
core/api/timeline_views.py
core/services/forensic/     ← 3 servicios forenses
core/services/shadow/       ← 2 servicios shadow
core/services/processors/   ← 2 procesadores
core/models_forensic.py
core/models_shadow.py
core/models_operational_*.py
core/models_timeline.py
core/models_engine_snapshot.py
core/domain/flexible/       ← 11 archivos dominio flexible
tests/forensic/             ← Tests forenses
tests/shadow/               ← Tests shadow
tests/api/test_forensic_api.py
```

#### Evidencia:
- **Frontend NO usa:** Ningún endpoint en `core/api/forensic/urls.py`
- **Frontend NO importa:** Ninguna función de endpoints forenses
- **Total:** ~30 archivos forenses sin uso en frontend

#### Impacto:
- 🟢 **No rompe nada**, pero infla el proyecto
- ⚠️ Posible deuda técnica si se planea usar después

### 2. **Vistas Stub Sin Registrar en URLs**
- **Archivo:** `core/views_stubs.py`
- **Funciones:** `stub_timeline()`, `stub_explanation()`
- **Estado:** ✅ Sí registradas en `core/urls.py` (líneas NO encontradas en urls.py actual)
- **Aclaración:** ❌ **NO ESTÁN REGISTRADAS** en `core/urls.py`
- **Impacto:** 🔴 Frontend llama pero **404 NOT FOUND**

### 3. **Referencias "SRTimeWeb" en Frontend**
- **Archivos:**
  - `frontend/src/pages/auth/Login.tsx:43` → `<h2>SRTimeWeb</h2>`
  - `frontend/src/pages/auth/Login.tsx:91` → `© SRTimeWeb - DEV MODE`
  - `frontend/src/components/layout/Topbar.tsx:51` → `<span>SRTimeWeb</span>`
- **Impacto:** 🟢 Cosmético, no rompe funcionalidad

### 4. **Sistema de Jobs (Usado pero incompleto)**
- **Backend:** Job tracking en `core/services/jobs.py` + workers en `zk_workers.py`
- **Frontend usa:** `getJob()`, `getJobLogs()` en api.ts
- **Problema:** No hay cleanup automático de jobs antiguos
- **Impacto:** 🟡 Base de datos acumula jobs sin `cleanup_old_jobs()` scheduled

## 4️⃣ DJANGO URLS & SPA ROUTING

### Verificación `config/urls.py`
```python
urlpatterns = [
    path('admin/', admin.site.urls),                    # ✅ Admin first
    path('api/v1/', include('core.urls')),              # ✅ API before catch-all
    path('api/token/', TokenObtainPairView...),         # ✅ JWT tokens
]
# ... static files in DEBUG mode ...
urlpatterns += [
    path('', TemplateView...('index.html')),            # ✅ Root → SPA
    re_path(r'^.*$', TemplateView...('index.html')),    # ✅ Catch-all → SPA
]
```

### ✅ Estado: CORRECTO
- API `/api/v1/*` registrado **ANTES** del catch-all
- SPA fallback `^.*$` captura todas las rutas React
- NO hay colisiones entre rutas API y SPA

### ⚠️ URLs Redundantes Detectadas
```python
# urls.py:98 - Alias duplicados
path('devices/<int:device_id>/test_connection', test_connection, ...),
path('devices/<int:device_id>/test_connection', test_connection, ...),  # DUPLICADO línea 99
```

### 🟡 Alias FastAPI Legacy (líneas 97-104)
Existen aliases para compatibilidad con frontend antiguo:
- `attendance/import` → `import-attendance/`
- `users/download` → `download-users/`
- Etc.

**No rompen nada** pero son redundantes si frontend ya usa paths Django.

---

## 5️⃣ MODELOS & DB

### Modelos Usados por Frontend (Dashboard/Day View)
| Modelo | Archivo | Estado |
|--------|---------|--------|
| `Employee` | models.py | ✅ Existe |
| `Device` | models.py | ✅ Existe |
| `AttendanceLog` | models.py | ✅ Existe |
| `DailyAttendance` | models.py | ✅ Existe |
| `Timetable` | models.py | ✅ Existe |
| `Shift` | models.py | ✅ Existe |
| `ShiftTimetable` | models.py | ✅ Existe |
| `EmployeeShift` | models.py | ✅ Existe |
| `Department` | models.py | ✅ Existe |
| `Job` | models.py | ✅ Existe |
| `JobLog` | models.py | ✅ Existe |

### ✅ Sin Dependencias Rotas
Todos los modelos básicos existen y funcionan.

---

## 6️⃣ COSMÉTICO / LEGACY

### Referencias "SRTimeWeb" (🟢 Cosmético)
| Archivo | Línea | Texto |
|---------|-------|-------|
| `Login.tsx` | 43 | `<h2>SRTimeWeb</h2>` |
| `Login.tsx` | 91 | `© SRTimeWeb - DEV MODE` |
| `Topbar.tsx` | 51 | `<span>SRTimeWeb</span>` |
| `static/index.html` | 8 | `<title>SRTimeWeb - Service Reloj</title>` |

**Impacto:** 🟢 Solo visual, no rompe funcionalidad.

---

## 🟡 RIESGOS REALES

## 🟡 RIESGOS REALES

### 1. **Métodos pyzk Inexistentes** 🟡
- **`get_recent_attendance()`** (zk.py:282): Método custom NO en librería pyzk
  - Usado en: `views_devices.py:311` → endpoint `/devices/{id}/attendance/recent`
  - **Falla si:** Se ejecuta y pyzk no tiene este método
  
- **`get_templates()`** (zk.py:308): Método custom NO en librería pyzk
  - Usado en: `views_devices.py:338` → endpoint `/devices/{id}/templates`
  - **Falla si:** Se ejecuta y pyzk no tiene este método

### 2. **Permisos Inconsistentes** 🟢
- Todos los endpoints device tienen `@permission_classes([IsAuthenticated])`
- Pero `settings.py:111` → `DEFAULT_PERMISSION_CLASSES: AllowAny`
- **Impacto:** 🟢 Sin impacto real (AllowAny override global), pero confuso

### 3. **Jobs Sin Cleanup** 🟡
- `jobs.py` tiene `cleanup_old_jobs()` pero NO se llama automáticamente
- **Impacto:** 🟡 DB acumula jobs viejos sin límite

---

## 🟢 CÓDIGO MUERTO / LEGACY

### Sistema Forense Completo (~30 archivos)
```
core/api/forensic/          ← 6 archivos
core/api/adjustment_views.py
core/api/operational_views.py
core/api/snapshot_views.py
core/api/timeline_views.py
core/services/forensic/     ← 3 servicios
core/services/shadow/       ← 2 servicios
core/services/processors/   ← 2 procesadores
core/models_forensic.py
core/models_shadow.py
core/models_operational_*.py
core/models_timeline.py
core/models_engine_snapshot.py
core/domain/flexible/       ← 11 archivos
tests/forensic/
tests/shadow/
tests/api/test_forensic_api.py
```

**Evidencia:** Frontend NO usa ningún endpoint forense.  
**Impacto:** 🟢 No rompe nada, pero infla el proyecto.

---

## 📋 RESUMEN EJECUTIVO

### 🔴 Errores Críticos (P1 - Rompen funcionalidad)
| # | Problema | Archivos | Impacto |
|---|----------|----------|---------|
| 1 | Stubs timeline/explanation NO registrados | urls.py, views_stubs.py | Day View → 404 |
| 2 | `/employees/import` no existe | api.ts, Employees.tsx | Botón importar roto |
| 3 | `/auth/*` deshabilitados | urls.py:75-80 | Login/Users roto |
| 4 | Build desactualizado | static/ vs frontend/src/ | Cambios no se ven en prod |

### 🟡 Riesgos (P2 - Fallan si se usan)
| # | Problema | Impacto |
|---|----------|---------|
| 1 | `get_recent_attendance()` no en pyzk | AttributeError al usar endpoint |
| 2 | `get_templates()` no en pyzk | AttributeError al usar endpoint |
| 3 | Jobs sin cleanup | DB crece sin control |

### 🟢 Código Muerto (P3 - Limpieza)
| # | Categoría | Archivos | Estado |
|---|-----------|----------|--------|
| 1 | Sistema forense | ~30 archivos | Sin uso en frontend |
| 2 | Referencias "SRTimeWeb" | 4 líneas | Cosmético |
| 3 | Alias FastAPI legacy | urls.py:97-104 | Redundantes |

---

## 🎯 ACCIONES PRIORIZADAS

### P1 - CRÍTICO (Rompe ejecución)
1. ✅ **Registrar stubs en urls.py:**
   ```python
   path('attendance/<int:employee_id>/timeline/<str:date>/', stub_timeline, ...),
   path('attendance/<int:employee_id>/explanation/<str:date>/', stub_explanation, ...),
   ```

2. ✅ **Decisión sobre `/employees/import`:**
   - Opción A: Implementar endpoint con lógica CSV/Excel
   - Opción B: Remover botón del frontend

3. ✅ **Decisión sobre `/auth/*`:**
   - Opción A: Habilitar endpoints (descomentar urls.py:75-80)
   - Opción B: Remover Login/Users del frontend (usar dev sin auth)

4. ✅ **Ejecutar build:**
   ```bash
   cd frontend && npm run build
   ```
   → Actualiza `static/` con código actual

### P2 - RIESGO (Estabilizar)
5. ✅ Verificar si `get_recent_attendance()` y `get_templates()` existen en pyzk
   - Si NO: Implementar o remover endpoints

6. ✅ Script de cleanup de jobs (cron/scheduled task)

### P3 - LIMPIEZA (Opcional)
7. ⚠️ Evaluar si eliminar sistema forense completo
8. ⚠️ Cambiar "SRTimeWeb" a nombre correcto
9. ⚠️ Remover alias FastAPI redundantes

---

**FIN DEL INFORME**
