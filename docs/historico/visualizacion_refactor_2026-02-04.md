# Refactor UI de Visualizacion (2026-02-04)

## Objetivo
Alinear el modulo de visualizacion con la realidad de datos productivos (ZKTimeNet), respetando el principio de que el sistema muestra datos crudos y RRHH interpreta.

## Cambios realizados

### 1) Detalle de fichadas
Archivo: frontend/src/components/asistencia/DayPunchList.tsx

- Se agrego precision a segundos (HH:MM:SS) para distinguir eventos dentro del mismo minuto.
- Se cambio la iconografia para entrada/salida por simbolos simples.
- Se resaltan automaticamente:
  - eventos cercanos (< 2 minutos)
  - secuencias irregulares (dos entradas o dos salidas seguidas)
- Se ajusto el copy para mantener tono neutral y observacional.

### 2) Linea de tiempo
Archivo: frontend/src/components/asistencia/DayTimeline.tsx

- Se reemplazaron etiquetas evaluativas por descripciones neutrales.
- Se simplifico el formato de duracion.
- Se ajusto el texto de nota para aclarar que la clasificacion es automatica y requiere contexto humano.

### 3) Explicacion del dia
Archivo: frontend/src/pages/asistencia/DayViewPage.tsx

- Se oculto el componente DayExplanation para evitar contenido evaluativo (anomalias y recomendaciones).

### 4) Acciones del dia
Archivo: frontend/src/components/asistencia/DayActions.tsx

- Se elimino la logica que determinaba "problemas" basada en estados evaluativos.
- Se reemplazaron acciones por opciones neutras (ajuste manual y nota de RRHH) deshabilitadas (Fase 2).
- Se mantuvo el toggle de detalles tecnicos con un id mas explicito.

## Principios aplicados
- Mostrar datos registrados, no juicios sobre el comportamiento.
- Evitar etiquetas evaluativas en UI (late/absent/early).
- Asegurar que RRHH pueda leer eventos cercanos en segundos.

## Pendientes opcionales
- Reintroducir una seccion de observaciones no evaluativas (conteo de eventos, primer/ultimo registro, fuentes).
- Agregar leyenda breve para explicar "evento cercano" y "secuencia irregular".
