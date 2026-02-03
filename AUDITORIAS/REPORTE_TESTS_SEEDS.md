# Reporte de Auditoría - Tests Ejecutados (Seeds)

**Fecha:** 2026-02-03  
**Contexto:** Validación de endpoints usando seeds realistas en DEV  
**Servidor:** Server ON durante todos los tests  
**Zona horaria:** Se muestra en UTC por `USE_TZ=True` (09:00 AR → 12:00 UTC)

---

## 1) Datos base usados

Seeds: [tests/seeds/attendance_log_realistic_dev.py](../tests/seeds/attendance_log_realistic_dev.py)

Employee IDs relevantes:
- `id=2`, `user_id=200`, `Empleado A`

---

## 2) Tests ejecutados

### 2.1 Timeline - Escenario A

**Endpoint:**
`GET /api/v1/attendance/2/timeline/2026-02-10/`

**Resultado:** 200 OK

**Salida observada (resumen):**
- `blocks`: 1
- `type`: WORK
- `start_time`: 12:00
- `end_time`: 21:00
- `duration_minutes`: 540

**Observación:** corresponde a 09:00→18:00 AR, convertido a UTC.

---

### 2.2 Day View - Escenario A

**Endpoint:**
`GET /api/v1/attendance/day/?employee_id=2&date=2026-02-10`

**Resultado:** 200 OK

**Salida observada (resumen):**
- `status`: Normal
- `worked_minutes`: 540
- `logs`: IN 12:00 / OUT 21:00

**Observación:** coincide con el seed y la conversión a UTC.

---

### 2.3 Explanation - Escenario A

**Endpoint:**
`GET /api/v1/attendance/2/explanation/2026-02-10/`

**Resultado:** 200 OK

**Salida observada (resumen):**
- `summary`: 540 minutos (9.0 horas)
- `Entrada`: 12:00
- `Salida`: 21:00

---

## 3) Conclusiones

- Los endpoints Timeline, Day View y Explanation responden correctamente con los datos seeded.
- La representación horaria en la API está en UTC por `USE_TZ=True` (comportamiento esperado).
- No se detectaron errores funcionales en los endpoints testeados.

---

## 4) Nota de cumplimiento

Este reporte no infiere reglas de negocio ni mapeos reales de ZKTeco. Se limita a verificar funcionamiento con datos de desarrollo.
