# Assessment: Engines V1 y V2 - Análisis y Recomendaciones

**Fecha:** 2026-02-09  
**Status:** CRITICAL ISSUES FOUND + SOLUTIONS PROVIDED

---

## Resumen Ejecutivo

Actualmente existen DOS motores de cálculo paralelos pero DESINCRONIZADOS:

- **V1** (attendance_engine.py): En producción, maneja asistencia oficial
- **V2** (attendance_engine_v2.py): En validación shadow, tiene problemas estructurales

**Riesgo:** Divergencia de lógica causará discrepancias en migración.

**Oportunidad:** Consolidar antes de go-live.

---

## ISSUES CRÍTICOS ENCONTRADOS

### Problema 1: shift.cycle_days No Existe en Modelo

**V2 usa esto (línea 90):**

```
if shift.cycle_days and shift.cycle_days > 0:
    cycle_index = days_since_start % shift.cycle_days
    shift_tt = models.ShiftTimetable.objects.filter(
        shift=shift,
        day_index=cycle_index
    )
```

**Pero el modelo Shift es así:**

```
class Shift(models.Model):
    name = models.CharField(max_length=100)
    # cycle_days NO EXISTE
```

**V1 nunca lo usa (línea 144):**

```
day_idx = target_date.weekday()  # SIEMPRE semanal (0-6)
shift_tt = models.ShiftTimetable.objects.filter(
    shift_id=shift.id,
    day_index=day_idx
)
```

**Impacto:**

- V2 cae al branch "else" (weekly) cuando cycle_days es None
- Si alguien agrega cycle_days sin sincronizar V1 → divergencia garantizada
- Code está preparado pero infraestructura no existe

---

### Problema 2: Resolución de Horarios Diferente

**V1 (líneas 108-180, resolve_schedule):**

1. ScheduleOverride
2. EmployeeShift (EMPLOYEE scope)
3. EmployeeShift (DEPARTMENT scope) - búsqueda adicional
4. Resuelve solo por weekday (0-6)

**V2 (líneas 27-64, resolve_schedule):**

1. ScheduleOverride
2. EmployeeShift (EMPLOYEE scope)
3. Department.default_shift_id - DIFERENTE
4. Resuelve por cycle_days O weekday

**La diferencia clave:**

| Aspecto | V1 | V2 | Riesgo |
|---------|----|----|--------|
| Fallback | Query EmployeeShift DEPT | Query Department.default_shift_id | Si Department.default_shift no está seteado, V2 retorna is_valid=False |

**Ejemplo problemático:**

```
Departamento Marketing sin asignación de shift departamental
Department.default_shift_id = None

Empleado sin EmployeeShift directo:
- V1: Busca shift en shift_assignments del departamento → encuentra
- V2: Retorna is_valid=False → status "Absent"

RESULTADO: DISCREPANCIA GARANTIZADA
```

---

### Problema 3: Shadow Mode Existe pero No Se Usa

**ShadowComparisonService está creada PERO:**

- No se llama desde views_attendance.py
- No hay feature flag para activarla
- No hay reportes de diferencias V1 vs V2
- Desconocemos qué tan divergentes están realmente

**Ubicación actual:**

- core/services/shadow_comparison_service.py (existe)
- core/models_shadow.py (existe)
- Pero views_attendance.py solo usa V1

---

### Problema 4: Sin Test Suite

**Estado actual:**

- No hay test_engines.py
- No hay validation que V1 y V2 producen mismo resultado
- Sin casos de prueba para:
  - Empleado sin EmployeeShift
  - Timetable sin ShiftTimetable
  - Ciclo cíclico (cuando se agregue)
  - Cambio de horario mid-mes

---

### Problema 5: Logging Silencioso

**V1 (línea ~65):**

```
try:
    # Build DayContext...
except Exception as e:
    return DayContext.empty()  # Silently fails, NO logging
```

**V2 (línea ~52):**

```
return DayContext(is_valid=False)  # Same issue
```

**Consecuencia:** Imposible debuggear cuándo/por qué fallan cálculos en producción.

---

### Problema 6: Campos DailyAttendance No Mapeados

**V2 intenta asignar:**

```
daily.regular_minutes = result.regular_minutes  # ← Puede ser None
daily.night_minutes = result.night_minutes      # ← Puede ser None
```

**Si result es None o falta el campo:** AttributeError silencioso

---

## SOLUCIONES RECOMENDADAS

### Solución Priority 1: Crear Schedule Resolver Unificado

**Crear archivo:** core/services/schedule_resolver.py

```python
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, date, time, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ScheduleSource(Enum):
    OVERRIDE = "OVERRIDE"
    EMPLOYEE_SHIFT = "EMPLOYEE_SHIFT"
    DEPARTMENT_SHIFT = "DEPARTMENT_SHIFT"
    IMPLICIT_REST = "IMPLICIT_REST"
    UNRESOLVED = "UNRESOLVED"

class ScheduleResolutionError(Enum):
    NO_SHIFT_ASSIGNED = "NO_SHIFT_ASSIGNED"
    SHIFT_NO_TIMETABLES = "SHIFT_NO_TIMETABLES"
    SHIFT_TIMETABLE_MISSING_DAY = "SHIFT_TIMETABLE_MISSING_DAY"
    INVALID_TIMETABLE = "INVALID_TIMETABLE"

@dataclass
class ResolvedSchedule:
    is_valid: bool
    timetable: Optional[object]
    source: ScheduleSource
    error: Optional[ScheduleResolutionError]
    on_duty_dt: Optional[datetime]
    off_duty_dt: Optional[datetime]
    search_start: datetime
    search_end: datetime
```

**Función principal:**

```python
def resolve_schedule_unified(
    employee_id: int,
    target_date: date,
) -> ResolvedSchedule:
    """
    Single source of truth para resolución de horarios.
    
    Priority:
    1. ScheduleOverride
    2. EmployeeShift (EMPLOYEE scope)
    3. EmployeeShift (DEPARTMENT scope)
    4. Department.default_shift (si existe)
    5. Día de descanso implícito
    """
    # 1. Override
    override = models.ScheduleOverride.objects.filter(
        employee_id=employee_id,
        date=target_date
    ).select_related('timetable').first()
    
    if override and override.timetable:
        return _build_resolved_schedule(
            timetable=override.timetable,
            target_date=target_date,
            source=ScheduleSource.OVERRIDE,
        )
    
    # 2. EmployeeShift (EMPLOYEE scope)
    emp_shift = models.EmployeeShift.objects.filter(
        scope='EMPLOYEE',
        employee_id=employee_id,
        start_date__lte=target_date,
    ).filter(
        Q(end_date__gte=target_date) | Q(end_date__isnull=True)
    ).select_related('shift').first()
    
    if emp_shift and emp_shift.shift:
        shift_tt = _resolve_shift_timetable(
            shift=emp_shift.shift,
            emp_shift=emp_shift,
            target_date=target_date,
        )
        if shift_tt and shift_tt.timetable:
            return _build_resolved_schedule(
                timetable=shift_tt.timetable,
                target_date=target_date,
                source=ScheduleSource.EMPLOYEE_SHIFT,
            )
    
    # 3. EmployeeShift (DEPARTMENT scope)
    emp = models.Employee.objects.filter(id=employee_id).select_related(
        'department'
    ).first()
    
    if emp and emp.department:
        dept_shift = models.EmployeeShift.objects.filter(
            scope='DEPARTMENT',
            department_id=emp.department.id,
            start_date__lte=target_date,
        ).filter(
            Q(end_date__gte=target_date) | Q(end_date__isnull=True)
        ).select_related('shift').first()
        
        if dept_shift and dept_shift.shift:
            shift_tt = _resolve_shift_timetable(
                shift=dept_shift.shift,
                emp_shift=dept_shift,
                target_date=target_date,
            )
            if shift_tt and shift_tt.timetable:
                return _build_resolved_schedule(
                    timetable=shift_tt.timetable,
                    target_date=target_date,
                    source=ScheduleSource.DEPARTMENT_SHIFT,
                )
    
    # 4. Implicit rest day
    logger.warning(
        f"No schedule found for employee {employee_id} on {target_date}"
    )
    return ResolvedSchedule(
        is_valid=False,
        timetable=None,
        source=ScheduleSource.IMPLICIT_REST,
        error=ScheduleResolutionError.NO_SHIFT_ASSIGNED,
        on_duty_dt=None,
        off_duty_dt=None,
        search_start=datetime.combine(target_date, time.min),
        search_end=datetime.combine(target_date, time.max),
    )
```

**Función auxiliar para timetable:**

```python
def _resolve_shift_timetable(
    shift: object,
    emp_shift: object,
    target_date: date,
) -> Optional[object]:
    """Resuelve qué timetable aplica para este shift en esta fecha."""
    
    has_timetables = models.ShiftTimetable.objects.filter(
        shift=shift
    ).exists()
    
    if not has_timetables:
        logger.warning(
            f"Shift {shift.id} has no ShiftTimetable configured"
        )
        return None
    
    # Determinar day_index
    if hasattr(shift, 'cycle_days') and shift.cycle_days and shift.cycle_days > 0:
        days_since_start = (target_date - emp_shift.start_date).days
        day_index = days_since_start % shift.cycle_days
    else:
        day_index = target_date.weekday()
    
    shift_tt = models.ShiftTimetable.objects.filter(
        shift=shift,
        day_index=day_index,
    ).select_related('timetable').first()
    
    if not shift_tt:
        logger.warning(
            f"No ShiftTimetable for shift {shift.id} on day_index {day_index}"
        )
    
    return shift_tt
```

**BENEFICIO:** Una vez que se agregue cycle_days al modelo, AMBOS engines lo soportan automáticamente.

---

### Solución Priority 2: Agregación de cycle_days

**Crear migration:**

```python
# core/migrations/0103_shift_cycle_days.py

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0102_attendancelog_edited_at_attendancelog_edited_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='shift',
            name='cycle_days',
            field=models.IntegerField(
                default=0,
                verbose_name='Dias de Ciclo',
                help_text='0=ciclo semanal. >0=ciclo largo (ej: 28 dias rotacion)',
            ),
        ),
    ]
```

**Regla:** cycle_days=0 O NULL significa semanal (backward compatible).

---

### Solución Priority 3: Feature Flag Shadow Mode

**En settings.py:**

```python
ATTENDANCE_SHADOW_ENABLED = env.bool('ATTENDANCE_SHADOW_ENABLED', default=False)
ATTENDANCE_SHADOW_LOG_CRITICAL = env.bool('ATTENDANCE_SHADOW_LOG_CRITICAL', default=True)
```

**En views_attendance.py:**

```python
from django.conf import settings
from core.services.shadow_comparison_service import get_shadow_service

@api_view(['POST'])
def calculate_attendance(request):
    run_shadow = settings.ATTENDANCE_SHADOW_ENABLED
    
    results, skipped_employees = calculate_period(start_date, end_date, department_id)
    
    if run_shadow:
        shadow_service = get_shadow_service()
        shadow_results = []
        
        for daily in results:
            try:
                emp = models.Employee.objects.get(id=daily.employee_id)
                shadow = shadow_service.run_shadow_for_day(
                    employee=emp,
                    target_date=daily.date,
                    v1_daily_attendance=daily,
                )
                if shadow:
                    shadow_results.append(shadow)
            except Exception as e:
                logger.error(f"Shadow failed: {e}")
    
    return Response({
        'results': DailyAttendanceSerializer(results, many=True).data,
        'skipped_employees': skipped_employees,
        'shadow_count': len(shadow_results) if run_shadow else 0,
    })
```

---

### Solución Priority 4: Test Suite Básico

**Crear:** tests/test_engines_consistency.py

```python
import pytest
from datetime import date, datetime, time, timedelta
from django.test import TestCase

from core import models
from core.services.schedule_resolver import resolve_schedule_unified

class TestScheduleResolution(TestCase):
    
    def setUp(self):
        self.company = models.Company.objects.create(name="Test Corp")
        self.dept = models.Department.objects.create(
            name="Engineering",
            company=self.company,
        )
        self.timetable = models.Timetable.objects.create(
            name="Standard 9-5",
            on_duty_time=time(9, 0),
            off_duty_time=time(17, 0),
            is_flexible=False,
        )
        self.shift = models.Shift.objects.create(name="Day Shift")
        models.ShiftTimetable.objects.create(
            shift=self.shift,
            timetable=self.timetable,
            day_index=0,
        )
        self.employee = models.Employee.objects.create(
            user_id="EMP001",
            name="John Doe",
            department=self.dept,
        )
        self.target_date = date(2026, 2, 9)
    
    def test_resolve_with_employee_shift(self):
        models.EmployeeShift.objects.create(
            scope='EMPLOYEE',
            employee=self.employee,
            shift=self.shift,
            start_date=self.target_date,
        )
        
        resolved = resolve_schedule_unified(
            self.employee.id,
            self.target_date,
        )
        
        assert resolved.is_valid
        assert resolved.timetable.id == self.timetable.id
```

---

## Resumen de Cambios

| Problema | Solución | Tiempo |
|----------|----------|--------|
| cycle_days no existe | Crear migration + agregar field | 30 min |
| V1 y V2 divergen | Crear schedule_resolver.py unificado | 2 hrs |
| Sin shadow integration | Agregar feature flag en settings | 1 hr |
| Sin tests | Crear test_engines_consistency.py | 2 hrs |
| Logging silencioso | Agregar logging estructurado | 1 hr |

**Total:** 6.5 horas

---

## Checklist de Implementación

- [ ] Crear core/services/schedule_resolver.py
- [ ] Crear migration 0103_shift_cycle_days
- [ ] Refactor attendance_engine.py para usar resolver
- [ ] Refactor attendance_engine_v2.py para usar resolver
- [ ] Agregar feature flags en settings.py
- [ ] Crear tests/test_engines_consistency.py
- [ ] Ejecutar tests: ambos engines producen mismo resultado
- [ ] Ejecutar shadow mode en QA 1-2 semanas
- [ ] Analizar ShadowCalculation para discrepancias
- [ ] Resolver todos los MAJOR/CRITICAL issues
- [ ] Migrar a V2 en producción

---

**Preparado:** Análisis Exhaustivo del Sistema  
**Fecha:** 2026-02-09
