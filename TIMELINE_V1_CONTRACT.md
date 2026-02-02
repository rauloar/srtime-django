# 📋 TIMELINE v1 — CONTRATO FUNCIONAL

**Versión:** 1.0  
**Congelado desde:** 2026-02-02  
**Estado:** ESTABLE  
**Baseline:** c666fb7 + mejoras incrementales  

---

## 🎯 ¿QUÉ ES TIMELINE v1?

**Timeline v1** es un endpoint que retorna hechos cronológicos desde `AttendanceLog` sin cálculos de horarios ni políticas de negocio.

```
GET /api/v1/attendance/{employee_id}/timeline/{date}/
```

**Propósito:**
- Mostrar bloques de tiempo de actividad
- Visualizar entrada/salida de manera legible
- Base para análisis futuro (sin comprometerse a lógica compleja hoy)

---

## 📐 CONTRATO TÉCNICO

### Request

```
GET /api/v1/attendance/1/timeline/2026-02-02/
```

**Parámetros:**
- `employee_id` (path) - ID del empleado
- `date` (path) - Fecha en formato YYYY-MM-DD

---

### Response — Status 200 OK

**Caso normal (con datos):**
```json
{
  "blocks": [
    {
      "type": "WORK",
      "start_time": "11:00",
      "end_time": "20:00",
      "duration_minutes": 540
    }
  ]
}
```

**Caso sin datos:**
```json
{
  "blocks": []
}
```

---

## 🔧 IMPLEMENTACIÓN ACTUAL

### Fuente de datos
- **BD:** `AttendanceLog`
- **Query:** Filtrado por `user_id` (string) + `date`
- **Orden:** `timestamp ASC`

### Lógica de bloques
1. Obtener todos los logs de la fecha
2. **Alternancia NAIVE:** 
   - Índice 0, 2, 4, ... = IN (start_time)
   - Índice 1, 3, 5, ... = OUT (end_time)
3. Agrupar en pares consecutivos
4. Calcular duración: `(out_timestamp - in_timestamp) / 60`
5. Retornar bloques tipo "WORK"

### Pseudocódigo
```python
logs = AttendanceLog.filter(user_id, date).order_by(timestamp)
blocks = []

for i in range(0, len(logs) - 1, 2):
    in_log = logs[i]
    out_log = logs[i + 1]
    if out_log exists:
        block = {
            "type": "WORK",
            "start_time": in_log.time.strftime("%H:%M"),
            "end_time": out_log.time.strftime("%H:%M"),
            "duration_minutes": (out_log - in_log) / 60
        }
        blocks.append(block)

return {"blocks": blocks}
```

---

## 🎭 CASOS EDGE

### ✅ SOPORTADOS (retorna 200 OK)

| Caso | Entrada | Salida |
|------|---------|--------|
| Employee no existe | `employee_id=999` | `{"blocks": []}` |
| Sin logs en fecha | Empleado válido, fecha sin marcaciones | `{"blocks": []}` |
| 1 solo log (impar) | 1 marcación | `{"blocks": []}` (ignora último sin par) |
| 2 logs (par normal) | Entrada + Salida | 1 bloque WORK |
| 3 logs (impar con resto) | IN, OUT, IN | 1 bloque WORK (ignora último IN) |
| Múltiples pares | 4, 6, 8+ logs | N bloques WORK correspondientes |

---

## ❌ QUÉ NO ES TIMELINE v1

**Timeline v1 es una "cámara de hechos"**, no un "analizador de políticas":

| Aspecto | ❌ NO hace |
|--------|-----------|
| Horarios | ❌ No consulta `Timetable` |
| Validación | ❌ No valida `punch` ni `workstate` |
| Tardanzas | ❌ No calcula `late_minutes` |
| Ausencias | ❌ No detecta "no llegó" |
| Permisos | ❌ No consulta `Leave` |
| Excepciones | ❌ No aplica `ScheduleOverride` |
| Inferencias | ❌ No adivina intenciones |
| Clasificaciones | ❌ No mapea "tipo de jornada" |

---

## ⚠️ LIMITACIONES CONOCIDAS

### 1. Alternancia NAIVE
```
Problema:   Si hay 2 logs fuera de orden, se procesan mal
Síntoma:    Bloques con start > end
Causa:      No valida contra punch/workstate
Estado:     CONOCIDO, PENDIENTE MEJORA FASE C
```

### 2. Sin uso de metadata
```
AttendanceLog captura:
- punch (tipo de marcación)
- workstate (estado del trabajo)
- punch_source (origen del evento)

Timeline v1: ⚠️ LOS IGNORA
```

### 3. Ambigüedad en casos impares
```
Ejemplo:  [11:00 IN, 12:00 OUT, 20:00 IN]
Resultado: 1 bloque WORK (11:00→12:00)
           Ignora el último IN (sin OUT)
           
¿Intención? No queda claro hasta FASE C
```

---

## 🔒 GARANTÍAS v1

✅ **SÍ garantiza:**
1. Datos crudos de `AttendanceLog` (nunca modificados)
2. Bloques en orden cronológico
3. Duraciones exactas (diferencia de timestamps)
4. Mismo tratamiento para todos los empleados
5. Respuesta 200 OK en todos los casos (nunca 404)

❌ **NO garantiza:**
1. Precisión según horarios configurados
2. Detección automática de anomalías
3. Clasificación de tardanzas/ausencias
4. Cumplimiento de políticas laborales

---

## 📊 EJEMPLO COMPLETO

### Escenario
- Empleado: `Test User` (ID=1, user_id=100)
- Fecha: 2026-02-02
- Logs en DB:
  ```
  2026-02-02 11:00:00 status=1 punch=1
  2026-02-02 20:00:00 status=1 punch=1
  ```

### Request
```bash
curl http://127.0.0.1:9000/api/v1/attendance/1/timeline/2026-02-02/
```

### Response
```json
{
  "blocks": [
    {
      "type": "WORK",
      "start_time": "11:00",
      "end_time": "20:00",
      "duration_minutes": 540
    }
  ]
}
```

### Interpretación
- 1 período de trabajo
- Duración: 540 minutos = 9 horas
- Sin información sobre si fue tardío, ausencia, etc.

---

## 🔄 VERSIONADO

### v1 (Actual)
- Naive alternancia
- Sin metadata processing
- Bloques simples

### v2 (Futuro — No implementado)
- Podría validar `punch` field
- Mapeo explícito IN/OUT
- Mejor manejo de casos impares

### v3+ (Roadmap)
- Integración con horarios
- Detección de anomalías
- Recomendaciones

---

## 📝 NOTAS PARA DEVS

### Al consumir Timeline v1:

1. **No asumir completitud:** Si hay 1 log, puede haber error de dispositivo
2. **Mostrar "sin datos" elegantemente:** `blocks: []` es válido
3. **No calcular horarios:** Es trabajo futuro
4. **Preparar UI flexible:** Cuando llegue v2, estructura seguirá igual

### Al modificar Timeline v1:

1. **No cambiar estructura de respuesta:** Frontend ya la consume
2. **No introducir reglas nuevas:** Eso es FASE C
3. **No tocar alternancia sin validar:** Hay lógica dependiente
4. **Documentar cualquier cambio:** Aquí, en este archivo

---

## 🚦 ESTADO DE VALIDACIÓN

**Tests ejecutados (2026-02-02):**
- ✅ Case normal: 2 logs → 1 bloque WORK
- ✅ Case empty: 0 logs → bloques vacíos
- ✅ Case employee missing: id=999 → bloques vacíos
- ✅ HTTP status: 200 OK en todos los casos
- ✅ Integración: No rompe day view, explanation, otros endpoints

**Regresiones encontradas:** 0

---

## 📌 RESUMEN

| Aspecto | Valor |
|--------|-------|
| **Propósito** | Hechos cronológicos, sin políticas |
| **Fuente** | AttendanceLog crudo |
| **Bloque base** | Pares IN→OUT (naive) |
| **HTTP status** | 200 siempre |
| **Estabilidad** | Congelada v1 |
| **Próxima mejora** | FASE C (si se aprueba) |

---

**Este contrato es el acuerdo explícito entre backend y frontend.**  
**Cualquier cambio debe ser revisado y documentado aquí.**

---

*Fin de documento v1.*
