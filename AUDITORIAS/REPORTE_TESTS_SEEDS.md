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

### 2.4 Timeline - Escenario B (break)

**Endpoint:**
`GET /api/v1/attendance/3/timeline/2026-02-11/`

**Resultado:** 200 OK

**Salida observada (resumen):**
- `blocks`: 2
- Bloque 1: 12:00→15:00 (180 min)
- Bloque 2: 16:00→21:00 (300 min)

**Observación:** corresponde a 09:00→12:00 y 13:00→18:00 AR, convertido a UTC.

**Limitación expuesta:** alternancia NAIVE no valida si OUT es break o salida final.

---

### 2.5 Timeline - Escenario C1 (1 evento)

**Endpoint:**
`GET /api/v1/attendance/4/timeline/2026-02-12/`

**Resultado:** 200 OK

**Salida observada (resumen):**
- `blocks`: 0 (vacío)

**Limitación expuesta:** evento impar se ignora; no hay forma de inferir estado final.

---

### 2.6 Timeline - Escenario C2 (3 eventos)

**Endpoint:**
`GET /api/v1/attendance/6/timeline/2026-02-12/`

**Resultado:** 200 OK

**Salida observada (resumen):**
- `blocks`: 1
- Bloque 1: 12:00→15:00 (180 min)

**Observación:** corresponde a 09:00→12:00 AR, convertido a UTC. El último evento queda sin par.

**Limitación expuesta:** alternancia NAIVE descarta el último evento impar.

---

### 2.7 Timeline - Escenario D (doble entrada)

**Endpoint:**
`GET /api/v1/attendance/5/timeline/2026-02-13/`

**Resultado:** 200 OK

**Salida observada (resumen):**
- `blocks`: 1
- Bloque 1: 12:00→12:01 (1 min)

**Limitación expuesta:** alternancia NAIVE interpreta IN-IN como IN-OUT, generando bloque incorrecto.

---

## 3) Conclusiones

- Los endpoints Timeline, Day View y Explanation responden correctamente con los datos seeded.
- La representación horaria en la API está en UTC por `USE_TZ=True` (comportamiento esperado).
- No se detectaron errores funcionales en los endpoints testeados.
- Quedaron evidenciadas limitaciones de alternancia NAIVE en C1/C2/D.

---

## 4) Nota de cumplimiento

Este reporte no infiere reglas de negocio ni mapeos reales de ZKTeco. Se limita a verificar funcionamiento con datos de desarrollo.
