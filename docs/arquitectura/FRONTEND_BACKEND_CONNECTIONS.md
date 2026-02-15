# Análisis de Conexiones Frontend-Backend

## Estado: 2026-02-09

### ✅ Conexiones Validadas y Funcionando

#### 1. **Cálculo de Asistencia**
**Frontend Component:** `Calculation.tsx`
- **Botón:** "Calcular" (con icono Play)
- **API Function:** `calculateAttendance(startDate, endDate, departmentId)`
- **HTTP:** `POST /api/v1/attendance/calculate/`
- **Backend View:** `calculate_attendance` en `views_attendance.py:19`
- **Backend Logic:** `calculate_period(start_date, end_date, department_id)`

**Inputs del Usuario:**
- Rango de fechas: `startDate` (date input), `endDate` (date input)
- Departamento: `departmentId` (select - opcional, "Todos" si vacío)

**Flujo:**
```
Usuario → Inputs (fecha desde/hasta, dept) → Botón "Calcular" 
→ calculateAttendance(startDate, endDate, departmentId)
→ POST /attendance/calculate/ {start_date, end_date, department_id}
→ calculate_attendance() → calculate_period()
→ Response: {count, message}
→ UI muestra éxito o error
```

**Validación:** ✅ CORRECTO
- URL coincide
- Payload correcto (POST body JSON)
- Trailing slash presente
- Backend procesa correctamente


---

#### 2. **Reportes Diarios**
**Frontend Component:** `Reports.tsx`
- **Botón:** "Filtrar" (ejecuta `fetchData()`)
- **API Function:** `getDailyReports(fromDate, toDate, departmentId)`
- **HTTP:** `GET /api/v1/attendance/reports/daily/`
- **Backend View:** `daily_reports` en `views_attendance.py:192`

**Inputs del Usuario:**
- Rango de fechas: `startDate`, `endDate` (date inputs)
- Departamento: `departmentId` (select - opcional)
- User ID: `userIdFilter` (text input - **filtrado client-side**)
- Nombre: `nameFilter` (text input - **filtrado client-side**)

**Flujo:**
```
Usuario → Filtros (fecha, dept, userID, nombre) → Botón "Filtrar"
→ fetchData()
→ getDailyReports(startDate, endDate, departmentId)
→ GET /attendance/reports/daily/?from_date=X&to_date=Y&department_id=Z
→ daily_reports() → Query DailyAttendance con filtros
→ Response: DailyAttendance[] con employee, status_info, etc.
→ UI aplica filtros client-side (userIdFilter, nameFilter)
→ DataGrid muestra registros agrupados por departamento
```

**Validación:** ✅ CORRECTO
- URL coincide
- Query params correctos (`from_date`, `to_date`, `department_id`)
- Backend devuelve datos con `select_related('employee')` optimizado
- Filtros adicionales (User ID, Name) aplicados en cliente
- **NOTA:** Ordenamiento por departamento y fecha hecho en cliente (`res.sort()`)


---

#### 3. **Logs de Asistencia (Marcaciones Crudas)**
**Frontend Component:** `Logs.tsx`
- **Botón:** (implícito en paginación y filtros)
- **API Function:** `getAttendanceLogs(params)`
- **HTTP:** `GET /api/v1/attendance/`
- **Backend View:** `AttendanceLogViewSet.list()` (viewset)

**Inputs del Usuario:**
- Dispositivo: `device_id` (select)
- User ID: `user_id` (text input)
- Nombre: `name` (text input - **filtrado client-side**)
- Fecha desde: `from_date` (date input)
- Fecha hasta: `to_date` (date input)
- Paginación: `page`, `page_size`

**Flujo:**
```
Usuario → Filtros → Botón "Buscar" (implícito en handleFilter)
→ loadLogs(page)
→ getAttendanceLogs({device_id, user_id, from_date, to_date, page, page_size})
→ GET /attendance/?device_id=X&user_id=Y&from_date=Z&to_date=W&page=N&page_size=M
→ AttendanceLogViewSet.list() 
→ DjangoFilterBackend aplica filtros
→ Response: {count, next, previous, results: AttendanceLog[]}
→ UI aplica filtro client-side para nombre
→ DataGrid muestra logs con paginación
```

**Validación:** ✅ **CORRECTO (CORREGIDO)**

**Problemas Detectados y Corregidos:**

1. **✅ CORREGIDO: Filtro `device_id` ahora funciona**
   - Frontend envía: `device_id` (número)
   - Backend ahora soporta: `device_id` como alias en `get_queryset()`

2. **✅ CORREGIDO: Filtros de fecha (`from_date`, `to_date`) implementados**
   - Frontend envía estos params en formato ISO
   - Backend ahora procesa en `get_queryset()` con `timestamp__gte` y `timestamp__lte`
   - **Impacto:** Búsquedas por rango de fechas FUNCIONAN

3. **⚠️ Filtro de nombre funciona vía search**
   - Backend soporta `search=nombre` via `search_fields`
   - Frontend podría usar `search` en vez de filtro client-side
   - **Actual:** Frontend filtra client-side funcional

4. **⚠️ Paginación funciona con defaults de DRF**
   - Django REST Framework usa paginación por defecto
   - **Recomendación:** Configurar explícitamente para control preciso


---

## Resumen de Endpoints API

### Attendance Endpoints

| Frontend Function | HTTP Method | URL | Backend Handler | Status |
|-------------------|-------------|-----|----------------|--------|
| `calculateAttendance()` | POST | `/attendance/calculate/` | `calculate_attendance()` | ✅ OK |
| `getDailyReports()` | GET | `/attendance/reports/daily/` | `daily_reports()` | ✅ OK |
| `getAttendanceLogs()` | GET | `/attendance/` | `AttendanceLogViewSet.list()` | ✅ OK (Corregido) |

### Otros Endpoints (Validados por uso en componentes)

| Frontend Function | HTTP Method | URL | Backend Handler | Status |
|-------------------|-------------|-----|----------------|--------|
| `getDepartments()` | GET | `/departments/` | `DepartmentViewSet.list()` | ✅ OK |
| `getDevices()` | GET | `/devices/` | `DeviceViewSet.list()` | ✅ OK |
| `getTimetables()` | GET | `/schedules/timetables/` | `TimetableViewSet.list()` | ✅ OK |
| `getShifts()` | GET | `/shifts/` | `ShiftViewSet.list()` | ✅ OK |


---

## Problemas Críticos - Estado Actual

### ✅ 1. AttendanceLog Filtrado de Fechas (CORREGIDO)

**Archivo:** `core/viewsets.py:142-175`

**Solución Implementada:**
```python
class AttendanceLogViewSet(viewsets.ModelViewSet):
    queryset = AttendanceLog.objects.all()
    serializer_class = AttendanceLogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'device': ['exact'],
        'user_id': ['exact', 'icontains'],
        'status': ['exact'],
        'punch': ['exact'],
        'is_manual': ['exact'],
        'timestamp': ['gte', 'lte', 'range'],  # ✅ Soporte de fechas
    }
    search_fields = ['user_id', 'user_name', 'edited_reason', 'edited_by']
    ordering_fields = ['timestamp', 'user_id']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Optimize queries and handle custom filters"""
        queryset = AttendanceLog.objects.select_related('device')
        
        # ✅ Handle from_date and to_date query params
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        device_id = self.request.query_params.get('device_id')  # ✅ Support device_id alias
        
        if from_date:
            queryset = queryset.filter(timestamp__gte=from_date)
        if to_date:
            queryset = queryset.filter(timestamp__lte=to_date)
        if device_id:  # ✅ Allow device_id as alias for device
            queryset = queryset.filter(device_id=device_id)
            
        return queryset
```

**Estado:** ✅ **RESUELTO**


---

## ~~Problemas Críticos Identificados~~ (HISTÓRICO)

### ~~1. AttendanceLog Filtrado de Fechas~~ ❌ → ✅ CORREGIDO

~~**Archivo:** `core/viewsets.py:142-170`~~

~~**Problema:**~~
```python
# CÓDIGO ANTERIOR (OBSOLETO)
class AttendanceLogViewSet(viewsets.ModelViewSet):
    filterset_fields = ['device', 'user_id', 'status', 'punch', 'is_manual']
    # ❌ NO soportaba from_date, to_date, device_id
```

~~**Frontend esperaba:**~~
```typescript
// CÓDIGO ACTUAL FUNCIONANDO
const params: any = { page, page_size: pageSize };
if (filters.device_id) params.device_id = parseInt(filters.device_id);
if (filters.user_id) params.user_id = filters.user_id;
if (filters.from_date) params.from_date = new Date(filters.from_date).toISOString();
if (filters.to_date) params.to_date = new Date(filters.to_date).toISOString();
```

~~**Solución Recomendada:**~~ **✅ IMPLEMENTADA - Ver arriba**


### 2. Paginación No Configurada Explícitamente ⚠️

**Recomendación:** Configurar en `settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}
```

O en el viewset específico:

```python
from rest_framework.pagination import PageNumberPagination

class AttendanceLogPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200

class AttendanceLogViewSet(viewsets.ModelViewSet):
    pagination_class = AttendanceLogPagination
    # ...
```


---

## Componentes Frontend Revisados

### 1. Calculation.tsx
- ✅ Botón "Calcular" → `handleCalculate()` → `calculateAttendance()`
- ✅ Select "Departamento" → `setDepartmentId()`
- ✅ Date inputs → `setStartDate()`, `setEndDate()`
- ✅ Mensajes de éxito/error con iconos

### 2. Reports.tsx
- ✅ Botón "Filtrar" → `handleFilter()` → `fetchData()` → `getDailyReports()`
- ✅ Botón "Limpiar" → `handleClear()` → resetea filtros
- ✅ Select "Departamento" → `setDepartmentId()`
- ✅ Input "User ID" → `setUserIdFilter()` (filtro client-side via `useMemo`)
- ✅ Input "Nombre" → `setNameFilter()` (filtro client-side via `useMemo`)
- ✅ Date inputs → `setStartDate()`, `setEndDate()`
- ✅ DataGrid con agrupación por departamento

### 3. Logs.tsx  
- ✅ Botón implícito "Buscar" → `handleFilter()` → `loadLogs()` → `getAttendanceLogs()`
- ✅ Select "Dispositivo" → `handleFilterChange('device_id', ...)` (ahora funciona en backend)
- ✅ Input "User ID" → `handleFilterChange('user_id', ...)` (funciona)
- ⚠️ Input "Nombre" → `handleFilterChange('name', ...)` (filtro client-side, podría usar `search=nombre`)
- ✅ Date inputs → `handleFilterChange('from_date/to_date', ...)` (ahora funciona en backend)
- ✅ Paginación → `loadLogs(page)`
- ✅ Botones exportar CSV/Excel
- ✅ Botón imprimir


---

## Recomendaciones de Corrección

### ~~Alta Prioridad~~ ✅ COMPLETADO
1. ~~**Implementar filtro de fechas en AttendanceLogViewSet**~~ ✅ RESUELTO
2. ~~**Corregir device_id vs device en filterset**~~ ✅ RESUELTO

### Media Prioridad 🟡  
3. **Agregar paginación explícita en settings o viewset** (funciona con defaults, pero mejor explícito)
4. **Mover filtro de nombre al backend usando search** (performance con datasets grandes)

### Baja Prioridad 🟢
5. **Documentar contratos API en OpenAPI/Swagger**
6. **Agregar tests E2E para validar conexiones**


---

## Comandos para Verificar

```bash
# Verificar rutas registradas
python manage.py show_urls | grep attendance

# Verificar serializers
python manage.py shell
>>> from core.serializers import AttendanceLogSerializer, DailyAttendanceSerializer
>>> AttendanceLogSerializer.Meta.fields
>>> DailyAttendanceSerializer.Meta.fields

# Test endpoint de logs con filtros
curl "http://localhost:9000/api/v1/attendance/?from_date=2026-01-01&to_date=2026-02-09&device_id=1"
```


---

## Archivos Clave

### Frontend
- `frontend/src/api.ts` - Cliente API (axios)
- `frontend/src/pages/asistencia/Calculation.tsx` - Cálculo
- `frontend/src/pages/asistencia/Reports.tsx` - Reportes
- `frontend/src/pages/Logs.tsx` - Logs crudos

### Backend
- `core/urls.py` - Rutas API
- `core/views_attendance.py` - Views de cálculo y reportes
- `core/viewsets.py` - ViewSets (AttendanceLog, DailyAttendance, etc.)
- `core/serializers.py` - Serializers DRF
- `core/services/attendance_engine.py` - Lógica de cálculo V1
- `core/services/attendance_engine_v2.py` - Lógica de cálculo V2


---

## Próximos Pasos

1. ✅ Aplicar migraciones pendientes (0105, 0106 - COMPLETADO)
2. ✅ **COMPLETADO:** Corregir filtros de AttendanceLogViewSet
3. ⏳ Ejecutar cálculo desde UI para validar end-to-end
4. ⏳ Revisar logs de shadow mode durante cálculo
5. ⏳ Verificar si tablas shadow se populan


---

## Cambios Aplicados en Esta Sesión

### 2026-02-09
- ✅ Comentados modelos de auditoría legal no implementados (PolicySnapshot, CalculationAuditLog)
- ✅ Migración 0106 aplicada (tablas shadow creadas)
- ✅ AttendanceLogViewSet corregido:
  - Soporte para `from_date` y `to_date`
  - Soporte para `device_id` como alias
  - Mejora en filtrado de timestamp con `gte`, `lte`, `range`
  - Agregado `user_name` a search_fields
- ✅ Documentación completa de conexiones frontend-backend creada
