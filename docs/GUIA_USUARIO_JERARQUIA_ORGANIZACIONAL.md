# 🏢 Guía del Usuario: Sistema de Organización y Control de Asistencia
## SRTimeWeb - Manual de Configuración

---

## 📖 ¿Qué es este documento?

Esta guía le ayudará a entender cómo funciona el sistema de control de asistencia de su empresa, cómo configurarlo correctamente y qué sucede cuando realiza cambios.

**No necesita conocimientos técnicos para seguir esta guía.**

---

## 🎯 1. CONCEPTOS BÁSICOS

### ¿Cómo funciona el sistema?

El sistema organiza su empresa en **5 niveles** que trabajan juntos:

```
┌─────────────────────────────────────────────────────────┐
│                    🏢 SU EMPRESA                        │
│                                                         │
│  Ejemplo: "Acme Corporation"                           │
└─────────────────────────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────┐
│                 🏛️ DEPARTAMENTOS                        │
│                                                         │
│  División de su empresa en áreas                       │
│  Ejemplo: Ventas, Producción, Administración          │
└─────────────────────────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   ⏰ HORARIOS                           │
│                                                         │
│  Horarios específicos con entradas y salidas           │
│  Ejemplo: 08:00-17:00, 14:00-22:00                    │
└─────────────────────────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    🔄 TURNOS                            │
│                                                         │
│  Patrones de trabajo que agrupan horarios              │
│  Ejemplo: Turno Mañana, Turno Tarde, Turno Rotativo   │
└─────────────────────────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   👤 EMPLEADOS                          │
│                                                         │
│  Su personal que marca entrada/salida                  │
│  Ejemplo: Juan Pérez (EMP001), María López (EMP002)   │
└─────────────────────────────────────────────────────────┘
```

### Analogía Simple

Piense en su empresa como un edificio:

- **Empresa** = El edificio completo
- **Departamentos** = Los pisos del edificio
- **Horarios** = Las franjas horarias disponibles (08:00-17:00, 14:00-22:00)
- **Turnos** = Los patrones semanales (qué horario cada día de la semana)
- **Empleados** = Las personas que trabajan en cada piso con sus turnos asignados

---

## 📝 2. CONFIGURACIÓN PASO A PASO

### Paso 1: Departamentos

**¿Qué son?**
Las áreas o secciones de su empresa.

**¿Cómo crear uno?**

1. Vaya a **RRHH** → **Departamentos**
2. Click en **+ Nuevo Departamento**
3. Complete:
   - **Nombre:** Nombre del departamento (ejemplo: "Ventas")
   - **Código:** Código corto (ejemplo: "VTA")
4. Click en **Guardar**

**Ejemplo práctico:**
```
┌─────────────────────────────────┐
│ Ventas (VTA)                    │
├─────────────────────────────────┤
│ Producción (PROD)               │
├─────────────────────────────────┤
│ Administración (ADM)            │
├─────────────────────────────────┤
│ Recursos Humanos (RRHH)         │
└─────────────────────────────────┘
```

---

### Paso 2: Horarios (Timetables)

**¿Qué son?**
Las franjas horarias específicas con hora de entrada y salida.

**¿Cómo crear uno?**

1. Vaya a **RRHH** → **Horarios**
2. Click en **+ Nuevo Horario**
3. Complete:
   - **Nombre:** Descriptivo (ejemplo: "Administrativo 08:00-17:00")
   - **Hora Entrada:** 08:00
   - **Hora Salida:** 17:00
   - **Tolerancia Llegada Tarde:** 15 minutos (opcional)
   - **Tolerancia Salida Temprano:** 5 minutos (opcional)
   - **Minutos Descanso:** 60 minutos (para almuerzo)
4. Click en **Guardar**

**Ejemplo práctico:**
```
Horario: "Administrativo"
├─ Entrada: 08:00 AM
├─ Salida:  05:00 PM (17:00)
├─ Tolerancia: +15 min tarde / -5 min temprano
└─ Descanso: 60 min (almuerzo)

➡️ Significado:
   - El empleado puede marcar hasta 08:15 sin penalización
   - Debe salir después de 16:55 para no contar salida temprana
   - Trabajó: 9 horas - 1 hora almuerzo = 8 horas efectivas
```

**Tipos de Horarios:**

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| **Fijo** | Entrada/Salida definidas | 08:00-17:00 |
| **Flexible** | Solo cuenta horas totales trabajadas | Trabajar 8 horas en cualquier momento |

---

### Paso 3: Turnos (Shifts)

**¿Qué son?**
Patrones de trabajo que agrupan horarios por día de la semana.

**¿Cómo crear uno?**

1. Vaya a **RRHH** → **Turnos**
2. Click en **+ Nuevo Turno**
3. Complete:
   - **Nombre:** Descriptivo (ejemplo: "Turno Administrativo")
   - **Tipo de Ciclo:** Semanal (Lunes-Domingo)
4. Click en **Guardar**
5. **Asignar Horarios por Día:**
   - Click en el turno creado
   - Para cada día de la semana:
     - Seleccione el día (Lunes, Martes, etc.)
     - Seleccione el horario a usar
     - Click en **Agregar**

**Ejemplo práctico: Turno Administrativo (5 días)**

```
Turno: "Administrativo"
┌─────────┬──────────────────┬────────────┐
│ Día     │ Horario          │ Estado     │
├─────────┼──────────────────┼────────────┤
│ Lunes   │ 08:00-17:00      │ ✅ Trabaja │
│ Martes  │ 08:00-17:00      │ ✅ Trabaja │
│ Miércoles│ 08:00-17:00     │ ✅ Trabaja │
│ Jueves  │ 08:00-17:00      │ ✅ Trabaja │
│ Viernes │ 08:00-17:00      │ ✅ Trabaja │
│ Sábado  │ (sin horario)    │ 🏖️ Descanso│
│ Domingo │ (sin horario)    │ 🏖️ Descanso│
└─────────┴──────────────────┴────────────┘
```

**Ejemplo práctico: Turno Rotativo (6x1)**

```
Turno: "Producción 6x1"
┌─────────┬──────────────────┬────────────┐
│ Día     │ Horario          │ Estado     │
├─────────┼──────────────────┼────────────┤
│ Lunes   │ 06:00-14:00      │ ✅ Trabaja │
│ Martes  │ 06:00-14:00      │ ✅ Trabaja │
│ Miércoles│ 06:00-14:00     │ ✅ Trabaja │
│ Jueves  │ 06:00-14:00      │ ✅ Trabaja │
│ Viernes │ 06:00-14:00      │ ✅ Trabaja │
│ Sábado  │ 06:00-14:00      │ ✅ Trabaja │
│ Domingo │ (sin horario)    │ 🏖️ Descanso│
└─────────┴──────────────────┴────────────┘
```

---

### Paso 4: Empleados

**¿Qué hacer?**

1. Vaya a **RRHH** → **Empleados**
2. Click en **+ Nuevo Empleado**
3. Complete:
   - **ID Usuario:** Código único (ejemplo: "EMP001")
   - **Nombre Completo:** Nombre del empleado
   - **Departamento:** Seleccione el departamento
   - **Activo:** ✅ (marcar si está trabajando actualmente)
4. Click en **Guardar**

**Importante:**
- El **ID Usuario** debe coincidir con el registrado en el lector biométrico
- Sin este código, el sistema no podrá vincular las marcaciones

---

### Paso 5: Asignar Turnos

**Última configuración:** Conectar empleados con sus turnos.

Hay **2 formas** de asignar:

#### Opción A: Asignación por Departamento (Recomendada)

**Cuándo usar:** Todos en el departamento trabajan el mismo turno.

1. Vaya a **RRHH** → **Asignación Individual**
2. Click en **Asignar Turno Múltiple**
3. Seleccione **Por Departamento**
4. Complete:
   - **Departamento:** Seleccione (ejemplo: "Ventas")
   - **Turno:** Seleccione (ejemplo: "Administrativo")
   - **Fecha Inicio:** Cuando comienza la vigencia
   - **Fecha Fin:** (opcional) Cuando termina
5. Click en **Confirmar Asignación**

**Resultado:**
```
✅ TODOS los empleados de "Ventas" ahora trabajan
   el turno "Administrativo" desde la fecha indicada
```

#### Opción B: Asignación Individual

**Cuándo usar:** Un empleado específico tiene turno diferente al departamento.

1. Vaya a **RRHH** → **Asignación Individual**
2. Click en **Asignar Turno Múltiple**
3. Seleccione **Por Empleado**
4. Complete:
   - **Empleado:** Seleccione (ejemplo: "Juan Pérez")
   - **Turno:** Seleccione
   - **Fecha Inicio/Fin**
5. Click en **Confirmar Asignación**

**Resultado:**
```
✅ Solo "Juan Pérez" tiene este turno asignado
   (las demás asignaciones no cambian)
```

---

## 🔄 3. FLUJO COMPLETO: DE LA MARCACIÓN AL REPORTE

### ¿Qué sucede cuando un empleado marca entrada/salida?

```
┌───────────────────────────────────────────────────────────┐
│ PASO 1: EMPLEADO MARCA EN EL LECTOR BIOMÉTRICO           │
│                                                           │
│  Juan Pérez coloca su huella en el lector                │
│  🖐️ → [Lector Biométrico]                                │
│                                                           │
│  RESULTADO: Se crea una "Marcación Raw" (AttendanceLog) │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Hora: 2026-02-09 08:05:32                        │   │
│  │ Usuario: EMP001 (Juan Pérez)                     │   │
│  │ Tipo: Entrada                                    │   │
│  └──────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────┘
                          ↓
┌───────────────────────────────────────────────────────────┐
│ PASO 2: SISTEMA ESPERA CALCULAR ASISTENCIA               │
│                                                           │
│  Las marcaciones se almacenan pero AÚN NO SE PROCESAN    │
│  Estado: "Marcaciones RAW guardadas"                     │
│                                                           │
│  ⏳ Esperando que administrador ejecute cálculo...       │
└───────────────────────────────────────────────────────────┘
                          ↓
┌───────────────────────────────────────────────────────────┐
│ PASO 3: ADMINISTRADOR CALCULA ASISTENCIA                 │
│                                                           │
│  Desde: Asistencia → Reporte Diario → [Calcular]        │
│                                                           │
│  Selecciona:                                             │
│  - Fecha Inicio: 2026-02-09                              │
│  - Fecha Fin:    2026-02-09                              │
│  - Departamento: (Todos o específico)                    │
│                                                           │
│  Click en [Calcular]                                     │
└───────────────────────────────────────────────────────────┘
                          ↓
┌───────────────────────────────────────────────────────────┐
│ PASO 4: SISTEMA PROCESA CADA EMPLEADO                    │
│                                                           │
│  Para Juan Pérez (EMP001) en 2026-02-09:                │
│                                                           │
│  4.1 ¿Qué turno tiene asignado?                          │
│      → Busca: Asignación Individual                      │
│      → Si no hay, busca: Asignación Departamento         │
│      → Resultado: "Turno Administrativo"                 │
│                                                           │
│  4.2 ¿Qué horario le corresponde hoy (Domingo)?          │
│      → Día: Lunes (día 0 de la semana)                  │
│      → Turno tiene: Lunes = 08:00-17:00                  │
│      → Resultado: Debe trabajar 08:00-17:00              │
│                                                           │
│  4.3 ¿Qué marcaciones hizo Juan?                         │
│      → Busca marcaciones RAW de EMP001 ese día          │
│      → Encuentra:                                        │
│         • 08:05:32 - Entrada                            │
│         • 17:02:15 - Salida                             │
│                                                           │
│  4.4 Aplicar reglas del horario:                         │
│      → Entrada: 08:05 (5 min tarde, dentro tolerancia) │
│      → Salida: 17:02 (2 min extra)                      │
│      → Minutos tarde: 5                                  │
│      → Minutos trabajados: 8h 57min (menos 1h almuerzo) │
│      → Estado: ✅ PRESENTE                               │
└───────────────────────────────────────────────────────────┘
                          ↓
┌───────────────────────────────────────────────────────────┐
│ PASO 5: SISTEMA GUARDA RESULTADO PROCESADO               │
│                                                           │
│  Se crea registro en "DailyAttendance":                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Empleado: Juan Pérez (EMP001)                    │   │
│  │ Fecha: 2026-02-09                                │   │
│  │ Estado: ✅ Presente                              │   │
│  │ Entrada: 08:05:32                                │   │
│  │ Salida: 17:02:15                                 │   │
│  │ Minutos Tarde: 5                                 │   │
│  │ Horas Trabajadas: 7h 57min                       │   │
│  │ Horario Aplicado: 08:00-17:00                    │   │
│  └──────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────┘
                          ↓
┌───────────────────────────────────────────────────────────┐
│ PASO 6: USUARIO VE EL REPORTE                            │
│                                                           │
│  En Asistencia → Reporte Diario:                        │
│                                                           │
│  ┌────────────┬──────────┬──────────┬─────────┬────────┐│
│  │ Empleado   │ Entrada  │ Salida   │ Estado  │ Tarde  ││
│  ├────────────┼──────────┼──────────┼─────────┼────────┤│
│  │ Juan Pérez │ 08:05:32 │ 17:02:15 │✅Present│ 5 min  ││
│  │ (EMP001)   │          │          │         │        ││
│  └────────────┴──────────┴──────────┴─────────┴────────┘│
└───────────────────────────────────────────────────────────┘
```

---

## 🎨 4. SISTEMA DE PRIORIDADES

### ¿Qué pasa si hay múltiples configuraciones?

El sistema usa **prioridades** para decidir qué horario aplicar:

```
┌─────────────────────────────────────────────────────┐
│         🏆 PRIORIDAD 1 (La más alta)                │
│                                                     │
│         EXCEPCIÓN MANUAL                            │
│         (ScheduleOverride)                          │
│                                                     │
│  ¿Cuándo? Configuró un horario específico para     │
│           un empleado en una fecha exacta           │
│                                                     │
│  Ejemplo: "Juan debe trabajar 10:00-19:00          │
│            solo el 14 de febrero"                   │
└─────────────────────────────────────────────────────┘
                          │
                          ↓ Si NO existe excepción
┌─────────────────────────────────────────────────────┐
│         🥈 PRIORIDAD 2                              │
│                                                     │
│         ASIGNACIÓN INDIVIDUAL                       │
│         (EmployeeShift - Empleado específico)      │
│                                                     │
│  ¿Cuándo? Asignó un turno directamente al empleado │
│                                                     │
│  Ejemplo: "Juan trabaja Turno Mañana"              │
└─────────────────────────────────────────────────────┘
                          │
                          ↓ Si NO tiene asignación individual
┌─────────────────────────────────────────────────────┐
│         🥉 PRIORIDAD 3                              │
│                                                     │
│         ASIGNACIÓN POR DEPARTAMENTO                 │
│         (EmployeeShift - Departamento)             │
│                                                     │
│  ¿Cuándo? Asignó un turno a todo el departamento   │
│                                                     │
│  Ejemplo: "Todo Ventas trabaja Turno Administrativo"│
└─────────────────────────────────────────────────────┘
                          │
                          ↓ Si NO hay asignación
┌─────────────────────────────────────────────────────┐
│         🏖️ DÍA DE DESCANSO                          │
│                                                     │
│  No tiene ninguna configuración                     │
│  = El empleado no trabaja ese día                   │
│                                                     │
│  Estado: AUSENTE (sin penalización)                │
└─────────────────────────────────────────────────────┘
```

### Ejemplo Práctico de Prioridades

**Situación:**
- **Departamento Ventas** tiene asignado "Turno Administrativo" (08:00-17:00)
- **Juan Pérez** (de Ventas) tiene asignación individual "Turno Tarde" (14:00-22:00)
- **14 de febrero** le configuró excepción "Horario Especial" (10:00-19:00)

**¿Qué horario usa Juan cada día?**

| Fecha | Horario Aplicado | Razón |
|-------|------------------|-------|
| 13 feb | 14:00-22:00 (Turno Tarde) | Prioridad 2: Tiene asignación individual |
| **14 feb** | **10:00-19:00 (Especial)** | **Prioridad 1: Excepción manual** |
| 15 feb | 14:00-22:00 (Turno Tarde) | Prioridad 2: Vuelve a su asignación individual |

**Nota:** La asignación del departamento (08:00-17:00) **nunca se usa** porque Juan tiene asignación individual que tiene más prioridad.

---

## ✏️ 5. CÓMO EDITAR CONFIGURACIONES

### Cambiar Horario de un Empleado

**Escenario:** Juan debe cambiar de turno.

**Opción 1: Nueva Asignación (Recomendado)**

1. Vaya a **RRHH** → **Asignación Individual**
2. Click en **Asignar Turno Múltiple** → **Por Empleado**
3. Seleccione:
   - Empleado: Juan Pérez
   - Turno: [Nuevo Turno]
   - Fecha Inicio: [Fecha del cambio]
4. Click en **Confirmar**

**Resultado:**
```
✅ Juan tendrá el nuevo turno desde la fecha indicada
   (el sistema automáticamente maneja el cambio)
```

**Opción 2: Excepción Manual (Para casos especiales)**

1. Vaya a (esta funcionalidad está pendiente de implementar en UI)
2. Cree ScheduleOverride con:
   - Empleado: Juan
   - Fecha: 2026-02-14
   - Horario: [Horario especial]

---

### Modificar un Horario Existente

**⚠️ IMPORTANTE:** Modificar un horario afecta a **TODOS** los que lo usan.

**Pasos:**

1. Vaya a **RRHH** → **Horarios**
2. Click en el horario a editar
3. Modifique lo necesario (ejemplo: tolerancia de 10 a 15 minutos)
4. Click en **Guardar**

**Impacto:**
```
┌────────────────────────────────────────────────────────┐
│ ⚠️ TODOS los turnos que usan este horario             │
│    aplicarán los nuevos valores INMEDIATAMENTE        │
│                                                        │
│ Ejemplo:                                              │
│ Si "Horario Administrativo 08:00-17:00" es usado por:│
│   • Turno Administrativo                              │
│   • Turno Gerencia                                    │
│                                                        │
│ Y cambia tolerancia de 10 → 15 minutos:              │
│ ➡️ Ambos turnos ahora tienen 15 min tolerancia       │
└────────────────────────────────────────────────────────┘
```

**Recomendación:** Si necesita valores diferentes, **cree un nuevo horario** en lugar de modificar uno existente.

---

### Modificar un Turno

**⚠️ IMPORTANTE:** Modificar un turno afecta a **TODOS** los empleados/departamentos asignados.

**Lo que SÍ puede hacer sin impacto:**
- Cambiar el nombre del turno (solo cosmético)

**Lo que GENERA IMPACTO:**
- Cambiar horarios de los días de la semana
- Agregar/quitar días laborables
- Cambiar de ciclo semanal a rotativo

**Ejemplo:**

```
Situación Inicial:
┌────────────────────────────────────────────────────┐
│ Turno "Administrativo" usado por:                 │
│  • Departamento Ventas (20 personas)              │
│  • Departamento RRHH (5 personas)                 │
│                                                    │
│ Lunes-Viernes: 08:00-17:00                        │
└────────────────────────────────────────────────────┘

Cambio: Agregar Sábado 08:00-12:00
                          ↓
┌────────────────────────────────────────────────────┐
│ RESULTADO:                                         │
│ ✅ 25 empleados ahora trabajan SÁBADO              │
│    (desde la próxima semana)                       │
└────────────────────────────────────────────────────┘
```

---

## 🔍 6. IMPACTO EN LAS MARCACIONES (FICHADAS RAW)

### ¿Qué son las "Marcaciones RAW"?

Son los registros **SIN PROCESAR** que vienen directamente del lector biométrico:

```
AttendanceLog (Marcación RAW)
┌─────────────────────────────────────────────┐
│ Hora: 2026-02-09 08:05:32                   │
│ Usuario: EMP001                             │
│ Dispositivo: Terminal Entrada               │
│ Tipo: Entrada (punch=0)                     │
└─────────────────────────────────────────────┘
      ↓
    [SIN PROCESAR]
      ↓
    ESPERA EL CÁLCULO
```

### ¿Las marcaciones RAW cambian cuando edito configuración?

**NO. Las marcaciones RAW NUNCA cambian.**

Lo que **SÍ cambia** es cómo el sistema las **interpreta** cuando calcula:

```
┌──────────────────────────────────────────────┐
│ MARCACIÓN RAW (nunca cambia):                │
│   08:05:32 - Entrada                         │
└──────────────────────────────────────────────┘
                  ↓
         ┌────────┴─────────┐
         │                  │
    ANTES (Tolerancia 10min) │ DESPUÉS (Tolerancia 15min)
         │                  │
    08:05 = 5 min tarde     │ 08:05 = Dentro de tolerancia
    Estado: ⚠️ Late        │ Estado: ✅ Present
         │                  │
         └──────────────────┘
```

### Escenarios de Impacto

#### Escenario 1: Cambio de Tolerancia

**Situación:**
- Empleado marcó: 08:12
- Horario original: Tolerancia 10 minutos
  - **Resultado:** ⚠️ Llegó tarde (12-10 = 2 min fuera de tolerancia)

**Cambio:** Aumenta tolerancia a 15 minutos

**Nuevo cálculo:**
- Empleado marcó: 08:12 (misma marcación RAW)
- Horario nuevo: Tolerancia 15 minutos
  - **Resultado:** ✅ Llegó a tiempo (12 < 15)

**Impacto:**
```
✅ La marcación 08:12 ahora es VÁLIDA
   (auto-recalcula si ejecuta cálculo nuevamente)
```

#### Escenario 2: Cambio de Horario

**Situación:**
- Empleado marcó: 13:45 (entrada)
- Turno original: 08:00-17:00
  - **Resultado:** 🛑 Llegó 5h 45min tarde

**Cambio:** Asigna turno tarde: 14:00-22:00

**Nuevo cálculo:**
- Empleado marcó: 13:45 (misma marcación RAW)
- Turno nuevo: 14:00-22:00
  - **Resultado:** ✅ Llegó 15 min antes

**Impacto:**
```
✅ La marcación 13:45 ahora es correcta
   (cambió el contexto, no la marcación)
```

#### Escenario 3: Cambio de Día Laborable

**Situación:**
- Empleado marcó domingo: 08:00
- Turno original: Lun-Vie (Sábado/Domingo descanso)
  - **Resultado:** 🏖️ Día no laborable (ignorado)

**Cambio:** Turno ahora incluye Domingo: 08:00-12:00

**Nuevo cálculo:**
- Empleado marcó: 08:00 (misma marcación RAW)
- Turno nuevo: Incluye domingo
  - **Resultado:** ✅ Trabajó medio día domingo

**Impacto:**
```
✅ La marcación del domingo ahora CUENTA
   (antes se ignoraba)
```

---

## ⚡ 7. RECALCULAR ASISTENCIA

### ¿Cuándo recalcular?

Debe recalcular la asistencia cuando:

1. ✅ Cambió tolerancias de horarios
2. ✅ Cambió horarios de turnos
3. ✅ Reasignó turnos a empleados
4. ✅ Importó marcaciones nuevas del lector

### ¿Cómo recalcular?

1. Vaya a **Asistencia** → **Reporte Diario**
2. Seleccione el rango de fechas a recalcular
3. Click en **[Calcular]**
4. Espere el mensaje de confirmación

**Resultado:**
```
✅ El sistema:
   1. Lee todas las marcaciones RAW del periodo
   2. Aplica la configuración ACTUAL (nueva)
   3. Sobrescribe los registros antiguos
   4. Genera nuevo reporte con valores actualizados
```

### ⚠️ Importante sobre Recalcular

```
┌────────────────────────────────────────────────────┐
│ RECALCULAR = SOBRESCRIBE DATOS ANTERIORES         │
│                                                    │
│ Antes del recálculo:                              │
│  Juan: ⚠️ Tarde (5 min)                          │
│                                                    │
│ Después del recálculo (con nueva tolerancia):     │
│  Juan: ✅ A tiempo (dentro de 15 min)            │
│                                                    │
│ ➡️ NO guarda historial de cálculos anteriores    │
└────────────────────────────────────────────────────┘
```

**Recomendación:** Si necesita comparar resultados antes/después, exporte el reporte actual antes de recalcular.

---

## 📊 8. CASOS DE USO COMUNES

### Caso 1: Inicio de Operaciones

**Situación:** Empresa nueva que va a comenzar a usar el sistema.

**Pasos:**

1. **Semana 1: Configuración Base**
   - Crear departamentos
   - Crear horarios
   - Crear turnos
   - Conectar turnos con horarios

2. **Semana 2: Personal**
   - Registrar empleados
   - Asignar a departamentos
   - Asignar turnos por departamento

3. **Semana 3: Pruebas**
   - Hacer que empleados marquen
   - Ejecutar cálculo de prueba
   - Revisar reportes
   - Ajustar tolerancias si es necesario

4. **Semana 4: Producción**
   - Operación normal
   - Cálculo diario o semanal

---

### Caso 2: Cambio Masivo de Turno

**Situación:** Todo el departamento de Ventas cambia de turno mañana a turno tarde.

**Pasos:**

1. **Opción A: Crear Nueva Asignación**
   - RRHH → Asignación Individual
   - Asignar Turno Múltiple → Por Departamento
   - Departamento: Ventas
   - Turno: Turno Tarde
   - Fecha Inicio: [Fecha del cambio]
   - Confirmar

2. **Resultado:**
   ```
   Automáticamente:
   ├─ Asignación anterior termina: Fin = [día antes del cambio]
   └─ Nueva asignación comienza: Inicio = [fecha del cambio]
   
   ✅ 20 empleados ahora trabajan Turno Tarde
      desde la fecha indicada
   ```

---

### Caso 3: Empleado con Horario Especial Temporal

**Situación:** María necesita trabajar horario especial durante 2 semanas.

**Pasos:**

1. RRHH → Asignación Individual
2. Asignar Turno Múltiple → Por Empleado
3. Seleccionar: María López
4. Turno: [Turno especial]
5. Fecha Inicio: 2026-02-10
6. Fecha Fin: 2026-02-21 (2 semanas)
7. Confirmar

**Resultado:**
```
┌─────────────────────────────────────────────────┐
│ María López:                                    │
│                                                 │
│ Antes 2026-02-10: Turno Administrativo         │
│ ├─ 2026-02-10 al 21: ⭐ Turno Especial        │
│ Después 2026-02-21: Turno Administrativo       │
│                                                 │
│ ✅ Automáticamente vuelve a su turno original │
└─────────────────────────────────────────────────┘
```

---

## ⚠️ 9. PREGUNTAS FRECUENTES (FAQ)

### ❓ Si cambio un horario, ¿afecta cálculos anteriores?

**Respuesta:** NO, a menos que **vuelva a calcular**.

- Los cálculos ya hechos **permanecen igual** hasta que recalcule
- Si recalcula, se sobrescriben con los nuevos valores
- Las marcaciones RAW **nunca cambian**

---

### ❓ ¿Puedo eliminar un turno que ya está en uso?

**Respuesta:** El sistema **NO debe permitirlo** (protección de datos).

Si necesita eliminarlo:
1. Primero reasigne a los empleados a otro turno
2. Espere confirmación de que no hay dependencias
3. Entonces podrá eliminarlo

---

### ❓ ¿Las marcaciones RAW se pueden editar?

**Respuesta:** NO directamente (protección de integridad).

Si hay un error en una marcación:
- **Opción 1:** Crear excepción manual para ese día
- **Opción 2:** Editar el registro procesado (DailyAttendance) manualmente
- **Opción 3:** Contactar soporte para corrección en logs

---

### ❓ ¿Qué pasa si un empleado marca sin tener turno asignado?

**Respuesta:**

1. La marcación RAW **sí se guarda**
2. Al calcular, el sistema:
   - Detecta que no tiene turno
   - Lo marca como **"Saltado"**
   - Reporta: "Razón: NO_SHIFT_ASSIGNED"
3. Estado final: **No aparece en reporte de asistencia**

**Solución:** Asigne un turno al empleado y recalcule.

---

### ❓ ¿Cómo sé si mi configuración está correcta?

**Prueba rápida:**

1. Seleccione 1 empleado de prueba
2. Asegúrese que tenga:
   - ✅ Departamento asignado
   - ✅ Turno asignado (individual o departamental)
   - ✅ El turno tiene horarios configurados
3. Cree una marcación de prueba
4. Ejecute cálculo para ese día
5. Revise que aparezca en el reporte

Si aparece con su horario correcto: ✅ **Configuración exitosa**

---

## 📌 10. RESUMEN VISUAL

```
┌─────────────────────────────────────────────────────────────┐
│           FLUJO COMPLETO DE CONFIGURACIÓN                   │
└─────────────────────────────────────────────────────────────┘

PASO 1: DEPARTAMENTOS
🏛️ Crear → Ventas, Producción, Admin, RRHH
           ↓
PASO 2: HORARIOS
⏰ Crear → 08:00-17:00 (Admin)
          06:00-14:00 (Producción)
          14:00-22:00 (Tarde)
           ↓
PASO 3: TURNOS
🔄 Crear → Turno Admin (Lun-Vie: 08:00-17:00)
          Turno Producción (Lun-Sab: 06:00-14:00)
          Turno Tarde (Lun-Vie: 14:00-22:00)
           ↓
PASO 4: EMPLEADOS
👤 Registrar → EMP001, EMP002, EMP003...
              Asignar a departamentos
           ↓
PASO 5: ASIGNAR TURNOS (RRHH → Asignación Individual)
🔗 Por Departamento: Ventas → Turno Admin
   Por Empleado: Juan → Turno Tarde
           ↓
PASO 6: MARCACIONES
🖐️ Empleados marcan en el lector
   → AttendanceLog (RAW)
           ↓
PASO 7: CALCULAR
⚙️ Ejecutar cálculo desde UI
   → DailyAttendance (PROCESADO)
           ↓
PASO 8: REPORTES
📊 Ver resultados en Reporte Diario
   Revisar ausencias, tardanzas
```

---

## 🎓 11. MEJORES PRÁCTICAS

### ✅ DO (Hacer)

1. **Planifique antes de configurar**
   - Liste todos sus departamentos
   - Defina horarios claramente
   - Diseñe turnos en papel primero

2. **Use asignación por departamento cuando sea posible**
   - Más fácil de mantener
   - Menos trabajo al agregar empleados nuevos

3. **Nombre descriptivamente**
   - ❌ "Turno 1"
   - ✅ "Administrativo Lun-Vie 08:00-17:00"

4. **Pruebe antes de implementar masivamente**
   - Cree configuración
   - Pruebe con 1-2 empleados
   - Valide resultados
   - Entonces aplique a todos

5. **Documente sus cambios**
   - Antes de cambiar tolerancias: "Antes: 10 min"
   - Exporte reporte si es necesario
   - Anote fecha y razón del cambio

### ❌ DON'T (No Hacer)

1. **No elimine configuraciones en uso**
   - Siempre reasigne primero
   - Verifique dependencias

2. **No modifique horarios sin planificar**
   - Recuerde: afecta a TODOS los que lo usan
   - Considere crear uno nuevo en su lugar

3. **No olvide recalcular después de cambios**
   - Los reportes no se actualizan solos
   - Debe ejecutar cálculo manualmente

4. **No configure sin entender el impacto**
   - Lea primero esta guía
   - Haga pruebas en periodo de prueba
   - Valide con datos reales

5. **No pierda las marcaciones RAW**
   - Son su registro original
   - Haga respaldos periódicos
   - No permita modificación directa

---

## 📞 12. SOPORTE

### ¿Necesita ayuda?

**Para problemas técnicos:**
- Revise la sección de FAQ arriba
- Consulte el documento técnico (TECHNICAL_HIERARCHY_ARCHITECTURE.md)
- Contacte al administrador del sistema

**Para configuración:**
- Siga esta guía paso a paso
- Haga pruebas pequeñas primero
- Documente cada cambio que realice

**Para reportar errores:**
1. Anote qué estaba haciendo
2. Capture pantalla si es posible
3. Anote fecha/hora del problema
4. Contacte soporte con esta información

---

**Documento generado:** 2026-02-09  
**Sistema:** SRTimeWeb  
**Versión:** 2.0  
**Ubicación:** `/docs/GUIA_USUARIO_JERARQUIA_ORGANIZACIONAL.md`

---

✅ **¡Configuración exitosa!**

Si siguió todos los pasos, su sistema ahora está listo para operar. Recuerde hacer cálculos periódicos y revisar los reportes regularmente.
