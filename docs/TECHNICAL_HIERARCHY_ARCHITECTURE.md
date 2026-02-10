# 📊 REPORTE TÉCNICO: Lógica de Jerarquía Organizacional
## Sistema de Gestión de Recursos Humanos - SRTimeWeb

---

## 📋 1. RESUMEN EJECUTIVO

El sistema implementa una jerarquía organizacional de **5 niveles** que permite gestionar la estructura empresarial y calcular automáticamente la asistencia del personal:

```
🏢 EMPRESA
   └─ 🏛️ DEPARTAMENTO
       └─ 🔄 TURNO (Shift)
           └─ ⏰ HORARIO (Timetable)
               └─ 👤 PERSONAL (Employee)
```

**Características Clave:**
- ✅ **Resolución Jerárquica Automática**: El sistema resuelve el horario aplicable por prioridad
- ✅ **Asignaciones Flexibles**: Soporte para asignación individual o por departamento
- ✅ **Excepciones Manuales**: Posibilidad de sobrescribir horarios específicos
- ✅ **Ciclos Flexibles**: Semanal (Lun-Dom) o ciclos largos (rotaciones de N días)

---

## 🗄️ 2. ARQUITECTURA DE DATOS

### 2.1 Modelos y Tablas

| Entidad | Tabla | Propósito | Relaciones |
|---------|-------|-----------|------------|
| **Company** | `companies` | Datos generales de la empresa | → Departments (1:N) |
| **Department** | `departments` | Áreas organizacionales | → Company (N:1)<br>→ Employees (1:N)<br>→ EmployeeShift (1:N) |
| **Shift** | `att_shifts` | Patrón de trabajo (turno) | → ShiftTimetable (1:N)<br>→ EmployeeShift (1:N) |
| **Timetable** | `att_timetables` | Franja horaria específica | → ShiftTimetable (1:N)<br>→ ScheduleOverride (1:N) |
| **ShiftTimetable** | `att_shift_timetables` | Relaciona Turno con Horario por día | → Shift (N:1)<br>→ Timetable (N:1) |
| **Employee** | `employees` | Personal | → Department (N:1)<br>→ EmployeeShift (1:N) |
| **EmployeeShift** | `att_employee_shifts` | Asignación turno → empleado/depto | → Employee (N:1)<br>→ Department (N:1)<br>→ Shift (N:1) |
| **ScheduleOverride** | `att_schedule_overrides` | Excepción manual de horario | → Employee (N:1)<br>→ Timetable (N:1) |

---

## 🔗 3. JERARQUÍA ORGANIZACIONAL

### 3.1 Nivel 1: Empresa (Company)

```python
class Company(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=200, null=True)
    website = models.CharField(max_length=100, null=True)
```

**Propósito:** Entidad raíz que agrupa toda la estructura organizacional.

**Relaciones:**
- **1:N** con Department (una empresa tiene múltiples departamentos)

**Ejemplo:**
```json
{
  "id": 1,
  "name": "Acme Corporation",
  "code": "ACM",
  "address": "123 Main St"
}
```

---

### 3.2 Nivel 2: Departamento (Department)

```python
class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, null=True)
    company = models.ForeignKey(Company, on_delete=SET_NULL, null=True)
    parent = models.ForeignKey('self', on_delete=SET_NULL, null=True)  # Jerarquía interna
```

**Propósito:** Divide la empresa en áreas funcionales. Soporta jerarquía anidada (departamento padre/hijo).

**Relaciones:**
- **N:1** con Company
- **1:N** con Employee (múltiples empleados)
- **1:N** con EmployeeShift (asignaciones a nivel departamento)

**Ejemplo:**
```json
{
  "id": 10,
  "name": "Producción",
  "code": "PROD",
  "company_id": 1,
  "parent_id": null
}
```

---

### 3.3 Nivel 3: Turno (Shift)

```python
class Shift(models.Model):
    name = models.CharField(max_length=100)
    cycle_days = models.IntegerField(default=0)
    # 0 = ciclo semanal (Lun-Dom)
    # >0 = ciclo largo (ejemplo: 28 días rotación minera)
```

**Propósito:** Define un patrón de trabajo abstracto (ejemplo: "Turno Mañana", "Turno Noche").

**Características:**
- **Ciclo Semanal** (`cycle_days=0`): Patrón fijo Lunes-Domingo
- **Ciclo Largo** (`cycle_days>0`): Rotaciones de N días (ejemplo: 7 días trabajo, 7 días descanso)

**Relaciones:**
- **1:N** con ShiftTimetable (múltiples horarios por día de la semana)
- **1:N** con EmployeeShift (múltiples asignaciones)

**Ejemplo:**
```json
{
  "id": 5,
  "name": "Turno Administrativo",
  "cycle_days": 0
}
```

---

### 3.4 Nivel 4: Horario (Timetable)

```python
class Timetable(models.Model):
    name = models.CharField(max_length=100)
    on_duty_time = models.TimeField()  # Hora entrada
    off_duty_time = models.TimeField()  # Hora salida
    late_allow_minutes = models.IntegerField(default=0)  # Tolerancia tardanza
    early_leave_allow_minutes = models.IntegerField(default=0)  # Tolerancia salida temprana
    check_in_start = models.TimeField(null=True)  # Ventana marcación entrada
    check_in_end = models.TimeField(null=True)
    check_out_start = models.TimeField(null=True)  # Ventana marcación salida
    check_out_end = models.TimeField(null=True)
    break_minutes = models.IntegerField(default=0)
    required_minutes = models.IntegerField(default=0)
    is_flexible = models.BooleanField(default=False)  # Horario flexible
    overtime_threshold_minutes = models.IntegerField(default=0)
```

**Propósito:** Franja horaria concreta con reglas de negocio (tolerancias, descansos, horas extra).

**Tipos:**
1. **Horario Fijo** (`is_flexible=False`): Entrada/Salida definidas
2. **Horario Flexible** (`is_flexible=True`): Solo cuenta horas trabajadas totales

**Relaciones:**
- **1:N** con ShiftTimetable (puede ser usado por múltiples turnos)
- **1:N** con ScheduleOverride (excepciones manuales)

**Ejemplo:**
```json
{
  "id": 3,
  "name": "08:00-17:00 (Administrativo)",
  "on_duty_time": "08:00:00",
  "off_duty_time": "17:00:00",
  "late_allow_minutes": 15,
  "early_leave_allow_minutes": 5,
  "break_minutes": 60,
  "is_flexible": false
}
```

---

### 3.5 Relación Turno-Horario (ShiftTimetable)

```python
class ShiftTimetable(models.Model):
    shift = models.ForeignKey(Shift, on_delete=CASCADE)
    timetable = models.ForeignKey(Timetable, on_delete=CASCADE)
    day_index = models.IntegerField()  # 0=Lunes, 6=Domingo (o día del ciclo)
```

**Propósito:** Conecta un turno con horarios específicos por día de la semana/ciclo.

**Lógica:**
- **Ciclo Semanal**: `day_index` = 0-6 (Lun-Dom)
- **Ciclo Largo**: `day_index` = 0 hasta `(cycle_days-1)`

**Ejemplo:** Turno Administrativo (5 días)
```json
[
  {"shift_id": 5, "day_index": 0, "timetable_id": 3},  // Lunes: 08:00-17:00
  {"shift_id": 5, "day_index": 1, "timetable_id": 3},  // Martes: 08:00-17:00
  {"shift_id": 5, "day_index": 2, "timetable_id": 3},  // Miércoles: 08:00-17:00
  {"shift_id": 5, "day_index": 3, "timetable_id": 3},  // Jueves: 08:00-17:00
  {"shift_id": 5, "day_index": 4, "timetable_id": 3},  // Viernes: 08:00-17:00
  // Sábado/Domingo: No hay registros = día de descanso
]
```

---

### 3.6 Nivel 5: Personal (Employee)

```python
class Employee(models.Model):
    user_id = models.CharField(max_length=50, unique=True)  # ID único
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=SET_NULL, null=True)
    position = models.ForeignKey(Position, on_delete=SET_NULL, null=True)
    active = models.BooleanField(default=True)
    hire_date = models.DateField(null=True)
    # ... otros campos (email, phone, etc.)
```

**Propósito:** Representa cada miembro del personal.

**Relaciones:**
- **N:1** con Department
- **1:N** con EmployeeShift (puede tener múltiples asignaciones temporales)
- **1:N** con AttendanceLog (marcaciones biométricas)
- **1:N** con DailyAttendance (registros diarios calculados)

**Ejemplo:**
```json
{
  "id": 289,
  "user_id": "EMP003",
  "name": "Empleado 03",
  "department_id": 10,
  "active": true
}
```

---

## ⚙️ 4. LÓGICA DE RESOLUCIÓN DE HORARIOS

### 4.1 Sistema de Prioridades (Cascada)

El sistema resuelve el horario aplicable para un empleado en una fecha específica mediante **búsqueda jerárquica por prioridad**:

```
┌─────────────────────────────────────────────┐
│  PRIORIDAD 1: ScheduleOverride              │  ← Más Alta
│  (Excepción manual para fecha específica)   │
├─────────────────────────────────────────────┤
│  PRIORIDAD 2: EmployeeShift (EMPLOYEE)      │
│  (Asignación directa al empleado)           │
├─────────────────────────────────────────────┤
│  PRIORIDAD 3: EmployeeShift (DEPARTMENT)    │
│  (Asignación por departamento)              │
├─────────────────────────────────────────────┤
│  PRIORIDAD 4: Día de descanso implícito     │  ← Más Baja
│  (No hay asignación)                         │
└─────────────────────────────────────────────┘
```

### 4.2 Código de Resolución (schedule_resolver.py)

**Ubicación:** `core/services/schedule_resolver.py`

**Función Principal:** `resolve_schedule_unified(employee_id, target_date)`

```python
def resolve_schedule_unified(employee_id: int, target_date: date) -> ResolvedSchedule:
    # 1. Buscar ScheduleOverride
    override = ScheduleOverride.objects.filter(
        employee_id=employee_id,
        date=target_date
    ).first()
    if override:
        return _build_resolved(override.timetable, source="OVERRIDE")
    
    # 2. Buscar EmployeeShift (scope='EMPLOYEE')
    emp_shift = EmployeeShift.objects.filter(
        scope='EMPLOYEE',
        employee_id=employee_id,
        start_date__lte=target_date,
    ).filter(Q(end_date__gte=target_date) | Q(end_date__isnull=True))
    
    if emp_shift.exists():
        timetable = _resolve_shift_timetable(emp_shift.first(), target_date)
        if timetable:
            return _build_resolved(timetable, source="EMPLOYEE_SHIFT")
    
    # 3. Buscar EmployeeShift (scope='DEPARTMENT')
    emp = Employee.objects.get(id=employee_id)
    if emp.department:
        dept_shift = EmployeeShift.objects.filter(
            scope='DEPARTMENT',
            department_id=emp.department.id,
            start_date__lte=target_date,
        ).filter(Q(end_date__gte=target_date) | Q(end_date__isnull=True))
        
        if dept_shift.exists():
            timetable = _resolve_shift_timetable(dept_shift.first(), target_date)
            if timetable:
                return _build_resolved(timetable, source="DEPARTMENT_SHIFT")
    
    # 4. No se encontró asignación → Día de descanso
    return ResolvedSchedule(is_valid=False, error="NO_SHIFT_ASSIGNED")
```

### 4.3 Resolución de Timetable desde Shift

```python
def _resolve_shift_timetable(shift, target_date):
    # Calcular day_index según tipo de ciclo
    if shift.cycle_days > 0:
        # Ciclo largo (rotación)
        days_since_start = (target_date - emp_shift.start_date).days
        day_index = days_since_start % shift.cycle_days
    else:
        # Ciclo semanal (0=Lun, 6=Dom)
        day_index = target_date.weekday()
    
    # Buscar ShiftTimetable para ese día
    shift_tt = ShiftTimetable.objects.filter(
        shift=shift,
        day_index=day_index
    ).first()
    
    return shift_tt.timetable if shift_tt else None
```

---

## 🔄 5. FLUJO DE CÁLCULO DE ASISTENCIA

### 5.1 Proceso Completo

```
┌─────────────────────────────────────────────────────────┐
│ 1. Usuario solicita cálculo (rango de fechas, dept)    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 2. Se obtienen empleados activos del departamento      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 3. Filtrar empleados con EmployeeShift asignado        │
│    → Empleados SIN shift = SKIPPED (reportados)        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 4. POR CADA empleado + fecha:                          │
│    ┌───────────────────────────────────────────────┐   │
│    │ a) Resolver horario (resolve_schedule)        │   │
│    │ b) Obtener marcaciones (AttendanceLog)        │   │
│    │ c) Aplicar reglas de negocio                  │   │
│    │ d) Calcular estado (Present/Absent/Late/...)  │   │
│    │ e) Guardar en DailyAttendance                 │   │
│    └───────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 5. Retornar resumen:                                    │
│    - Registros procesados                               │
│    - Empleados saltados (con razón)                     │
│    - Ausencias detectadas                               │
└─────────────────────────────────────────────────────────┘
```

### 5.2 Estados de Resultado

| Estado | Descripción | Condición |
|--------|-------------|-----------|
| **Present** | Asistió correctamente | Check-in y Check-out dentro de tolerancia |
| **Late** | Llegó tarde | Check-in > (on_duty + late_allow_minutes) |
| **Early Leave** | Salió temprano | Check-out < (off_duty - early_allow_minutes) |
| **Absent** | No asistió | Sin marcaciones o fuera de ventanas |
| **Incomplete** | Incompleto (flexible) | Horario flexible con marcaciones insuficientes |

---

## 📐 6. CASOS DE USO PRÁCTICOS

### Caso 1: Asignación Individual

**Escenario:** Juan Pérez (EMP001) debe trabajar turno administrativo desde 2026-01-01

**Configuración:**
```json
// EmployeeShift
{
  "scope": "EMPLOYEE",
  "employee_id": 287,
  "shift_id": 5,
  "start_date": "2026-01-01",
  "end_date": null
}
```

**Resolución para 2026-01-15 (Miércoles):**
1. Busca Override → No existe
2. Busca EmployeeShift (EMPLOYEE) → ✅ Encontrado
3. Calcula `day_index = 2` (Miércoles)
4. Busca ShiftTimetable (shift=5, day=2) → Retorna Timetable "08:00-17:00"
5. **Horario aplicable:** 08:00-17:00

---

### Caso 2: Asignación por Departamento

**Escenario:** Todo el departamento "Producción" trabaja turno rotativo

**Configuración:**
```json
// EmployeeShift
{
  "scope": "DEPARTMENT",
  "department_id": 10,
  "shift_id": 7,
  "start_date": "2026-01-01",
  "end_date": "2026-12-31"
}
```

**Resolución para empleado del dpto Producción:**
1. Busca Override → No existe
2. Busca EmployeeShift (EMPLOYEE) → No existe
3. Busca EmployeeShift (DEPARTMENT) → ✅ Encontrado
4. Resuelve timetable del turno
5. **Todos los empleados del dpto usan el mismo horario**

---

### Caso 3: Excepción Manual

**Escenario:** María López debe trabajar horario especial el 2026-02-14

**Configuración:**
```json
// ScheduleOverride
{
  "employee_id": 290,
  "date": "2026-02-14",
  "timetable_id": 12  // Horario especial 10:00-19:00
}
```

**Resolución:**
1. Busca Override para fecha → ✅ Encontrado
2. **Horario aplicable:** 10:00-19:00 (ignora asignaciones de turno)

---

## 🎯 7. ENDPOINTS API

### Gestión de Jerarquía

| Endpoint | Método | Propósito |
|----------|--------|-----------|
| `/api/v1/departments/` | GET, POST | Gestionar departamentos |
| `/api/v1/shifts/` | GET, POST | Gestionar turnos |
| `/api/v1/timetables/` | GET, POST | Gestionar horarios |
| `/api/v1/employees/` | GET, POST | Gestionar personal |
| `/api/v1/employee-shifts/` | GET, POST | Asignar turnos |

### Cálculo de Asistencia

| Endpoint | Método | Propósito |
|----------|--------|-----------|
| `/api/v1/attendance/calculate/` | POST | Calcular asistencia periodo |
| `/api/v1/attendance/daily-attendance/` | GET | Consultar registros diarios |
| `/api/v1/attendance/absences/` | GET | Consultar ausencias (manual + detectadas) |

---

## ⚠️ 8. CONSIDERACIONES TÉCNICAS

### 8.1 Validaciones Críticas

1. **EmployeeShift debe tener vigencia válida:**
   - `start_date <= target_date`
   - `end_date >= target_date OR end_date IS NULL`

2. **ShiftTimetable debe existir para el día:**
   - Si no existe registro para `day_index` → día de descanso

3. **Empleado debe estar activo:**
   - `employee.active = True`

### 8.2 Rendimiento

- ✅ **Uso de select_related**: Reduce queries N+1
- ✅ **Filtrado temprano**: Descarta empleados sin shift antes de procesar
- ✅ **Logging detallado**: Rastrea empleados saltados con razón

### 8.3 Logs y Debugging

**Archivo:** `core/services/schedule_resolver.py`

```python
logger.debug("Schedule resolved via EMPLOYEE_SHIFT")
logger.warning("No schedule found - implicit rest day")
logger.error("Schedule resolution failed")
```

**Revisar logs cuando:**
- Empleados no aparecen en reporte
- Horarios incorrectos aplicados
- Cálculos de asistencia erróneos

---

## 📊 9. DIAGRAMA DE FLUJO VISUAL

```
                    ┌──────────────┐
                    │   EMPRESA    │
                    └──────┬───────┘
                           │
                           ↓
                    ┌──────────────┐
                    │ DEPARTAMENTO │ ←──────┐
                    └──────┬───────┘        │
                           │                 │
                 ┌─────────┴─────────┐       │
                 ↓                   ↓       │
          ┌──────────┐        ┌──────────┐  │
          │ EMPLEADO │        │  TURNO   │  │
          └──────────┘        └─────┬────┘  │
                 │                   │       │
                 │                   ↓       │
                 │            ┌──────────────┐
                 │            │ShiftTimetable│
                 │            └──────┬───────┘
                 │                   │
                 │                   ↓
                 │            ┌──────────────┐
                 │            │   HORARIO    │
                 │            └──────────────┘
                 │
                 └─────→ EmployeeShift ←──────┘
                              (EMPLOYEE/DEPARTMENT)
                                    ↓
                            ┌───────────────┐
                            │ CÁLCULO DIARIO│
                            └───────────────┘
```

---

## ✅ 10. CONCLUSIONES

### Fortalezas del Sistema:

1. ✅ **Flexibilidad Total**: Soporta asignaciones individuales, departamentales y excepciones
2. ✅ **Escalabilidad**: Maneja ciclos semanales y rotaciones complejas
3. ✅ **Trazabilidad**: Logs detallados de resolución y causas de ausencia
4. ✅ **Robustez**: Continúa procesando aunque fallen registros individuales
5. ✅ **Consistencia**: Único resolver usado por ambos engines (V1/V2)

### Flujo de Trabajo Recomendado:

1. **Configurar Empresa** → Datos generales
2. **Crear Departamentos** → Estructura organizacional
3. **Definir Horarios** → Franjas horarias con tolerancias
4. **Crear Turnos** → Patrones de trabajo
5. **Asociar Turno-Horario** → ShiftTimetable por día
6. **Registrar Empleados** → Personal asignado a departamentos
7. **Asignar Turnos** → EmployeeShift (individual o por dpto)
8. **Ejecutar Cálculo** → Procesar asistencia por periodo

---

**Documento generado:** 2026-02-09  
**Versión Sistema:** V2 (Engine Unificado)  
**Analista:** Sistema SRTimeWeb  
**Ubicación:** `/docs/TECHNICAL_HIERARCHY_ARCHITECTURE.md`
