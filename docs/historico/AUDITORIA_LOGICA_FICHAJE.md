# 🔍 AUDITORÍA TÉCNICA: LÓGICA DE FICHAJE EXISTENTE

**Fecha:** 2026-02-02  
**Baseline:** c666fb7 (v0.1-dev-baseline)  
**Propósito:** Mapear estado real de implementación de horario fijo vs flexible

---

## 📋 ALCANCE

Revisión **SOLO de código existente** sin propuestas de solución.

### Qué se auditó:
- Backend: Modelos, servicios, views de asistencia
- Frontend: Componentes de Day View, Timeline, Explanation
- Integración: Consistencia entre backend y frontend

### Qué NO se auditó:
- Auth, permisos, forense, auditorías, snapshots
- Scripts externos o migration data
- Código comentado o muerto deliberadamente

---

## [BACKEND] `core/models.py` - Modelo AttendanceLog

### Qué existe:
```python
class AttendanceLog(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=50, db_index=True)
    timestamp = models.DateTimeField(db_index=True)
    status = models.IntegerField()
    punch = models.IntegerField()
    
    # Detalles extendidos
    verify_mode = models.IntegerField(null=True, blank=True)
    workstate = models.IntegerField(null=True, blank=True)
    workcode = models.IntegerField(null=True, blank=True)
    punch_source = models.CharField(max_length=50, null=True, blank=True)
    raw_json = models.JSONField(null=True, blank=True)
```

### Qué hace hoy:
- Almacena eventos crudos del dispositivo ZKTeco
- Captura campos: `timestamp`, `punch`, `status`, `workstate`, `workcode`, `punch_source`
- Preserva JSON original sin procesar

### Para qué parece diseñado:
- Captura completa de eventos con metadata del dispositivo
- Potencial para distinguir IN vs OUT basado en `punch` y `workstate`
- Raw JSON sugiere análisis futuro de payloads complejos

### Estado real: 
🔴 **MUERTO**
- Los campos `punch`, `workstate`, `workcode` existen pero **nunca se consultan en cálculos**
- Raw JSON nunca se procesa
- El sistema actual usa solo `timestamp` (ignorando metadata de evento)

---

## [BACKEND] `core/models.py` - Modelo Timetable

### Qué existe:
```python
class Timetable(models.Model):
    name = models.CharField(max_length=100)
    
    # Horario (Fijo)
    on_duty_time = models.CharField(max_length=10)        # "09:00"
    off_duty_time = models.CharField(max_length=10)       # "18:00"
    
    # Tolerancias (Fijo)
    late_allow_minutes = models.IntegerField(default=0)
    early_leave_allow_minutes = models.IntegerField(default=0)
    
    # Ventanas de entrada/salida (Ambos)
    check_in_start = models.CharField(max_length=10, null=True, blank=True)
    check_in_end = models.CharField(max_length=10, null=True, blank=True)
    check_out_start = models.CharField(max_length=10, null=True, blank=True)
    check_out_end = models.CharField(max_length=10, null=True, blank=True)
    
    # Config general
    break_minutes = models.IntegerField(default=0)
    required_minutes = models.IntegerField(default=0)
    
    # 🔑 SELECTOR FIJO vs FLEXIBLE
    is_flexible = models.BooleanField(default=False)
```

### Qué hace hoy:
- Define reglas de horario completas
- Soporte dual: horarios fijos (`on_duty_time`/`off_duty_time`) vs flexibles (`check_in_start/end` + `check_out_start/end`)
- Tolerancias para llegar tarde / salir temprano

### Para qué parece diseñado:
- Distinguir entre dos modelos de trabajo opuestos
- Soportar cálculos diferentes según `is_flexible`
- Validar ventanas de entrada/salida

### Estado real:
🟡 **PARCIAL**
- Estructura completa y bien diseñada
- Campo `is_flexible` existe pero **nunca se consulta en cálculos actuales**
- Tolerancias definidas pero no aplicadas en `get_simple_day_view()`

---

## [BACKEND] `core/services/flexible_engine.py`

### Qué existe:
Motor completo de cálculo para horario flexible (240 líneas, 7 fases):

```python
def calculate_flexible_day(
    employee_id: int,
    target_date: date,
    punches: List[Punch],
    policy: FlexPolicy,
    holidays: List[date],
    has_leave: bool,
) -> DailyCalculationResult:
    """
    Orquesta 7 fases:
    1. Validación
    2. Parsing (punches → blocks)
    3. Análisis estructural (gaps, splits)
    4. Cálculo base (worked, breaks, net)
    5. Clasificación legal (overtime, night)
    6. Determinación de status
    7. Evaluación forense
    """
```

Importa modelos de dominio:
- `Punch`, `FlexPolicy`, `FlexStatus`
- Funciones especializadas: `validate_punches()`, `build_work_blocks()`, `compute_night_minutes()`

### Qué hace hoy:
- Calcula jornada flexible basada en punch_in/punch_out explícitos
- Computa: bloques de trabajo, breaks, diferencias, tiempo nocturno, etc.
- Genera resultado forense (confidence, warnings)

### Para qué parece diseñado:
- Calcular asistencia flexible sin inferencias de horario fijo
- Capturar eventos seleccionados por usuario/botones en terminal
- Análisis completo con clasificación legal

### Estado real:
🟢 **ACTIVO** pero 🔴 **NO USADO**
- Código está completo y bien estructurado
- **Nunca se llama desde ningún view o endpoint actual**
- Ningún request Django alcanza esta función

---

## [BACKEND] `core/services/attendance_engine.py`

### Qué existe:
Lógica para distinguir horario fijo vs flexible (405 líneas):

```python
def _build_context(tt: models.Timetable, target_date: date, source: str) -> DayContext:
    # Rama 1: FLEXIBLE
    if tt.is_flexible:
        t_in_start = parse_time(tt.check_in_start or "00:00")
        t_out_end = parse_time(tt.check_out_end or "23:59")
        dt_search_start = combine(target_date, t_in_start)
        dt_search_end = combine(target_date, t_out_end)
        # → Buscar logs en rango amplio [00:00 - 23:59]
        return DayContext(
            is_valid=True,
            on_duty_dt=dt_search_start,
            off_duty_dt=dt_search_end,
            search_start=dt_search_start,
            search_end=dt_search_end,
        )
    
    # Rama 2: FIXED
    t_on = parse_time(tt.on_duty_time)      # "09:00"
    t_off = parse_time(tt.off_duty_time)    # "18:00"
    dt_on = combine(target_date, t_on)
    dt_off = combine(target_date, t_off)
    # → Buscar logs en rango específico [09:00 - 18:00]
    return DayContext(...)
```

### Qué hace hoy:
- Consulta `Timetable.is_flexible`
- Determina rango de búsqueda según tipo
- Crea `DayContext` con metadata del día

### Para qué parece diseñado:
- Preparar contexto inteligente según tipo de horario
- Búsquedas de logs eficientes (diferentes rangos)
- Base para cálculos posteriores que respeten horarios

### Estado real:
🟡 **PARCIAL**
- Estructura existe y distingue casos
- **No se llama desde ningún view actual**
- Lógica de contexto está "dormida"

---

## [BACKEND] `core/views_attendance.py` - Función `get_simple_day_view`

### Qué existe:
```python
@api_view(['GET'])
def get_simple_day_view(request):
    """GET /api/v1/attendance/day/?employee_id=1&date=2026-02-02"""
    
    # 1. Obtener empleado
    emp = models.Employee.objects.get(id=employee_id)
    
    # 2. Consultar logs (SIN considerar Timetable)
    logs_qs = models.AttendanceLog.objects.filter(
        user_id=str(emp.user_id),
        timestamp__date=target_date
    ).order_by('timestamp')
    
    # 3. Asignar IN/OUT por ALTERNANCIA (index % 2)
    logs_data = []
    for log in logs_qs:
        logs_data.append({
            "type": "IN" if len(logs_data) % 2 == 0 else "OUT",  # 🔴 NAIVE
            "time": log.timestamp.strftime("%H:%M")
        })
    
    # 4. Calcular status por CANTIDAD de logs (SIN horario)
    if len(logs_qs) == 0:
        status = "Absent"
    elif len(logs_qs) == 1:
        status = "Partial"
    else:
        status = "Normal"
        # Horas = diferencia entre primer y último log
        worked_minutes = int((last - first).total_seconds() / 60)
    
    return Response({
        "employee_id": employee_id,
        "employee_name": emp_name,
        "date": date_str,
        "status": status,
        "worked_minutes": worked_minutes,
        "logs": logs_data
    })
```

### Qué hace hoy:
- ✅ Obtiene logs para un empleado en una fecha
- ✅ Ordena cronológicamente
- ✅ Retorna estructura simple: IN/OUT + tiempo

### Para qué parece diseñado:
- Endpoint "mínimo viable" que funciona sin lógica de negocio compleja

### ⚠️ CÓMO CALCULA (HOY):

**IN/OUT:**
```
Log 0 → "IN"  (0 % 2 == 0)
Log 1 → "OUT" (1 % 2 == 1)
Log 2 → "IN"  (2 % 2 == 0)
Log 3 → "OUT" (3 % 2 == 1)
```
→ Alternancia simple, sin validación

**Horas trabajadas:**
```
worked_minutes = (timestamp_última - timestamp_primera) / 60
```
→ Diferencia bruta, sin descontar breaks

**Status:**
```
0 logs    → "Absent"
1 log     → "Partial"
2+ logs   → "Normal" (SIEMPRE, sin importar horario)
```

### Estado real:
🟢 **ACTIVO** pero 🔴 **NAIVE**
- Funciona sin crashes
- **No consulta `Timetable` en absoluto**
- No distingue horario fijo de flexible
- No aplica tolerancias
- No calcula overtime
- Ignora campos `punch`, `workstate`, `workcode`

---

## [BACKEND] `core/views_stubs.py`

### Qué existe:
```python
@api_view(['GET'])
@permission_classes([AllowAny])
def stub_timeline(request, employee_id, date):
    """Stub for /attendance/{id}/timeline/{date}/"""
    return Response({"blocks": []})

@api_view(['GET'])
@permission_classes([AllowAny])
def stub_explanation(request, employee_id, date):
    """Stub for /attendance/{id}/explanation/{date}/"""
    return Response({
        "summary": "Data not available in DEV mode",
        "anomalies": [],
        "recommendations": []
    })
```

### Qué hace hoy:
- `stub_timeline`: retorna lista vacía
- `stub_explanation`: retorna objeto genérico

### Estado real:
🔴 **MUERTO**
- Mock puro, sin consultas a BD
- Registrado en URLs pero no implementado
- Existen para que frontend no crash (prevent 404)

---

## [FRONTEND] `frontend/src/api.ts` - Interfaces

### Qué espera Timeline:
```typescript
interface TimelineBlock {
    type: string;              // "WORK", "BREAK", etc.
    start_time: string;        // "08:30"
    end_time: string;          // "17:45"
    duration_minutes: number;  // 555
}

interface TimelineData {
    blocks: TimelineBlock[];
}

export const getTimeline = async (employeeId: string, date: string) =>
    (await api.get<TimelineData>(`/attendance/${employeeId}/timeline/${date}/`)).data;
```

### Qué espera Explanation:
```typescript
interface ExplanationData {
    summary: string;        // Análisis en texto
    anomalies: string[];    // ["Gap > 2h", "Sin salida"]
    recommendations: string[]; // ["Verificar dispositivo"]
}

export const getExplanation = async (employeeId: string, date: string) =>
    (await api.get<ExplanationData>(`/attendance/${employeeId}/explanation/${date}/`)).data;
```

### Estado real:
🟢 **ACTIVO** - Interfaces bien definidas
- Types correctos y documentados
- Pero endpoints retornan mocks vacíos

---

## [FRONTEND] `frontend/src/components/asistencia/DayTimeline.tsx`

### Qué asume:
```typescript
interface TimelineBlock {
    type: string;              // "WORK", "BREAK", "GAP_ANOMALY", etc.
    start_time: string;
    end_time: string;
    duration_minutes: number;
}

const getBlockStyle = (type: string) => {
    const styles = {
        'WORK': { bg: '#4caf50', label: 'Trabajo' },
        'BREAK': { bg: '#2196f3', label: 'Descanso' },
        'GAP_ANOMALY': { bg: '#ff9800', label: 'Gap Anómalo' },
        'SCHEDULE_BLOCK': { bg: '#e0e0e0', label: 'Horario' },
    };
};
```

### Qué hace hoy:
```typescript
const result = await getTimeline(employeeId, date);
setBlocks(result.blocks || []);

if (blocks.length === 0) {
    return <div>No hay bloques de tiempo para mostrar</div>;
}
```

### Dependencias implícitas:
- Asume que backend calcula bloques (no solo IN/OUT)
- Espera estructura con `type`, `start_time`, `end_time`
- No maneja "simple IN/OUT"

### Estado real:
🟢 **ACTIVO** pero 🔴 **SIN DATOS**
- Código correcto para renderear bloques
- Recibe `[]` del stub, renderea "sin datos"

---

## [FRONTEND] `frontend/src/pages/asistencia/DayViewPage.tsx`

### Qué asume:
```typescript
interface DayViewData {
    employee_id: string;
    employee_name: string;
    date: string;
    status: string;
    worked_minutes: number;
    logs: Array<{ type: string; time: string }>;
}

// Llama a:
const response = await api.get(`/attendance/day/?employee_id=${employeeId}&date=${date}`);
setData(response.data);
```

### Qué recibe hoy:
```json
{
  "employee_id": "1",
  "employee_name": "Juan",
  "date": "2026-02-02",
  "status": "Normal",
  "worked_minutes": 480,
  "logs": [
    { "type": "IN", "time": "08:30" },
    { "type": "OUT", "time": "17:30" }
  ]
}
```

### Qué renderea:
- Header con nombre del empleado, fecha, status
- Componentes hijos: `DayTimeline`, `DayExplanation`, `DayPunchList`
- Controles de navegación

### Estado real:
🟢 **ACTIVO** - Funciona correctamente
- Obtiene datos del stub
- Renderea interfaz sin crashes

---

## [FRONTEND] `frontend/src/components/asistencia/DayExplanation.tsx`

### Qué asume:
```typescript
interface ExplanationData {
    summary: string;
    anomalies: string[];
    recommendations: string[];
}

const data = await getExplanation(employeeId, date);
if (!data || !data.summary) {
    return null;  // Silently hide
}
```

### Qué renderea:
- `summary`: información general
- `anomalies`: lista de problemas detectados
- `recommendations`: sugerencias de acción

### Dependencias implícitas:
- Asume que backend entiende de horarios, políticas, reglas
- Solo renderiza, no calcula nada
- Falla silenciosamente si no hay datos

### Estado real:
🟢 **ACTIVO** pero 🔴 **SIN DATOS**
- Código correcto para renderear
- Stub retorna mock, componente se oculta silenciosamente

---

## 📊 TABLA DE SÍNTESIS

| Componente | Existe | Se Usa | Estado | Observación |
|-----------|--------|--------|--------|------------|
| `AttendanceLog` (modelo) | ✅ | ✅ | 🟢 ACTIVO | Pero sin usar `punch`, `workstate` |
| `Timetable.is_flexible` | ✅ | ❌ | 🔴 MUERTO | Nunca consultado en cálculos |
| `flexible_engine.py` | ✅ | ❌ | 🔴 MUERTO | Código completo pero no se llama |
| `attendance_engine.py` | ✅ | ❌ | 🔴 MUERTO | Contexto inteligente ignorado |
| `get_simple_day_view()` | ✅ | ✅ | 🟢 ACTIVO | NAIVE: alternancia par/impar |
| `stub_timeline()` | ✅ | ✅ | 🟡 STUB | Retorna `[]` |
| `stub_explanation()` | ✅ | ✅ | 🟡 STUB | Retorna mock genérico |
| `DayViewPage` | ✅ | ✅ | 🟢 ACTIVO | Funciona con datos mínimos |
| `DayTimeline` | ✅ | ✅ | 🟢 ACTIVO | Sin datos que renderear |
| `DayExplanation` | ✅ | ✅ | 🟢 ACTIVO | Sin datos, se oculta |

---

## ❓ CONTRADICCIONES BACKEND ↔ FRONTEND

### 1️⃣ Timeline: Formato desacoplado

**Backend (stub):**
```json
{ "blocks": [] }
```

**Frontend (expectativa):**
```typescript
interface TimelineBlock {
    type: string;          // "WORK", "BREAK", "GAP_ANOMALY"
    start_time: string;
    end_time: string;
    duration_minutes: number;
}
```

**Realidad:**
- Frontend espera bloques complejos (trabajo, breaks, gaps)
- Backend retorna lista vacía
- Frontend renderea "sin datos"

**⚠️ Contradicción:**
Arquitectura de frontend diseñada para "análisis de bloques" pero endpoint actual usa "IN/OUT simple".

---

### 2️⃣ Explicación: Opcional pero incompleta

**Backend (stub):**
```json
{
  "summary": "Data not available in DEV mode",
  "anomalies": [],
  "recommendations": []
}
```

**Frontend (expectativa):**
```typescript
interface ExplanationData {
    summary: string;
    anomalies: string[];
    recommendations: string[];
}
```

**Realidad:**
- Interfaz lista para análisis complejo (anomalías, recomendaciones)
- Backend retorna stub con texto genérico
- Frontend silenciosamente oculta componente

**⚠️ Contradicción:**
Interfaz sugiere análisis profundo, pero backend no implementa nada.

---

### 3️⃣ Horarios: Existen pero no se usan

**Infraestructura disponible:**
- `Timetable` con `is_flexible`, `on_duty_time`, tolerancias
- Motor `flexible_engine.py` completo
- Lógica de contexto en `attendance_engine.py`

**Uso real:**
- `get_simple_day_view()` **no consulta `Timetable` en absoluto**
- Status se calcula solo por cantidad de logs
- SIN validar si es horario fijo o flexible
- SIN aplicar tolerancias

**⚠️ Contradicción:**
Sistema tiene infraestructura completa para horarios, pero cálculo ignora todo.

---

### 4️⃣ Punch metadata: Existe pero muere sin usar

**Modelo `AttendanceLog`:**
- Campo `punch: IntegerField`
- Campo `workstate: IntegerField`
- Campo `punch_source: CharField`

**Uso real:**
- Nunca consultados
- Nunca procesados
- Nunca validados

**⚠️ Contradicción:**
Dispositivo ZKTeco envía metadata de evento (punch type, work state), pero backend lo ignora completamente.

---

## 🎯 CONCLUSIÓN: ESTADO REAL HOY

### ✅ Qué FUNCIONA ACTUALMENTE:
1. `get_simple_day_view()` → retorna IN/OUT alternado
2. `DayViewPage` → renderea datos recibidos sin crashes
3. `DayTimeline` → renderea estructura (aunque vacía)
4. `DayExplanation` → se oculta silenciosamente

### ❌ Qué ESTÁ DORMIDO (existe pero no se usa):
1. `flexible_engine.py` → motor completo sin llamadas
2. `attendance_engine.py` → contexto inteligente ignorado
3. `Timetable.is_flexible` → nunca consultado
4. `AttendanceLog.punch` → nunca procesado
5. `AttendanceLog.workstate` → nunca procesado

### 🤯 HONESTAMENTE:

**El sistema tiene lógica para horario fijo y flexible, pero NADA está conectado.**

| Aspecto | ¿Existe? | ¿Se usa? | Conclusión |
|---------|---------|---------|-----------|
| Modelo `is_flexible` | ✅ | ❌ | Ignorado |
| Motor flexible | ✅ | ❌ | Dormido |
| Lógica de contexto | ✅ | ❌ | No se llama |
| Cálculo actual | ✅ | ✅ | NAIVE (sin horarios) |

**Hoy funciona porque usa reglas NAIVE (alternancia par/impar) que no requieren horarios.**

---

## 📌 RECOMENDACIÓN PARA PRÓXIMO PASO

Para implementar timeline y explanation reales:

1. ❓ **Decidir:** ¿Usar almacenado `punch`/`workstate` o alternancia?
2. ❓ **Decidir:** ¿Consultar `Timetable` o ignorar horarios?
3. ❓ **Decidir:** ¿Activar `flexible_engine.py` o escribir lógica nueva simple?

El código necesario **ya existe**, solo está desconectado.

---

**Fin del documento.**
