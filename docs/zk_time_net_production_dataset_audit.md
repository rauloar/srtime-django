# ZKTimeNet Production Dataset Audit

**Fecha de Análisis**: 2026-02-04  
**Archivo Fuente**: `caso_real_sql/ZKTimeNet.db.sql`  
**Rol**: Senior Data Analyst / Product Analyst  

---

## ⚠️ ADVERTENCIAS PREVIAS

- ✅ Este documento describe **datos reales de producción** tal como existen
- ❌ NO contiene propuestas de cambios al core ni a la lógica del sistema
- 📊 El objetivo es comprender la realidad operativa para validar/mejorar la UI

---

## 1. RESUMEN EJECUTIVO

### 1.1 Volumen de Datos

| Entidad | Cantidad | Observaciones |
|---------|----------|---------------|
| **Empresa** | 1 | Enerbom |
| **Departamentos** | 13 | Algunos nombrados como horarios (ej: "21 a 04", "05 a 14") |
| **Empleados** | 54 | Todos asociados a la misma empresa |
| **Turnos/Horarios** | 13 | Ciclos diarios y semanales |
| **Logs de asistencia (att_punches)** | 97,182 | Registros crudos del biométrico (2018-2024) |
| **Días procesados (att_day_details)** | 166,888 | Resúmenes diarios por empleado |

### 1.2 Período Temporal

- **Inicio**: 17 de mayo de 2018
- **Fin**: Enero 2024 (aproximadamente)
- **Duración**: ~6 años de operación continua

---

## 2. ENTIDADES CONCEPTUALES

### 2.1 Empresa

**Tabla**: `hr_company`

```
id: 1
nombre: "Enerbom"
campos vacíos: dirección, teléfono, email, logo
```

**Observación**: Configuración mínima. La empresa no tiene datos de contacto registrados.

---

### 2.2 Departamentos

**Tabla**: `hr_department`

Los departamentos muestran una mezcla de **áreas funcionales** y **franjas horarias**:

#### Áreas Funcionales Tradicionales:
- Administración (dept_code: 2)
- Moldeo (dept_code: 3)
- Rebaba (dept_code: 1)
- Horno (dept_code: 4)
- Mantenimiento (dept_code: 5)

#### "Departamentos" que son Horarios:
- 21 a 04 (dept_code: 6)
- 05 a 14 (dept_code: 7)
- 03 a 12 (dept_code: 8)
- 04 a 13 (dept_code: 9)
- 14 a 23 (dept_code: 10)
- 13 a 22 (dept_code: 11)
- 15 a 00 (dept_code: 13)
- 08 a 17 (dept_code: 14)

**Hallazgo Crítico para la UI**: La estructura refleja turnos rotativos de una planta industrial. Los nombres de departamento no son exclusivamente organizacionales.

**Relación con Turnos**: Cada departamento tiene asociado un `shift_id`, confirmando que el modelo mezcla estructura organizacional con esquemas de horario.

---

### 2.3 Empleados

**Tabla**: `hr_employee`

**Campos Poblados Consistentemente**:
- `emp_pin`: ID numérico del empleado (usado en el dispositivo biométrico)
- `emp_firstname`: Nombre
- `emp_lastname`: Apellido
- `emp_active`: Estado activo/inactivo
- `department_id`: Relacionado con hr_department

**Campos Vacíos en Producción**:
- SSN, dirección, email, teléfono de emergencia
- Foto (`emp_photo`)
- Tarjetas de acceso (`emp_cardNumber`)
- Tasas horarias (`emp_hourlyrate1`, `emp_hourlyrate2`)

**Observación para la UI**: La información personal es mínima. No mostrar campos opcionales vacíos reduciría ruido visual.

---

### 2.4 Turnos / Horarios

**Tabla**: `att_shift`

**Tipos de Ciclo**:
- `cycle_type = 1`: Ciclo diario (ej: Administración)
- `cycle_type = 0`: Ciclo semanal con rotación

**Turnos Activos** (13 en total):
1. Administración (ciclo diario, por defecto)
2. Rebaba, Moldeo, Mantenimiento, Horno (ciclos semanales)
3. Horarios específicos: 21 a 04, 05 a 14, 03 a 12, etc.

**Relación con `att_shift_details`**: Define los timetables específicos para cada día del ciclo.

**Observación**: La presencia de múltiples turnos con nombres de hora sugiere que el personal rota entre diferentes horarios según el día de la semana.

---

## 3. LOGS DE ASISTENCIA: ANÁLISIS DE DATOS REALES

### 3.1 Tabla `att_punches` (Log Crudo del Biométrico)

**Estructura**:
```
- id: Autoincremental
- employee_id: Referencia a hr_employee
- punch_time: Timestamp exacto del registro
- workstate: 0 = Check-In, 1 = Check-Out
- workcode: 0 en la mayoría de los casos
- terminal_id: Siempre 1 (un solo dispositivo)
- verifycode: NULL en todos los casos
- punch_type: '0' (tipo de verificación)
- operator: NULL (no hay ediciones manuales registradas)
- processed: 0 en la mayoría
```

### 3.2 Patrones Observados en los Logs

#### 3.2.1 Eventos Muy Cercanos en el Tiempo

**Ejemplo del empleado ID 1 el 2018-05-22**:

```
10:38:52 → workstate=0 (Check-In)
10:52:59 → workstate=1 (Check-Out)  [14 minutos después]
11:01:33 → workstate=1 (Check-Out)  [8 minutos después]
11:11:55 → workstate=0 (Check-In)   [10 minutos después]
11:21:00 → workstate=1 (Check-Out)  [9 minutos después]
11:30:11 → workstate=0 (Check-In)   [9 minutos después]
```

**Análisis**:
- Múltiples entradas y salidas en períodos muy cortos
- No hay lógica de "consolidación" visible en los datos originales
- Los eventos parecen ser registros legítimos (pausa, vuelta, nueva salida)

**Implicancia para la UI**:
- Mostrar **todos los punches** puede ser ruidoso
- Considerar agrupación visual por día
- Diferenciar claramente Check-In (workstate=0) vs Check-Out (workstate=1)

#### 3.2.2 Días Incompletos (Solo Check-In)

**Ejemplo del empleado ID 30 el 2022-05-17**:

```
2022-05-17 06:14:00 → Check-In
                     → [Sin Check-Out registrado]
```

**Frecuencia**: Común en la base de datos. Muchos registros en `att_day_details` tienen `checkin` pero `checkout=NULL`.

**Análisis**:
- Empleado fichó entrada pero no salida
- Puede ser un olvido, problema del dispositivo, o salida fuera del alcance del reloj

**Implicancia para la UI**:
- Mostrar claramente cuando falta el cierre
- No asumir automáticamente horas trabajadas sin checkout
- Opción para marcaje manual/corrección

#### 3.2.3 Días Sin Registros

**Ejemplo**: Empleado ID 26, día 2022-05-18 (miércoles):

```
att_day_details:
- checkin: NULL
- checkout: NULL
- worked: NULL
- remark: 'Wednesday'
```

**Observación**: Se crean registros en `att_day_details` incluso cuando no hay asistencia.

**Implicancia para la UI**:
- Distinguir "sin registros" de "ausencia confirmada"
- No confundir día vacío con día festivo o licencia

#### 3.2.4 Jornadas con Horarios Atípicos

**Ejemplo del empleado ID 29 el 2022-05-27**:

```
Check-In:  02:49:00 (2:49 AM)
Check-Out: 12:00:00 (12:00 PM)
Trabajado: 09:11:00 (9 horas 11 minutos)
```

**Análisis**: Entrada de madrugada confirmando turnos nocturnos reales.

**Implicancia para la UI**:
- No asumir horarios "normales" (9 a 17)
- Respetar visualizaciones de turnos nocturnos que cruzan medianoche

---

### 3.3 Tabla `att_day_details` (Resumen Diario Procesado)

**Estructura**:
```
- att_date: Fecha del día
- checkin: Primera entrada (timestamp)
- checkout: Última salida (timestamp)
- lunchin, lunchout: Casi siempre NULL en producción
- breakin, breakout: Casi siempre NULL
- worked: Intervalo calculado (formato TIME)
- timetable_id: Horario asignado
- employee_id: Empleado
```

**Observación Notable**:
- Los campos `lunchin` y `lunchout` están en NULL en **casi toda la base de datos**
- Los campos `roundedin`, `roundedout`, `roundworked` están en NULL

**Implicancia para la UI**:
- No mostrar campos de lunch/break si no se usan en la práctica
- Simplificar visualización a: entrada → salida → horas trabajadas

---

### 3.4 Tabla `att_day_summary` (Resumen con Códigos de Pago)

**Estructura**:
```
- att_date: Fecha
- employee_id: Empleado
- timetable_id: Horario esperado
- paycode_id: Código de categoría de horas
- pc_results: Minutos calculados para ese paycode
```

**Ejemplo Real** (Empleado 26, 2022-05-16):

| paycode_id | pc_results (minutos) | Equivalente |
|------------|----------------------|-------------|
| 1 | 605 | 10h 05min (Regular) |
| 2 | 540 | 9h 00min (¿Esperado?) |
| 3 | 65 | 1h 05min (Exceso/Extra) |
| 4-10 | 0 | Sin uso |
| 6 | 4 | 4 min (¿Penalización/Redondeo?) |

**Observación**: Este nivel de desagregación por `paycode` sugiere cálculos de nómina avanzados, pero no hay documentación en los datos sobre qué significa cada código.

**Implicancia para la UI**:
- Si se muestra `att_day_summary`, **etiquetar los paycodes** con descripciones legibles
- Caso contrario, ocultar esta tabla técnica y mostrar solo el total trabajado

---

## 4. CANTIDAD DE FICHADAS POR DÍA

### 4.1 Distribución Típica Observada

**Escenario Común** (jornada completa):
- 2 punches: 1 entrada + 1 salida

**Escenario con Pausas**:
- 4-6 punches: entrada → salida (pausa) → entrada → salida

**Escenario Extremo** (Empleado ID 1, 2018-05-22):
- **19 punches en un solo día**
- Alternancia continua entre Check-In y Check-Out

### 4.2 Implicancias para la UI

- No limitar visualización a 2 eventos por día
- Permitir scroll o tabla expandible para días con muchos registros
- Resaltar días anómalos (ej: más de 10 punches)

---

## 5. DUPLICADOS Y ANOMALÍAS

### 5.1 Eventos Duplicados

**Ejemplo del empleado ID 1, 2018-05-17**:

```
11:14:18 → workstate=0
11:14:27 → workstate=1  [9 segundos después]
```

**Análisis**:
- Dos eventos con el mismo empleado en menos de 10 segundos
- Posible doble lectura del biométrico o error del empleado

**Implicancia para la UI**:
- Mostrar timestamp completo (con segundos)
- Opción para "consolidar eventos duplicados" (sin eliminarlos automáticamente)

### 5.2 Secuencias Irregulares

**Ejemplo del empleado ID 1, 2018-05-22**:

```
10:52:59 → workstate=1 (Check-Out)
11:01:33 → workstate=1 (Check-Out)  [Dos salidas consecutivas sin entrada]
```

**Análisis**:
- No hay validación estricta de secuencia entrada-salida en el dispositivo
- Puede haber salidas consecutivas o entradas consecutivas

**Implicancia para la UI**:
- No asumir alternancia perfecta
- Resaltar en color diferente si hay inconsistencias
- Permitir corrección manual desde la interfaz

---

## 6. EMPLEADOS SIN REGISTROS

**Hallazgo**: De los 54 empleados registrados, **no todos tienen registros de asistencia activos**.

**Posibles Razones**:
- Empleados dados de baja (`emp_active=0`)
- Personal administrativo sin obligación de fichar
- Empleados nuevos sin registros históricos

**Implicancia para la UI**:
- Filtrar empleados activos por defecto
- Mostrar indicador si un empleado activo no tiene registros en X días
- No mostrar empleados inactivos en reportes de asistencia actual

---

## 7. RELACIÓN ENTRE TABLAS CLAVE

```
hr_company (Enerbom)
    ↓
hr_department (13 departamentos/turnos)
    ↓
hr_employee (54 empleados)
    ↓
att_employee_shift (asignación de turno)
    ↓           ↓
att_punches     att_day_details     att_day_summary
(logs crudos)   (resumen diario)    (cálculo nómina)
```

**Observación**:
- `att_punches` es la **fuente de verdad**
- `att_day_details` es un **resumen consolidado** (primer check-in, último check-out)
- `att_day_summary` es un **agregado con lógica de negocio** (paycodes, horas regulares vs extras)

---

## 8. CAMPOS ÚTILES PARA MOSTRAR EN LA UI

### 8.1 Nivel Empleado

✅ **Mostrar**:
- `emp_pin` (ID biométrico)
- `emp_firstname + emp_lastname` (nombre completo)
- `department_id` → dept_name (departamento/turno)
- `emp_active` (estado activo/inactivo)

❌ **NO Mostrar** (vacíos en producción):
- SSN, email, teléfono, dirección
- Foto (NULL en todos los casos)
- Tasas horarias (no usadas)

### 8.2 Nivel Asistencia Diaria

✅ **Mostrar**:
- Fecha (`att_date`)
- Primera entrada (`checkin`)
- Última salida (`checkout`)
- Horas trabajadas (`worked`)
- Nombre del día (`remark` → "Monday", "Tuesday", etc.)

❌ **NO Mostrar** (casi siempre NULL):
- `lunchin`, `lunchout`
- `breakin`, `breakout`
- `roundedin`, `roundedout`

### 8.3 Nivel Log Crudo (att_punches)

✅ **Mostrar**:
- Timestamp completo con **segundos**
- Estado: "Entrada" (workstate=0) / "Salida" (workstate=1)
- Terminal ID (siempre 1, informativo)

⚠️ **Considerar**:
- Agrupar visualmente punches del mismo día
- Resaltar inconsistencias (dos entradas seguidas, etc.)

---

## 9. CAMPOS QUE CONFUNDEN

### 9.1 `department_id` en hr_employee

**Problema**: No todos los nombres de departamento son áreas funcionales. Algunos son horarios ("21 a 04").

**Solución UI**:
- Renombrar label a "Turno/Área"
- Mostrar tanto el `dept_name` como el `shift_name` asociado

### 9.2 `workcode` y `workstate` en att_punches

**Problema**: Nombres técnicos sin contexto.

**Solución UI**:
- Traducir `workstate` a:
  - 0 → "Entrada ↓"
  - 1 → "Salida ↑"
- Ignorar `workcode` si siempre es 0

### 9.3 `pc_results` en att_day_summary

**Problema**: Valores en minutos sin descripción del paycode.

**Solución UI**:
- Si se muestra, convertir a "hh:mm"
- Etiquetar cada paycode con su significado (requiere diccionario de negocio)

---

## 10. ESTADOS RECOMENDADOS PARA EXPRESAR COMO TEXTO

### 10.1 Estado de Día

Basado en `att_day_details`:

| Condición | Estado Sugerido |
|-----------|-----------------|
| `checkin != NULL AND checkout != NULL` | ✅ "Jornada Completa" |
| `checkin != NULL AND checkout = NULL` | ⚠️ "Pendiente de Salida" |
| `checkin = NULL AND checkout = NULL` | ⏸️ "Sin Registros" |
| `worked < expected` | ⚠️ "Jornada Incompleta" |
| `worked > expected` | 🔼 "Horas Extra" |

### 10.2 Estado de Empleado

| Condición | Estado Sugerido |
|-----------|-----------------|
| `emp_active = 1` | ✅ "Activo" |
| `emp_active = 0` | 🚫 "Inactivo/Baja" |
| Sin punches en los últimos 30 días (emp_active=1) | ⚠️ "Sin Actividad Reciente" |

### 10.3 Estado de Secuencia de Punches

| Condición | Estado Sugerido |
|-----------|-----------------|
| Alternancia correcta (0,1,0,1...) | ✅ "Normal" |
| Dos entradas seguidas (0,0) | ⚠️ "Inconsistencia: Doble Entrada" |
| Dos salidas seguidas (1,1) | ⚠️ "Inconsistencia: Doble Salida" |
| Diferencia < 1 minuto entre eventos | 🔄 "Posible Duplicado" |

---

## 11. CONCLUSIONES PARA VALIDACIÓN DE UI

### 11.1 Prioridades de Visualización

1. **Vista de Lista de Empleados**
   - Mostrar: PIN, Nombre, Turno/Área, Estado
   - Filtrar por defecto solo activos
   - Indicar si no hay registros recientes

2. **Vista de Asistencia Diaria**
   - Mostrar: Fecha, Primera Entrada, Última Salida, Horas Trabajadas
   - Estado visual (completo/pendiente/sin registros)
   - NO mostrar campos lunch/break si no se usan

3. **Vista de Detalle de Punches**
   - Mostrar todos los eventos del día
   - Timestamp completo (con segundos)
   - Indicador visual: Entrada (↓) / Salida (↑)
   - Resaltar inconsistencias

### 11.2 Funcionalidades Necesarias

- ✅ Filtro por rango de fechas
- ✅ Búsqueda por nombre/PIN de empleado
- ✅ Filtro por departamento/turno
- ✅ Exportación a CSV/Excel
- ⚠️ Opción para consolidar/editar punches duplicados
- ⚠️ Marcaje manual para días incompletos

### 11.3 Lo Que NO Debe Hacer la UI (Según los Datos)

- ❌ Asumir horarios fijos (9-17)
- ❌ Validar estrictamente secuencia entrada-salida (los datos muestran inconsistencias)
- ❌ Calcular automáticamente horas si falta checkout
- ❌ Mostrar campos que siempre están vacíos (lunch, break, tasas horarias)
- ❌ Rechazar registros de madrugada (turnos nocturnos son reales)

---

## 12. DATOS ESTADÍSTICOS FINALES

| Métrica | Valor |
|---------|-------|
| **Total de punches** | 97,182 |
| **Días procesados** | 166,888 |
| **Empleados registrados** | 54 |
| **Período de datos** | 2018-05-17 a 2024-01-02 (~6 años) |
| **Promedio punches/día/empleado** | ~2-4 (con extremos de 10+) |
| **Días sin registros** | Frecuente (NULL en checkin/checkout) |
| **Inconsistencias de secuencia** | Presentes (ej: doble entrada, doble salida) |
| **Campos lunch/break usados** | <1% (casi todos NULL) |

---

## 13. RECOMENDACIONES FINALES

### Para el Equipo de UI/Frontend:

1. **Simplicidad Visual**
   - Ocultar campos que no se usan en producción
   - Priorizar entrada, salida y horas trabajadas

2. **Manejo de Inconsistencias**
   - NO asumir perfección en los datos
   - Resaltar anomalías sin bloquear la visualización

3. **Contexto de Negocio**
   - Reconocer que "departamento" incluye turnos horarios
   - Respetar horarios no tradicionales (madrugada, medianoche)

4. **Feedback Visual**
   - Usar colores/iconos para estados (completo ✅, pendiente ⚠️, sin datos ⏸️)
   - Diferenciar claramente entrada (workstate=0) de salida (workstate=1)

### Para Validación con Usuarios:

- Confirmar significado de los paycodes (att_day_summary)
- Validar si las inconsistencias son errores reales o casos de uso legítimos
- Determinar si se debe permitir edición manual de registros

---

**Documento Generado**: 2026-02-04  
**Analista**: GitHub Copilot (Senior Data Analyst Role)  
**Propósito**: Auditoría descriptiva del dataset para validación y mejora de la UI  
**Alcance**: Descriptivo, NO prescriptivo

