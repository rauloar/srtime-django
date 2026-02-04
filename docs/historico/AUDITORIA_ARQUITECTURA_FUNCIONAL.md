# 🏗️ AUDITORÍA ARQUITECTURA FUNCIONAL

**Fecha:** 2026-02-02  
**Baseline:** c666fb7 (v0.1-dev-baseline)  
**Propósito:** Mapear estado real de módulos funcionales del sistema

---

## 📋 METODOLOGÍA

Auditoría de código existente clasificando cada componente como:
- ✅ **EXISTE Y SE USA** - Implementado y funcional
- 🟡 **EXISTE PERO NO SE USA** - Código presente pero desconectado
- 🟠 **EXISTE PARCIAL** - Incompleto o en desarrollo
- ❌ **NO EXISTE** - Sin implementación

---

# 1️⃣ MÓDULO: INGRESO DE INFORMACIÓN (CAPTURA)

## 1.1 Subcomponente: Terminales ZKTeco

### Backend

**Modelo Device:**
```python
# core/models.py:123
class Device(models.Model):
    name = models.CharField(max_length=100)
    ip = models.CharField(max_length=50)
    port = models.IntegerField(default=4370)
    password = models.IntegerField(default=0)
    
    # Estado e identidad
    enabled = models.BooleanField(default=True)
    serialnumber = models.CharField(max_length=100, null=True)
    device_name = models.CharField(max_length=100, null=True)
    platform = models.CharField(max_length=50, null=True)
    firmware_version = models.CharField(max_length=100, null=True)
    
    # Estadísticas
    user_count = models.IntegerField(default=0)
    face_count = models.IntegerField(default=0)
    fp_count = models.IntegerField(default=0)
    transaction_count = models.IntegerField(default=0)
    
    last_seen = models.DateTimeField(null=True)
    last_error = models.CharField(max_length=255, null=True)
```
**Estado:** ✅ EXISTE Y SE USA

**Servicio ZKService:**
```python
# core/services/zk.py
class ZKService:
    - connect()
    - disconnect()
    - test_connection()
    - get_users()
    - get_attendance()
    - sync_time()
    - clear_data()
    - set_user()
    - delete_user()
```
**Estado:** ✅ EXISTE Y SE USA

**Endpoints de ingesta:**
```python
# core/views_devices.py
POST /api/v1/devices/{id}/import-attendance/
  - Parámetros: overwrite, start_date
  - Ejecuta: run_import_attendance_job (background)
  - Guarda en: AttendanceLog

POST /api/v1/devices/{id}/sync-users/
  - Parámetros: employee_ids (opcional)
  - Ejecuta: run_sync_users_job (background)
  - Sincroniza: Django → Dispositivo

GET /api/v1/devices/{id}/test-connection-sync/
  - Test rápido síncrono
```
**Estado:** ✅ EXISTE Y SE USA

**Job Management:**
```python
# core/services/jobs.py
- JobManager: create_job(), update_job(), complete_job()
- Background workers: run_in_background()
- Estado persiste en BD
```
**Estado:** ✅ EXISTE Y SE USA

### Frontend

**Pantalla principal:**
```tsx
// frontend/src/pages/DeviceList.tsx
- Grid de dispositivos con filtros
- Estado: ACTIVO/INACTIVO (persistente)
- Estado conexión: CONECTADA/DESCONECTADA (on-demand)
- Botón: "Verificar Conexiones" → checkDevicesConnection()
- Modal de creación de dispositivo
```
**Estado:** ✅ EXISTE Y SE USA

**Detalle de dispositivo:**
```tsx
// frontend/src/pages/DeviceDetail.tsx
- Info del dispositivo (IP, puerto, serial, firmware)
- Estadísticas (usuarios, rostros, huellas, transacciones)
- Acciones:
  - Test Connection
  - Import Attendance
  - Sync Users
  - Clear Data
  - Enable/Disable
  - Delete
- Lista de usuarios en dispositivo
- Lista de logs importados
```
**Estado:** ✅ EXISTE Y SE USA

**API Frontend:**
```typescript
// frontend/src/api.ts
- getDevices()
- createDevice()
- updateDevice()
- deleteDevice()
- testConnectionSync()
- importAttendance()
- syncUsers()
- getDeviceUsers()
- getDeviceLogs()
```
**Estado:** ✅ EXISTE Y SE USA

**Conclusión Ingesta ZKTeco:**
| Componente | Estado |
|-----------|--------|
| Modelo Device | ✅ EXISTE Y SE USA |
| Servicio ZKService | ✅ EXISTE Y SE USA |
| Jobs background | ✅ EXISTE Y SE USA |
| Endpoints ingesta | ✅ EXISTE Y SE USA |
| Frontend devices | ✅ EXISTE Y SE USA |
| Import UI | ✅ EXISTE Y SE USA |

---

## 1.2 Subcomponente: Otros dispositivos biométricos

### Backend
**Estado:** ❌ NO EXISTE
- No hay modelos para otros fabricantes
- No hay adaptadores/drivers
- ZKTeco es el único soportado

### Frontend
**Estado:** ❌ NO EXISTE
- No hay pantallas para configurar otros dispositivos

---

## 1.3 Subcomponente: Archivos externos (TXT, CSV, LOG)

### Backend

**Modelo ImportBatch:**
```python
# core/models.py:195
class ImportBatch(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    imported_at = models.DateTimeField(auto_now_add=True)
    count = models.IntegerField(default=0)
```
**Estado:** ✅ EXISTE Y SE USA
- Trackea lotes de importación
- Relacionado con Device (no archivos externos genéricos)

**Parsers/Processors:**
**Estado:** ❌ NO EXISTE
- No hay parsers para TXT/CSV/LOG externos
- No hay endpoints para subir archivos
- No hay procesadores de formatos genéricos

### Frontend
**Estado:** ❌ NO EXISTE
- No hay pantalla de "Upload File"
- No hay drag & drop de archivos
- Import solo desde dispositivos ZKTeco

---

## 1.4 Subcomponente: Cargas manuales

### Backend
**Estado:** ❌ NO EXISTE
- No hay endpoint para crear AttendanceLog manual
- No hay formulario de carga individual de evento

### Frontend
**Estado:** ❌ NO EXISTE
- No hay pantalla de "Registrar evento manual"
- Solo lectura de logs importados

---

## 1.5 Modelo de datos crudos: AttendanceLog

```python
# core/models.py:161
class AttendanceLog(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=50, db_index=True)
    timestamp = models.DateTimeField(db_index=True)
    status = models.IntegerField()
    punch = models.IntegerField()
    
    # Detalles extendidos
    verify_mode = models.IntegerField(null=True)
    workstate = models.IntegerField(null=True)
    workcode = models.IntegerField(null=True)
    punch_source = models.CharField(max_length=50, null=True)
    raw_json = models.JSONField(null=True)
    
    # Constraints
    UniqueConstraint(['device', 'user_id', 'timestamp'])
    
    # Indexes
    Index(['user_id', 'timestamp'])
    Index(['timestamp'])
    Index(['device', 'timestamp'])
```
**Estado:** ✅ EXISTE Y SE USA
- Almacena eventos crudos de dispositivos
- Metadata completa del evento
- Indexado para consultas rápidas

---

# 2️⃣ MÓDULO: CONFIGURACIÓN DEL SISTEMA (RRHH / ADMIN)

## 2.1 Entidad: Empresa / Organización

### Backend

**Modelo Company:**
```python
# core/models.py
class Company(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=200, null=True)
    website = models.CharField(max_length=100, null=True)
    logo_path = models.CharField(max_length=255, null=True)
```
**Estado:** ✅ EXISTE Y SE USA

**Endpoints:**
```python
# core/viewsets.py
CompanyViewSet (GET, POST, PUT, DELETE)
```
**Estado:** ✅ EXISTE Y SE USA

### Frontend

**Pantalla:**
```tsx
// frontend/src/pages/organization/Company.tsx
- CRUD completo de empresas
- Formulario: name, code, address, website
```
**Estado:** ✅ EXISTE Y SE USA

---

## 2.2 Entidad: Departamentos

### Backend

**Modelo Department:**
```python
# core/models.py
class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, null=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)  # Árbol
```
**Estado:** ✅ EXISTE Y SE USA
- Soporte de jerarquías (self-referencing FK)

**Endpoints:**
```python
DepartmentViewSet (GET, POST, PUT, DELETE)
```
**Estado:** ✅ EXISTE Y SE USA

### Frontend

**Pantalla:**
```tsx
// frontend/src/pages/personnel/Departments.tsx
- Vista de árbol jerárquico
- CRUD completo
- Asignación a company
```
**Estado:** ✅ EXISTE Y SE USA

---

## 2.3 Entidad: Posiciones

### Backend

**Modelo Position:**
```python
# core/models.py
class Position(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=255, null=True)
```
**Estado:** ✅ EXISTE Y SE USA

**Endpoints:**
```python
PositionViewSet (GET, POST, PUT, DELETE)
```
**Estado:** ✅ EXISTE Y SE USA

### Frontend

**Pantalla:**
```tsx
// frontend/src/pages/organization/Positions.tsx
- Grid con CRUD
- Formulario simple
```
**Estado:** ✅ EXISTE Y SE USA

---

## 2.4 Entidad: Zonas

### Backend

**Modelo Zone:**
```python
# core/models.py
class Zone(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=255, null=True)
```
**Estado:** ✅ EXISTE Y SE USA

**Endpoints:**
```python
ZoneViewSet (GET, POST, PUT, DELETE)
```
**Estado:** ✅ EXISTE Y SE USA

### Frontend

**Pantalla:**
```tsx
// frontend/src/pages/organization/Zones.tsx
- Grid con CRUD
```
**Estado:** ✅ EXISTE Y SE USA

---

## 2.5 Entidad: Empleados

### Backend

**Modelo Employee:**
```python
# core/models.py
class Employee(models.Model):
    user_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=100, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True)
    
    # Contacto
    email = models.EmailField(max_length=100, null=True)
    phone = models.CharField(max_length=50, null=True)
    mobile_phone = models.CharField(max_length=50, null=True)
    
    # Datos laborales
    hire_date = models.DateField(null=True)
    
    # Dirección
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100, null=True)
    
    # Foto
    photo_path = models.CharField(max_length=255, null=True)
```
**Estado:** ✅ EXISTE Y SE USA

**Endpoints:**
```python
EmployeeViewSet (GET, POST, PUT, DELETE)
  - Filtros: department, search
  - Paginación
```
**Estado:** ✅ EXISTE Y SE USA

### Frontend

**Pantalla:**
```tsx
// frontend/src/pages/personnel/Employees.tsx
- DataGrid con filtros
- CRUD completo
- Export to Excel
- Formulario completo con todos los campos
```
**Estado:** ✅ EXISTE Y SE USA

---

## 2.6 Entidad: Turnos y Horarios

### Backend

**Modelo Timetable (Horario):**
```python
# core/models.py:343
class Timetable(models.Model):
    name = models.CharField(max_length=100)
    
    # Horario fijo
    on_duty_time = models.CharField(max_length=10)      # "09:00"
    off_duty_time = models.CharField(max_length=10)     # "18:00"
    
    # Tolerancias
    late_allow_minutes = models.IntegerField(default=0)
    early_leave_allow_minutes = models.IntegerField(default=0)
    
    # Ventanas (flex)
    check_in_start = models.CharField(max_length=10, null=True)
    check_in_end = models.CharField(max_length=10, null=True)
    check_out_start = models.CharField(max_length=10, null=True)
    check_out_end = models.CharField(max_length=10, null=True)
    
    # Config
    break_minutes = models.IntegerField(default=0)
    required_minutes = models.IntegerField(default=0)
    rounding_rule = models.CharField(max_length=50, choices=ROUNDING_CHOICES)
    
    # 🔑 Selector fijo vs flexible
    is_flexible = models.BooleanField(default=False)
```
**Estado:** ✅ EXISTE Y SE USA

**Modelo Shift (Turno):**
```python
# core/models.py:379
class Shift(models.Model):
    name = models.CharField(max_length=100)
```
**Estado:** ✅ EXISTE Y SE USA

**Modelo ShiftTimetable (Relación Turno-Horario):**
```python
# core/models.py:393
class ShiftTimetable(models.Model):
    shift = models.ForeignKey(Shift)
    timetable = models.ForeignKey(Timetable)
    day_index = models.IntegerField()  # 0=Lunes, 6=Domingo
```
**Estado:** ✅ EXISTE Y SE USA

**Modelo EmployeeShift (Asignación):**
```python
# core/models.py:433
class EmployeeShift(models.Model):
    scope = models.CharField(choices=['EMPLOYEE', 'DEPARTMENT'])
    employee = models.ForeignKey(Employee, null=True)
    department = models.ForeignKey(Department, null=True)
    shift = models.ForeignKey(Shift)
    start_date = models.DateField()
    end_date = models.DateField(null=True)
```
**Estado:** ✅ EXISTE Y SE USA

**Endpoints:**
```python
# core/viewsets.py
TimetableViewSet (GET, POST, PUT, DELETE)
ShiftViewSet (GET, POST, DELETE)
EmployeeShiftViewSet (GET, POST, PUT, DELETE)

# core/views.py
POST /shifts/{id}/configure-cycle/
GET /shifts/{id}/cycle/
```
**Estado:** ✅ EXISTE Y SE USA

### Frontend

**Pantallas:**
```tsx
// frontend/src/pages/asistencia/Timetables.tsx
- Grid de horarios
- CRUD completo con formulario avanzado
- Campos: on_duty, off_duty, tolerancias, flex, breaks

// frontend/src/pages/asistencia/Shifts.tsx
- Grid de turnos
- Configuración de ciclo (7 días)
- Asignación de horarios por día de semana

// frontend/src/pages/asistencia/EmployeeSchedule.tsx
- Asignación de turnos a empleados/departamentos
- Rango de fechas (start_date, end_date)
```
**Estado:** ✅ EXISTE Y SE USA

---

## 2.7 Tipos de jornada (fija / flexible)

### Backend

**Campo en Timetable:**
```python
is_flexible = models.BooleanField(default=False)
```
**Estado:** ✅ EXISTE Y SE USA (en modelo)

**Lógica de distinción:**
```python
# core/services/attendance_engine.py:_build_context()
if tt.is_flexible:
    # Lógica flexible (rango amplio)
else:
    # Lógica fija (horario + tolerancias)
```
**Estado:** 🟡 EXISTE PERO NO SE USA
- Código existe pero no se llama desde views actuales
- `get_simple_day_view()` no consulta `is_flexible`

### Frontend

**Formulario Timetable:**
```tsx
<Checkbox label="Es Flexible" checked={is_flexible} onChange={...} />
```
**Estado:** ✅ EXISTE Y SE USA (en UI)
- Campo se captura y guarda
- Pero backend actual no lo usa en cálculos

---

## 2.8 Tiempo máximo de trabajo

### Backend
**Estado:** ❌ NO EXISTE
- No hay campo `max_work_hours` en Timetable
- No hay campo `max_work_hours_per_day`
- No hay validaciones de límites

### Frontend
**Estado:** ❌ NO EXISTE
- No hay configuración de límites

---

## 2.9 Ausencias / Presencias / Vacaciones

### Backend

**Modelo Leave (Ausencias/Licencias):**
```python
# core/models.py:456
class Leave(models.Model):
    TYPE_CHOICES = [
        ('SICK', 'Enfermedad'),
        ('VACATION', 'Vacaciones'),
        ('PERSONAL', 'Personal'),
        ('OTHER', 'Otro'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=255, null=True)
    approved = models.BooleanField(default=False)
    approved_by = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```
**Estado:** ✅ EXISTE Y SE USA

**Endpoints:**
```python
LeaveViewSet (GET, POST, PUT, DELETE)
  - Filtros: employee, start_date, end_date, leave_type, approved
```
**Estado:** ✅ EXISTE Y SE USA

### Frontend

**Pantalla:**
```tsx
// frontend/src/pages/asistencia/Absences.tsx
- Grid de ausencias
- CRUD completo
- Filtros: empleado, tipo, rango, aprobado
- Formulario con:
  - Tipo (SICK, VACATION, PERSONAL, OTHER)
  - Rango de fechas
  - Razón
  - Aprobación
```
**Estado:** ✅ EXISTE Y SE USA

---

## 2.10 Feriados

### Backend

**Modelo Holiday:**
```python
# core/models.py:481
class Holiday(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    is_recurring = models.BooleanField(default=False)
```
**Estado:** ✅ EXISTE Y SE USA

**Endpoints:**
```python
HolidayViewSet (GET, POST, PUT, DELETE)
```
**Estado:** ✅ EXISTE Y SE USA

### Frontend
**Estado:** 🟠 EXISTE PARCIAL
- No hay pantalla dedicada de "Feriados"
- Se puede gestionar via API directa
- Sin CRUD en UI

---

## 2.11 Sobrescritura de horarios (Excepciones)

### Backend

**Modelo ScheduleOverride:**
```python
# core/models.py:411
class ScheduleOverride(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    UniqueConstraint(['employee', 'date'])
```
**Estado:** ✅ EXISTE Y SE USA

**Endpoints:**
```python
ScheduleOverrideViewSet (GET, POST, PUT, DELETE)
```
**Estado:** ✅ EXISTE Y SE USA

### Frontend
**Estado:** 🟠 EXISTE PARCIAL
- No hay pantalla dedicada de "Excepciones"
- Se puede gestionar via API directa
- Sin CRUD en UI

---

# 3️⃣ MÓDULO: VISUALIZACIÓN Y EXPLOTACIÓN DE INFORMACIÓN

## 3.1 Dashboard

### Backend

**Endpoint:**
```python
GET /api/v1/
  - Info básica de API
  - Links de documentación
  - Estado del sistema
```
**Estado:** 🟠 EXISTE PARCIAL
- No hay endpoint de "Dashboard metrics"
- No hay agregaciones precalculadas
- No hay KPIs

### Frontend

**Pantalla:**
```tsx
// frontend/src/pages/Dashboard.tsx
- TodaySummary: empleados presentes, ausentes, tardíos
- AttentionList: empleados que requieren atención
- Navegación a vista diaria
```
**Estado:** ✅ EXISTE Y SE USA

**Componentes:**
```tsx
// frontend/src/components/dashboard/TodaySummary.tsx
- Obtiene /attendance/reports/daily/?from_date=HOY&to_date=HOY
- Agrega en frontend:
  - Presentes: status != "Absent"
  - Ausentes: status == "Absent"
  - Tardíos: late_minutes > 0

// frontend/src/components/dashboard/AttentionList.tsx
- Filtra empleados con anomalías
- Muestra warning si late_minutes > tolerancia
```
**Estado:** ✅ EXISTE Y SE USA
- Lógica de agregación en frontend (no backend)

---

## 3.2 Vista diaria de asistencia

### Backend

**Endpoint principal:**
```python
# core/views_attendance.py:133
GET /api/v1/attendance/day/?employee_id=1&date=2026-02-02

Retorna:
{
  "employee_id": "1",
  "employee_name": "Juan",
  "date": "2026-02-02",
  "status": "Normal",  # Absent/Partial/Normal
  "worked_minutes": 480,
  "logs": [
    { "type": "IN", "time": "08:30" },
    { "type": "OUT", "time": "17:30" }
  ]
}

Cálculo actual:
- IN/OUT: alternancia por índice (0=IN, 1=OUT, 2=IN...)
- worked_minutes: diferencia entre primer y último log
- status: según cantidad de logs (0=Absent, 1=Partial, 2+=Normal)
```
**Estado:** ✅ EXISTE Y SE USA
- Lógica NAIVE (sin horarios ni política)

### Frontend

**Pantalla:**
```tsx
// frontend/src/pages/asistencia/DayViewPage.tsx
- Parámetros: employeeId, date
- Llama a /attendance/day/
- Renderea:
  - DayHeader: info del empleado, fecha, status
  - DayNavigation: prev/next day
  - DayTimeline: bloques de tiempo (vacío hoy)
  - DayExplanation: análisis (vacío hoy)
  - DayPunchList: lista de marcaciones IN/OUT
  - DayActions: acciones disponibles
```
**Estado:** ✅ EXISTE Y SE USA

---

## 3.3 Timeline

### Backend

**Endpoint:**
```python
# core/views_stubs.py:7
GET /api/v1/attendance/{employee_id}/timeline/{date}/

Retorna:
{
  "blocks": []
}
```
**Estado:** 🔴 STUB (mock vacío)

### Frontend

**Componente:**
```tsx
// frontend/src/components/asistencia/DayTimeline.tsx
- Llama a getTimeline(employeeId, date)
- Espera estructura:
  interface TimelineBlock {
    type: string;  // "WORK", "BREAK", "GAP_ANOMALY"
    start_time: string;
    end_time: string;
    duration_minutes: number;
  }
- Renderea bloques con colores por tipo
- Hoy recibe [], muestra "sin datos"
```
**Estado:** ✅ EXISTE Y SE USA (UI preparada)
- Backend retorna stub

---

## 3.4 Explanation

### Backend

**Endpoint:**
```python
# core/views_stubs.py:16
GET /api/v1/attendance/{employee_id}/explanation/{date}/

Retorna:
{
  "summary": "Data not available in DEV mode",
  "anomalies": [],
  "recommendations": []
}
```
**Estado:** 🔴 STUB (mock genérico)

### Frontend

**Componente:**
```tsx
// frontend/src/components/asistencia/DayExplanation.tsx
- Llama a getExplanation(employeeId, date)
- Espera estructura:
  interface ExplanationData {
    summary: string;
    anomalies: string[];
    recommendations: string[];
  }
- Renderea secciones con iconos
- Hoy recibe mock, se oculta silenciosamente
```
**Estado:** ✅ EXISTE Y SE USA (UI preparada)
- Backend retorna stub

---

## 3.5 Reportes

### Backend

**Endpoint:**
```python
# core/views_attendance.py:49
GET /api/v1/attendance/reports/daily/
  ?from_date=2026-01-01
  &to_date=2026-01-07
  &employee_id=1
  &department_id=1

Retorna:
[
  {
    "id": 123,
    "employee": {...},
    "date": "2026-01-01",
    "check_in": "2026-01-01T08:30:00Z",
    "check_out": "2026-01-01T17:30:00Z",
    "status": "Normal",
    "late_minutes": 0,
    "early_minutes": 0,
    "worked_minutes": 480,
    "overtime_minutes": 0,
    ...
  },
  ...
]

Fuente: DailyAttendance (precalculado)
```
**Estado:** ✅ EXISTE Y SE USA

**Modelo DailyAttendance:**
```python
# core/models.py:497
class DailyAttendance(models.Model):
    employee = models.ForeignKey(Employee)
    date = models.DateField()
    timetable = models.ForeignKey(Timetable, null=True)
    
    # Timestamps
    check_in = models.DateTimeField(null=True)
    check_out = models.DateTimeField(null=True)
    
    # Schedule context
    on_duty = models.CharField(max_length=10, null=True)
    off_duty = models.CharField(max_length=10, null=True)
    
    # Métricas
    late_minutes = models.IntegerField(default=0)
    early_minutes = models.IntegerField(default=0)
    worked_minutes = models.IntegerField(default=0)
    overtime_minutes = models.IntegerField(default=0)
    break_minutes = models.IntegerField(default=0)
    net_worked_minutes = models.IntegerField(default=0)
    regular_minutes = models.IntegerField(default=0)
    night_minutes = models.IntegerField(default=0)
    
    # Status
    status = models.CharField(choices=STATUS_CHOICES, default='Absent')
    exception_reason = models.CharField(max_length=100, null=True)
    is_absent = models.BooleanField(default=True)
```
**Estado:** ✅ EXISTE Y SE USA
- Modelo completo para almacenar cálculos

**Cálculo de DailyAttendance:**
```python
# core/views_attendance.py:14
POST /api/v1/attendance/calculate/
  Body: {
    "start_date": "2025-01-01",
    "end_date": "2025-01-07",
    "department_id": 1  // Opcional
  }

Ejecuta: calculate_period() → crea/actualiza DailyAttendance
```
**Estado:** ✅ EXISTE Y SE USA

### Frontend

**Pantalla:**
```tsx
// frontend/src/pages/asistencia/Reports.tsx
- Filtros: rango de fechas, empleado, departamento
- Llama a /attendance/reports/daily/
- DataGrid con columnas:
  - Empleado
  - Fecha
  - Check In
  - Check Out
  - Status
  - Horas trabajadas
  - Tarde
  - Salida temprana
  - Overtime
- Export to Excel
```
**Estado:** ✅ EXISTE Y SE USA

**Pantalla Calculation:**
```tsx
// frontend/src/pages/asistencia/Calculation.tsx
- Formulario:
  - Rango de fechas
  - Departamento (opcional)
- Botón "Calcular"
- Llama a POST /attendance/calculate/
- Muestra resultado: "Calculados X registros"
```
**Estado:** ✅ EXISTE Y SE USA

---

## 3.6 Exportación

### Backend
**Estado:** ❌ NO EXISTE
- No hay endpoints de export a PDF
- No hay generadores de reportes
- No hay templates de impresión

### Frontend

**Export Excel:**
```tsx
// frontend/src/pages/personnel/Employees.tsx
- Botón "Exportar"
- Usa librería xlsx
- Genera archivo Excel con empleados

// frontend/src/pages/asistencia/Reports.tsx
- Botón "Exportar"
- Genera Excel con reportes de asistencia
```
**Estado:** ✅ EXISTE Y SE USA (solo Excel, client-side)

**Export PDF:**
**Estado:** ❌ NO EXISTE

---

# 📊 MAPA FUNCIONAL DEL SISTEMA

## ✅ MÓDULOS COMPLETOS Y FUNCIONALES

### 1. INGRESO - ZKTeco
- ✅ Modelo Device
- ✅ Servicio ZKService (pyzk wrapper)
- ✅ Endpoints de importación
- ✅ Jobs background
- ✅ UI completa (DeviceList, DeviceDetail)
- ✅ Import attendance
- ✅ Sync users
- ✅ Test connection

**Conclusión:** Módulo completamente funcional

---

### 2. CONFIGURACIÓN - Estructura Organizacional
- ✅ Company (CRUD completo)
- ✅ Department (CRUD completo, jerárquico)
- ✅ Position (CRUD completo)
- ✅ Zone (CRUD completo)
- ✅ Employee (CRUD completo)

**Conclusión:** Módulo completamente funcional

---

### 3. CONFIGURACIÓN - Turnos y Horarios
- ✅ Timetable (CRUD completo, fijo/flex)
- ✅ Shift (CRUD completo)
- ✅ ShiftTimetable (configuración de ciclo)
- ✅ EmployeeShift (asignaciones)
- ✅ ScheduleOverride (excepciones)

**Conclusión:** Módulo completamente funcional

---

### 4. CONFIGURACIÓN - Ausencias
- ✅ Leave (CRUD completo)
- ✅ UI de Absences
- ✅ Filtros y aprobación

**Conclusión:** Módulo completamente funcional

---

### 5. VISUALIZACIÓN - Dashboard
- ✅ Dashboard UI
- ✅ Agregaciones en frontend
- ✅ Resumen diario
- ✅ Lista de atención

**Conclusión:** Funcional pero sin backend de KPIs

---

### 6. VISUALIZACIÓN - Vista Diaria
- ✅ Endpoint /attendance/day/
- ✅ DayViewPage UI completa
- ✅ Lista de marcaciones

**Conclusión:** Funcional con lógica NAIVE

---

### 7. VISUALIZACIÓN - Reportes
- ✅ DailyAttendance (modelo)
- ✅ Endpoint /attendance/reports/daily/
- ✅ Calculation endpoint
- ✅ Reports UI
- ✅ Export Excel (client-side)

**Conclusión:** Módulo completamente funcional

---

## 🟡 MÓDULOS PARCIALES (EXISTEN PERO NO COMPLETOS)

### 1. INGRESO - AttendanceLog metadata
- ✅ Campos: punch, workstate, workcode, punch_source
- 🟡 NO SE USAN en cálculos
- 🟡 Raw JSON nunca procesado

**Conclusión:** Captura completa, procesamiento inexistente

---

### 2. CONFIGURACIÓN - Tipo de jornada (fijo/flexible)
- ✅ Campo is_flexible existe en Timetable
- ✅ UI captura el valor
- 🟡 Backend NO lo usa en cálculos
- 🟡 Lógica de distinción existe pero DORMIDA

**Conclusión:** Estructura lista, lógica desconectada

---

### 3. CONFIGURACIÓN - Feriados
- ✅ Modelo Holiday
- ✅ Endpoints
- 🟡 NO hay UI dedicada

**Conclusión:** Backend listo, falta frontend

---

### 4. VISUALIZACIÓN - Timeline
- ✅ UI preparada (DayTimeline)
- ✅ Endpoint registrado
- 🔴 Backend retorna stub vacío

**Conclusión:** Frontend listo, backend mock

---

### 5. VISUALIZACIÓN - Explanation
- ✅ UI preparada (DayExplanation)
- ✅ Endpoint registrado
- 🔴 Backend retorna stub genérico

**Conclusión:** Frontend listo, backend mock

---

## ❌ MÓDULOS INEXISTENTES

### 1. INGRESO - Otros dispositivos biométricos
- ❌ Sin soporte de otros fabricantes
- ❌ Sin adaptadores genéricos

---

### 2. INGRESO - Archivos externos (TXT/CSV/LOG)
- ❌ Sin parsers
- ❌ Sin endpoints de upload
- ❌ Sin UI de importación

---

### 3. INGRESO - Cargas manuales
- ❌ Sin formulario de carga manual
- ❌ Sin endpoint de creación directa

---

### 4. CONFIGURACIÓN - Límites de tiempo máximo
- ❌ Sin campo max_work_hours
- ❌ Sin validaciones de límites

---

### 5. VISUALIZACIÓN - Export PDF
- ❌ Sin generadores de PDF
- ❌ Sin templates de impresión

---

### 6. VISUALIZACIÓN - Backend de Dashboard KPIs
- ❌ Sin endpoint de métricas
- ❌ Agregaciones solo en frontend

---

# 🎯 RESUMEN EJECUTIVO

## ESTADO POR MÓDULO

| Módulo | Subcomponente | Estado |
|--------|---------------|--------|
| **1. INGRESO** | ZKTeco | ✅ COMPLETO |
| | Otros dispositivos | ❌ NO EXISTE |
| | Archivos externos | ❌ NO EXISTE |
| | Carga manual | ❌ NO EXISTE |
| | AttendanceLog | ✅ COMPLETO |
| | Metadata punch | 🟡 CAPTURA OK, PROCESO NO |
| **2. CONFIGURACIÓN** | Company | ✅ COMPLETO |
| | Department | ✅ COMPLETO |
| | Position | ✅ COMPLETO |
| | Zone | ✅ COMPLETO |
| | Employee | ✅ COMPLETO |
| | Timetable | ✅ COMPLETO |
| | Shift | ✅ COMPLETO |
| | EmployeeShift | ✅ COMPLETO |
| | Tipo jornada | 🟡 MODELO OK, LÓGICA DORMIDA |
| | Leave/Absences | ✅ COMPLETO |
| | Holiday | 🟡 BACKEND OK, SIN UI |
| | ScheduleOverride | 🟡 BACKEND OK, SIN UI |
| | Límites tiempo | ❌ NO EXISTE |
| **3. VISUALIZACIÓN** | Dashboard | 🟡 UI OK, SIN BACKEND KPIs |
| | Day View | ✅ COMPLETO (NAIVE) |
| | Timeline | 🟡 UI OK, BACKEND STUB |
| | Explanation | 🟡 UI OK, BACKEND STUB |
| | Reports | ✅ COMPLETO |
| | Calculation | ✅ COMPLETO |
| | Export Excel | ✅ COMPLETO (client) |
| | Export PDF | ❌ NO EXISTE |

---

## COBERTURA FUNCIONAL

**COMPLETO Y FUNCIONAL (24 componentes):**
- Ingesta ZKTeco: Device, ZKService, Jobs, UI
- Organización: Company, Department, Position, Zone, Employee
- Horarios: Timetable, Shift, ShiftTimetable, EmployeeShift
- Ausencias: Leave
- Visualización: Dashboard UI, Day View, Reports, Calculation
- Export: Excel (client-side)

**PARCIAL (8 componentes):**
- AttendanceLog metadata (captura sin uso)
- Tipo jornada (modelo sin conectar)
- Holiday (backend sin UI)
- ScheduleOverride (backend sin UI)
- Timeline (UI sin backend)
- Explanation (UI sin backend)
- Dashboard KPIs (frontend sin backend)

**NO EXISTE (7 componentes):**
- Otros dispositivos biométricos
- Archivos externos
- Carga manual
- Límites de tiempo
- Export PDF
- Generadores de reportes
- Templates de impresión

---

## FORTALEZAS

1. **Ingesta robusta:** ZKTeco completamente implementado
2. **Configuración sólida:** RRHH completo y funcional
3. **Reportería operativa:** DailyAttendance + filtros + export
4. **UI preparada:** Frontend anticipa funcionalidad futura

---

## DEBILIDADES

1. **Lógica desconectada:** Flexible engine dormido
2. **Metadata ignorada:** Campos punch/workstate sin uso
3. **Stubs en producción:** Timeline/Explanation no implementados
4. **Cálculos naive:** Sin aplicar política de horarios

---

## OPORTUNIDADES

1. **Conectar lógica existente:** flexible_engine.py está listo
2. **Activar metadata:** punch/workstate ya capturados
3. **Implementar stubs:** UI ya preparada

---

**Fin del documento.**
