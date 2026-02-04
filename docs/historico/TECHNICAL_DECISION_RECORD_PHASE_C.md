# Technical Decision Record - FASE C
## Limites de Inferencia de Estado de Fichaje

**Fecha:** 2026-02-03  
**Contexto:** Análisis de limitaciones observadas en Timeline v1 (FROZEN)  
**Status:** ⛔ **APPROVED – FASE C BLOCKED BY DESIGN**

> FASE C formalmente congelada hasta obtener datos reales de ZKTeco y aprobación ejecutiva explícita.  

---

## 📋 Resumen Ejecutivo

El análisis de stress tests ejecutados sobre **Timeline v1** con seeds realistas evidencia que el algoritmo de alternancia NAIVE es **estructuralmente frágil** ante datos incompletos o inesperados. 

Esta limitación no es un bug aislado, sino una consecuencia de intentar **inferir estado de fichaje sin metadatos explícitos**.

**Decisión propuesta:** Antes de FASE C, declarar explícitamente qué casos son **no recuperables** y cuáles requieren intervención manual o supervisión.

---

## 🔍 Evidencia Observada

### Caso 1: Entrada-Entrada-Salida (IN-IN-OUT)
**Escenario D - Stress Test**

```
Entrada:   09:00 (punch=0, índice 0)
Entrada:   10:00 (punch=0, índice 1)  ← Duplicada o error de captura
Salida:    18:00 (punch=1, índice 2)
```

**Comportamiento actual (NAIVE):**
```
Bloque generado: 09:00 → 10:00 (1 minuto)
```

**Problema:** 
- Interpreta el segundo IN como salida (alternancia par-impar)
- Genera duración de **1 minuto** (incorrecto)
- El tercio evento se descarta

**¿Por qué ocurre?**  
Sin metadato `punch` o `workstate` confiable, el algoritmo asume alternancia perfecta. Cualquier desviación rompe la lógica.

---

### Caso 2: Evento Impar sin Salida Correspondiente
**Escenario C - Stress Test**

```
Entrada:   09:00 (punch=0, índice 0)
(Sin salida)
```

**Comportamiento actual (NAIVE):**
```
Bloques: [] (vacío)
```

**Problema:**
- El sistema ignora eventos sin pareja
- No existe forma de inferir si el empleado sigue dentro o si olvidó registrar salida
- La jornada "desaparece" de la interfaz

**¿Por qué ocurre?**  
Alternancia requiere pares (IN-OUT, IN-OUT, ...). Un evento impar no tiene contrapartida → se descarta silenciosamente.

---

### Caso 3: Eventos Impares Múltiples
**Escenario C2 - Stress Test**

```
Entrada:   09:00 (punch=0, índice 0)
Salida:    12:00 (punch=1, índice 1)  → Break
Entrada:   13:00 (punch=0, índice 2)  ← Último evento, impar
(Sin salida final)
```

**Comportamiento actual (NAIVE):**
```
Bloque generado: 09:00 → 12:00 (3 horas)
Evento 13:00:     Ignorado
```

**Problema:**
- El tercer evento queda sin procesar
- El sistema muestra **parcialmente incorrecto**: oculta que el empleado reinició jornada a las 13:00
- Frontend no refleja estado actual

**¿Por qué ocurre?**  
Misma razón: índice impar → sin pareja → descartado.

---

### Caso 4: Break Vs. Salida Final (Ambigüedad Semántica)
**Escenario B - Stress Test**

```
Entrada:   09:00 (punch=0)
Salida:    12:00 (punch=1)  ← ¿Es break o cierre de jornada?
Entrada:   13:00 (punch=0)
Salida:    18:00 (punch=1)
```

**Comportamiento actual (NAIVE):**
```
Bloques: [09:00-12:00 (3h), 13:00-18:00 (5h)]
```

**Problema:** 
- El algoritmo **adivina** basado en patrón (si hay siguiente IN, asume break)
- Sin validación de intervalos razonables (¿30 min de break?, ¿8 horas?)
- No soporta jornadas nocturnas (ej: entrada 22:00, salida 06:00 al día siguiente)

**¿Por qué ocurre?**  
El evento `punch=1` es completamente ambiguo sin contexto: podría ser descanso, error, o fin de día.

---

## ⚠️ Qué el Sistema NO Debe Inferir

La siguiente lista documenta **casos donde NO es seguro intentar reconstrucción de estado:**

### 1. Salidas Automáticas
❌ **PROHIBIDO:** Asumir cierre de jornada si no hay evento registrado  
*Razón:* Falta de evento es indeterminada (olvidó registrar, siguió trabajando sin captura, sistema caído)  
*Riesgo:* Falsear asistencia creditando horas no verificadas

### 2. Breaks Implícitos
❌ **PROHIBIDO:** Inferir descanso basado en gaps de tiempo  
*Razón:* Un gap podría ser: trabajo fuera del área de captura, almuerzo no reglamentario, inactividad registrada  
*Riesgo:* Asignar crédito de break sin supervisión explícita

### 3. Jornadas Nocturnas o Multigía
❌ **PROHIBIDO:** Asumir que OUT→IN implica salida+entrada en el mismo día  
*Razón:* Un turno podría ser 22:00 a 06:00 (siguiente día), requeriendo cruce de medianoche  
*Riesgo:* Dividir jornada nocturna en dos días, perdiendo contexto de turno

### 4. Duplicaciones o Errores de Captura
❌ **PROHIBIDO:** Distinguir entre IN duplicada vs. primera entrada real sin metadato  
*Razón:* Sin `workstate` o validación de ZKTeco, imposible saber si segundo IN es:
  - Error de captura (doble lectura de dedo)
  - Reinicio del terminal
  - Intento de acceso rechazado
*Riesgo:* Borrar evento potencialmente válido

### 5. Compensaciones o Cambios ad-hoc
❌ **PROHIBIDO:** Recalcular jornadas basadas en reglas de negocio no registradas  
*Razón:* Sin campo `adjustment` o `note`, no hay trazabilidad de cambios  
*Riesgo:* Timeline mutable sin auditoría

---

## 🎯 Principio Rector

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Es preferible NO MOSTRAR un bloque antes que mostrar UNO INCORRECTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Este principio implica:

1. **Defensa contra falsos positivos**  
   Una duración inventada (ej: 1 min por IN-IN) daña confiabilidad más que ausencia de dato

2. **Trazabilidad sobre completitud**  
   Es mejor marcar un día como "Incompleto" que mostrar "Normal" con horas fantasma

3. **Supervisión humana como escalada**  
   Si el sistema no puede reconstruir con seguridad, debe alertar para revisión manual

---

## 🛡️ Reglas Defensivas Aceptables (Conceptuales)

Las siguientes reglas **podrían** implementarse en FASE C sin violar el principio rector, pero **requieren validación** y **no presuponen mapeos reales de ZKTeco**:

### Regla D1: Rechazo de Eventos Incompletos
**Concepto:** Si un día tiene eventos de cantidad impar, marcar jornada como `INCOMPLETE` vs. `NORMAL`

**Condiciones:**
- Número de eventos ≤ 1 (sin pareja) → `INCOMPLETE`
- Número de eventos ≥ 3 e impar → `INCOMPLETE` (último evento sin cerrar)

**Beneficio:** Evita descartes silenciosos; avisa al usuario que hay datos incompletos

**Riesgo:** Falsos positivos si jornada real es nocturna (OUT→IN cruza medianoche)

---

### Regla D2: Validación de Intervalos Mínimos
**Concepto:** Si un bloque IN-OUT dura < 1 minuto (o > 16 horas), marcar como `SUSPICIOUS`

**Condiciones:**
- `duration < 60 segundos` → Posible captura duplicada
- `duration > 16 horas` → Posible jornada nocturna no delimitada

**Beneficio:** Identifica datos malformados sin descartarlos

**Riesgo:** Requiere threshold configurable (¿1 min?, ¿5 min?)

---

### Regla D3: Rechazo de Alternancia Cortada
**Concepto:** En lugar de descartar silencios, generar bloque `PENDING` si hay IN sin OUT

**Condiciones:**
- Último evento del día es `punch=0` (entrada) → Crear bloque marcado como `OPEN`
- Usuario puede cerrar manualmente o supervisión lo valida

**Beneficio:** Visibiliza jornadas abiertas vs. ignorarlas

**Riesgo:** Cambia semántica de API (nuevo status `OPEN` o `PENDING`)

---

### Regla D4: Descarte Explícito de Secuencias Ambiguas
**Concepto:** Si se detectan secuencias IN-IN o OUT-OUT consecutivas, descartar evento duplicado + marcar para revisión

**Condiciones:**
- Dos eventos `punch=0` (IN) con intervalo < 5 minutos → Posible duplicación
- Dos eventos `punch=1` (OUT) con intervalo < 5 minutos → Posible duplicación
- Marcar el segundo como `DISCARDED` (trazable, no borrado)

**Beneficio:** Maneja errores de captura explícitamente

**Riesgo:** ¿Quién decide cuál es "duplicado"? Requiere supervisión

---

## 📊 Matriz de Decisión: Qué Mostrar Vs. Qué Ocultar

| Caso | Eventos | Bloques Generados | Status | Acción | Razón |
|------|---------|------------------|--------|--------|-------|
| **Jornada normal** | IN-OUT | 1 bloque | `NORMAL` | Mostrar | Datos completos y pares |
| **Break normal** | IN-OUT-IN-OUT | 2 bloques | `NORMAL` | Mostrar | Datos completos y pares |
| **Entrada sin salida** | IN | 0 bloques | `INCOMPLETE` | Alertar | Evento impar → estado indeterminado |
| **Salida sin entrada** | OUT | 0 bloques | `ERROR` | Alertar+Descarte | Imposible iniciar con OUT |
| **IN-IN-OUT** | IN-IN-OUT | 1 bloque (1 min) | `SUSPICIOUS` | Alertar+Revisar | Duplicación probable |
| **IN-OUT-OUT** | IN-OUT-OUT | 1 bloque + OUT huérfano | `SUSPICIOUS` | Alertar+Revisar | Duplicación probable |
| **Múltiples breakss** | IN-OUT-IN-OUT-IN | 1 bloque (ej 09-12) | `INCOMPLETE` | Alertar | Evento final impar |
| **Salida nocturna** | IN (día N) - OUT (día N+1) | N/A sin validación | `REVIEW_NEEDED` | Escalate | Requiere cruce de medianoche |

---

## 🚫 Límites Explícitos de FASE C

### No se resolverá en FASE C:
- ❌ Mapeo real `punch` ↔ `workstate` (requiere datos productivos)
- ❌ Reglas de negocio de breaks (HR debe definir política)
- ❌ Políticas de jornadas nocturnas (varía por contrato)
- ❌ Compensaciones o ajustes retroactivos
- ❌ Cambios a contratos de API

### Se asume en FASE C:
- ✅ Datos de ZKTeco crudos llegan sin validación  
- ✅ `punch` es index par/impar sin significado semántico
- ✅ Alternancia es mejor inferencia disponible hoy
- ✅ Timeline v1 es representación **mejor-esfuerzo**, no canónica
- ✅ Supervisión humana es requerida para casos ambiguos

---

## 📋 Criterio de Aceptación para FASE C

FASE C será viable si:

1. ✅ Documento es revisado y aprobado por arquitecto senior y PM
2. ✅ Se acuerda conjunto de reglas defensivas (D1, D2, D3, D4 o variantes)
3. ✅ Se actualiza contrato de API para reflejar nuevos status (`INCOMPLETE`, `SUSPICIOUS`, `OPEN`, etc.)
4. ✅ Se define umbrales (ej: "duplicación si Δt < 5 min")
5. ✅ Se obtienen muestras de datos reales de ZKTeco para validar hipótesis
6. ✅ Se planifica escalada de casos ambiguos a supervisión humana

---

## 🎬 Próximos Pasos

| Paso | Responsable | Duración | Bloqueo |
|------|-------------|----------|---------|
| 1. Revisión de este documento | Arquitecto Senior + PM | 1-2 días | ← AQUI |
| 2. Obtener sample datos reales de ZKTeco | DevOps / Producción | 2-5 días | Paso 1 ✓ |
| 3. Definir reglas defensivas concretas | Backend + HR | 1-2 días | Paso 2 ✓ |
| 4. Actualizar contrato de API | Backend + Frontend | 2-3 días | Paso 3 ✓ |
| 5. Implementar FASE C | Backend | 5-7 días | Paso 4 ✓ |
| 6. Validar con datos reales | QA + Backend | 2-3 días | Paso 5 ✓ |

---

## 📝 Notas

**Por qué no simplemente "arreglarlo"?**  
Porque no hay dato suficiente para "arreglar" sin asumir negocio. Meter código hoy sin reglas defensivas garantiza regresiones en producción cuando datos reales expongan nuevos patrones.

**¿Qué significa "mejor-esfuerzo"?**  
Timeline v1 hace lo mejor que puede con poca información. FASE C debe ser honesto sobre sus límites y fallar explícitamente (no silenciosamente).

**¿Por qué Timeline v1 no tiene esta documentación?**  
Porque fue prototipo rápido. FASE C es oportunidad para diseñar defensivamente desde el inicio.

---

## ✍️ Aprobaciones

| Rol | Nombre | Firma | Fecha |
|-----|--------|-------|-------|
| Arquitecto Senior | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ | \_\_\_\_\_\_\_ | |
| Product Manager | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ | \_\_\_\_\_\_\_ | |
| Tech Lead Backend | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ | \_\_\_\_\_\_\_ | |

---

**Documento generado:** 2026-02-03  
**Versión:** 1.0  
**Status:** DRAFT - Pending Review

