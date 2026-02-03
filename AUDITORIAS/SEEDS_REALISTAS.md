# Seeds Realistas de Desarrollo Local

**Última actualización:** 2026-02-03  
**Estado:** ✅ COMPLETADO  
**Zona horaria:** UTC-3 (Argentina)

## 📋 Descripción

Script de seeds para simular flujos reales de fichaje en desarrollo local sin hardcodear lógica de negocio.

**Propósito:** Permitir testeo end-to-end de Timeline/Explanation con datos realistas.

**Ubicación:** `tests/seeds/attendance_log_realistic_dev.py`

## 🔧 Ejecución

```bash
# Opción 1: Desde shell de Django
cd srtime-django
python manage.py shell -c "exec(open('tests/seeds/attendance_log_realistic_dev.py', encoding='utf-8').read())"

# Opción 2: Dentro del shell interactivo
python manage.py shell
>>> exec(open('tests/seeds/attendance_log_realistic_dev.py', encoding='utf-8').read())
```

## 📊 Escenarios Generados

### Escenario A: Jornada Normal (Basic Entry/Exit)

**Empleado:** 200 (Empleado A)  
**Fecha:** 2026-02-10  
**Logs:** 2 registros

```
09:00 → Entrada (punch=0)
18:00 → Salida (punch=1)
```

**Duración:** 9 horas (540 minutos)  
**Timeline esperado:** 1 bloque WORK 09:00→18:00

**Curl de prueba:**
```bash
curl http://127.0.0.1:9000/api/v1/attendance/200/timeline/2026-02-10/
```

---

### Escenario B: Jornada Con Break

**Empleado:** 201 (Empleado B - con break)  
**Fecha:** 2026-02-11  
**Logs:** 4 registros

```
09:00 → Entrada (punch=0)
12:00 → Salida por break (punch=1)
13:00 → Retorno de break (punch=0)
18:00 → Salida (punch=1)
```

**Duración:** 8 horas netas (09:00-12:00: 3h + 13:00-18:00: 5h)  
**Timeline esperado:** 2 bloques WORK  
- Bloque 1: 09:00→12:00 (180 min)
- Bloque 2: 13:00→18:00 (300 min)

**Curl de prueba:**
```bash
curl http://127.0.0.1:9000/api/v1/attendance/201/timeline/2026-02-11/
```

---

### Escenario C: Jornada Incompleta

**Empleado:** 202 (Empleado C - incompleto)  
**Fecha:** 2026-02-12  
**Logs:** 1 registro

```
09:00 → Entrada (punch=0)
(SIN salida registrada)
```

**Duración:** Indeterminada  
**Timeline esperado:** [] (vacío - evento impar se ignora)  
**Day View esperado:** status=Partial

**Curl de prueba:**
```bash
curl http://127.0.0.1:9000/api/v1/attendance/202/timeline/2026-02-12/
```

---

### Escenario D: Error de Dispositivo (Doble Entrada)

**Empleado:** 203 (Empleado D - doble entrada)  
**Fecha:** 2026-02-13  
**Logs:** 3 registros

```
09:00 → Entrada 1 (punch=0) [CORRECTA]
09:01 → Entrada 2 (punch=0) [ERROR del dispositivo]
18:00 → Salida (punch=1)
```

**Duración:** Ambigua (¿09:00 o 09:01?)  

**Timeline ACTUAL (NAIVE - INCORRECTO):** 1 bloque 09:01→18:00 (BUGGY)
- Índice 0 (09:00) → ENTRADA ✓
- Índice 1 (09:01) → SALIDA (interpretado incorrectamente)
- Índice 2 (18:00) → ignorado (sin par)

**Timeline IDEAL (con punch) - CORRECTO:** 1 bloque 09:00→18:00

**Curl de prueba:**
```bash
curl http://127.0.0.1:9000/api/v1/attendance/203/timeline/2026-02-13/
```

**⚠️ Este escenario EXPONE el BUG de alternancia NAIVE** y valida la necesidad de mapeo punch/status en FASE C.

---

## 🧪 Testeo Day View y Explanation

### Day View

```bash
curl http://127.0.0.1:9000/api/v1/attendance/day/?employee_id=200&date=2026-02-10
```

**Esperado:** 
```json
{
  "employee_id": 200,
  "employee_name": "Empleado A",
  "date": "2026-02-10",
  "status": "Normal",
  "worked_minutes": 540,
  "logs": [...]
}
```

### Explanation

```bash
curl http://127.0.0.1:9000/api/v1/attendance/200/explanation/2026-02-10/
```

**Esperado:** Narrativa describiendo 9 horas de trabajo efectivas.

---

## ⚠️ SUPUESTOS DOCUMENTADOS

### VALORES SIMULADOS (NO representan mapping real de ZKTeco)

```
punch=0  → Entrada (SIMULADO)
punch=1  → Salida (SIMULADO)
status=1 → Evento normal (SIMULADO)
```

**Estos valores son SOLO para desarrollo local y permitir flujo end-to-end.**

---

## ❌ PROHIBIDO

- ❌ Inferir que `punch=0/1` es mapping real de ZKTeco
- ❌ Usar estos datos para validar lógica de negocio
- ❌ Asumir que `status=1` siempre significa lo mismo en producción
- ❌ Hardcodear lógica basada en estos valores
- ❌ Mergear estos supuestos como comportamiento productivo

---

## ✅ PERMITIDO

- ✅ Testear que Timeline/Explanation renderizan datos sin errores
- ✅ Verificar que queries funcionan correctamente
- ✅ Validar que el frontend recibe la estructura esperada
- ✅ Identificar bugs como el del Escenario D (alternancia NAIVE)
- ✅ Usar para desarrollo y QA local

---

## 📝 ESTRUCTURA DE MODELOS UTILIZADOS

### Device
```
- device_id (FK a AttendanceLog)
- name: "ZKTeco DEV Simulator"
- ip: "192.168.1.100"
- port: 4370
- enabled: True
```

### Employee
```
- user_id: 200-203 (unique)
- name: Empleado A/B/C/D
- active: True
```

### AttendanceLog
```
- device (FK requerido)
- user_id: "200"-"203"
- timestamp: DateTimeField (con UTC-3)
- status: 1 (simulado)
- punch: 0 (entrada) | 1 (salida)
- verify_mode: NULL
- workstate: NULL
- workcode: NULL
- punch_source: NULL
- raw_json: NULL

Constraint: UNIQUE(device, user_id, timestamp)
```

---

## 🔮 PRÓXIMOS PASOS

### FASE C: Punch/Workstate Mapping

Para implementar punch/workstate mapping en FASE C, se requiere:

1. **Obtener datos REALES de ZKTeco** (50-100 logs de dispositivo en producción)
2. **Documentar valores reales** de punch/status/workstate
3. **Actualizar seed template** con datos reales
4. **Crear suite de tests** con todos los tipos de seeds
5. **Implementar lógica de mapeo** con confianza

**Blocker:** Sin datos reales de ZKTeco, no se puede implementar FASE C.

---

## 📌 Notas Importantes

- **Zona horaria:** UTC-3 (Argentina) explícitamente configurada
- **Idempotencia:** El script es re-ejecutable (limpia antes de insertar)
- **Consistencia:** Todos los timestamps usan zona horaria uniforme
- **Sin regresiones:** Respeta datos existentes (otros employees)
- **Documentado:** Cada escenario explica qué esperar

---

## ✅ Estado Actual

- ✅ Script creado y funcional
- ✅ 4 escenarios de prueba (A, B, C, D)
- ✅ 10 registros de AttendanceLog (2+4+1+3)
- ✅ Todos los timestamps en UTC-3
- ✅ Documentación completa
- ✅ Testeable sin errores

**Listo para QA local y validación end-to-end de Timeline/Explanation.**
