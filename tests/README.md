# SRTime Django - Test Suite

Documentación y guía para ejecutar los tests del sistema de asistencia.

## 📋 Estructura

```
tests/
├── __init__.py                                  # Package init
├── README.md                                    # Esta documentación
├── test_flexible_processing_integration.py      # Testing básico de processador flexible
├── test_schedule_resolver.py                    # Tests de resolución de horarios (9 tests)
├── test_shadow_mode.py                          # Tests de shadow mode (8 tests)
└── test_engines_consistency.py                  # Tests consistencia V1/V2 (17 tests)
```

## 🚀 Ejecución Rápida

### Todos los tests
```bash
python manage.py test
```

### Tests específicos
```bash
# Solo tests de consistencia de engines
python manage.py test tests.test_engines_consistency -v 1

# Solo tests de schedule resolver
python manage.py test tests.test_schedule_resolver -v 1

# Solo tests de shadow mode
python manage.py test tests.test_shadow_mode -v 1
```

### Test de integración de procesamiento flexible
```bash
# Como módulo Python
python -m tests.test_flexible_processing_integration

# O en Django shell
python manage.py shell -c "from tests.test_flexible_processing_integration import test_phase1_phase2; test_phase1_phase2()"
```

## 📊 Test Suites Disponibles

### 1. Schedule Resolver Tests (9/9 ✅)
**Archivo:** `test_schedule_resolver.py`

Valida que la resolución de horarios funciona correctamente:
- Resolución de ScheduleOverride
- Resolución de EmployeeShift (EMPLOYEE scope)
- Resolución de EmployeeShift (DEPARTMENT scope)
- Resolución de ciclos semanales (0-6 = Monday-Sunday)
- Resolución de ciclos largos (rotaciones de N días)
- Manejo de horarios flexibles
- Manejo de horarios fijos

```bash
python manage.py test tests.test_schedule_resolver -v 2
```

### 2. Shadow Mode Tests (8/8 ✅)
**Archivo:** `test_shadow_mode.py`

Valida que el shadow mode funciona correctamente:
- Servicio de shadow mode
- Extracción de resultados V1
- Ejecución de cálculos V2
- Comparación y tolerancia
- Endpoint API de shadow_comparison

```bash
python manage.py test tests.test_shadow_mode -v 2
```

### 3. Engines Consistency Tests (17/17 ✅)
**Archivo:** `test_engines_consistency.py`

Valida que V1 y V2 producen resultados idénticos:

#### TestEngineScheduleConsistency (3 tests)
- Schedule resolution consistency
- EMPLOYEE_SHIFT resolution
- DEPARTMENT_SHIFT resolution

#### TestEngineCalculationConsistency (5 tests)
- Normal day calculation
- Late arrival handling
- Early departure handling
- Overtime calculation
- Multiple logs handling

#### TestEngineOvernightShiftConsistency (2 tests)
- Overnight shift calculation
- Cross-midnight transitions

#### TestEngineEdgeCases (3 tests)
- No shift assigned
- Empty shift configured
- Multiple check-ins/check-outs

#### TestEngineWeeklyCycleConsistency (4 tests)
- Weekly cycle resolution (Mon-Sun)
- Employee with weekly schedule
- Overnight shifts with weekly cycle
- Multiple day scenarios

```bash
python manage.py test tests.test_engines_consistency -v 2
```

### 4. Flexible Processing Integration Test
**Archivo:** `test_flexible_processing_integration.py`

Prueba End-to-End del procesamiento flexible:
- Validación de punches
- Construction de bloques de trabajo
- Análisis de gaps (pausas)
- Atribución de bloques
- Handling de turnos nocturnos
- Split de medianoche

```bash
python -m tests.test_flexible_processing_integration
```

## 🔍 Ejecutar con Verbose Output

```bash
# Máximo detalle (verbose=2)
python manage.py test tests -v 2

# Detalle moderado (verbose=1 - default)
python manage.py test tests -v 1

# Sin output (verbose=0)
python manage.py test tests -v 0
```

## 📈 Estadísticas Actuales

| Suite | Tests | Status |
|-------|-------|--------|
| Schedule Resolver | 9 | ✅ PASSING |
| Shadow Mode | 8 | ✅ PASSING |
| Engines Consistency | 17 | ✅ PASSING |
| Flexible Processing Integration | 1 | ⚙️ Manual |
| **TOTAL** | **34** | **✅ 34/34** |

## 🔧 Configuraciones de Timetable (Sin Hardcoding)

Todos los parámetros de cálculo son configurables vía el modelo `Timetable`:

```python
late_allow_minutes = 5              # Tolerancia llegada tarde (min)
early_leave_allow_minutes = 5       # Tolerancia salida temprana (min)
break_minutes = 60                  # Tiempo de descanso (min)
rounding_rule = 'none'              # 'none', '5min', '10min', '15min', '30min'
overtime_threshold_minutes = 0      # Umbral mínimo para que cuente overtime
```

## 🧪 Que se Prueba

### Escenarios Cubiertos

1. **Schedule Resolution**
   - ✅ Prioridad OVERRIDE > EMPLOYEE > DEPARTMENT
   - ✅ Ciclos semanales (Mon-Sun automation)
   - ✅ Ciclos largos (rotaciones de N días)
   - ✅ Horarios flexibles vs fijos

2. **Cálculos de Asistencia**
   - ✅ Entrada normal
   - ✅ Llegada tarde (con tolerancia)
   - ✅ Salida temprana (con tolerancia)
   - ✅ Horas extra (con threshold mínimo)
   - ✅ Tiempo trabajado (bruto - break)

3. **Casos Edge**
   - ✅ Sin horario asignado (implicit rest)
   - ✅ Shift vacío (no timetables)
   - ✅ Múltiples logs misma sesión
   - ✅ Turnos nocturnos (cruzan medianoche)

4. **Consistency V1/V2**
   - ✅ Ambos engines usan mismo schedule resolver
   - ✅ Ambos producen idénticos resultados
   - ✅ Shadow mode valida en paralelo

## 📝 Notas Importantes

- Tests usan timezone-aware datetimes (Django USE_TZ=True)
- Se validan tolerancias mediante sustracción (20 min tarde - 5 min tolerancia = 15 min)
- Overtime solo cuenta si >= threshold configurado
- Shadow mode valida pero nunca afecta producción

## 🚨 Troubleshooting

### "DateTimeField received naive datetime"
**Solución:** Todos los datetimes en tests deben ser timezone-aware usando `timezone.make_aware()`

### "Schedule resolution failed" 
**Solución:** Verificar que EmployeeShift tiene:
- Shift asignado
- Shift tiene ShiftTimetable configurado para el día
- start_date <= test_date
- end_date >= test_date (o null)

### Logs no encontrados en get_logs()
**Solución:** Validar que AttendanceLog.timestamp está dentro de search_start y search_end

## 📚 Referencias

- Django Testing: https://docs.djangoproject.com/en/stable/topics/testing/
- Model Documentation: `core/models.py`
- Engine Implementation: `core/services/attendance_engine.py`
- Schedule Resolver: `core/services/schedule_resolver.py`
- Shadow Mode: `core/services/shadow_mode_service.py`
