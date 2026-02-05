# Manual de Uso (Simple) - Alpha

Este manual es breve porque el sistema esta en fase alfa. Esta orientado al usuario final o QA que prueba desde la UI.

## Objetivo
- Ver asistencia diaria por empleado.
- Registrar correcciones manuales cuando falten fichadas.
- Reprocesar un periodo para generar un informe correcto.

## Flujo Basico (UI)
1) Abrir el modulo de asistencia.
2) Buscar un empleado y elegir una fecha.
3) Revisar el detalle de fichadas (entradas/salidas).
4) Si falta una fichada o hay error, registrar la correccion con un motivo.
5) Reprocesar el periodo.
6) Revisar el resultado diario y ausencias con motivo.

## Paso a Paso Detallado

### Pantalla 1: Listado de Empleados
1) Desde el navbar superior, ir a **Visualización** → **Empleados**.
2) Se abre la pantalla "**Empleados**" con tabla de búsqueda.
3) Opcionalmente, buscar por nombre o ID en el campo de búsqueda.
4) Seleccionar un empleado haciendo clic en la fila.

### Pantalla 2: Detalle del Empleado
5) Se abre la página de detalle con información del empleado.
6) Seleccionar una fecha (calendario o rango) para ver el día específico.
7) Hacer clic en el botón "Ver Día" o la fecha elegida.

### Pantalla 3: Vista Diaria (DayView)
8) Se abre el resumen del día con:
   - **Cabecera**: Información del empleado, fecha, estado resumen.
   - **Métricas**: Minutos trabajados, status, horario esperado.
   - **Lista de Fichadas**: Tabla con todas las entradas/salidas del día.
     - Columnas: Hora exacta (HH:MM:SS), tipo (Entrada/Salida), estado.
   - **Línea de Tiempo**: Visualización gráfica de los bloques de trabajo.
9) Revisar si hay problemas evidentes (ej: sin checkout, sin checkin).

### Pantalla 4: Correccion Manual (Si es necesario)
10) Si falta una fichada o hay error:
    - Ir a la sección **Administración** (si está disponible).
    - Buscar el empleado en la lista de logs crudos.
    - Hacer clic en "Editar".
11) Se abre el formulario de edición con campos:
    - `timestamp`: Fecha/hora de la fichada.
    - `edited_reason`: Motivo de la correccion (REQUERIDO).
    - `is_manual`: Marcar como "Editado manualmente".
12) Ejemplos de motivos a escribir:
    - "Terminal fuera de servicio, no pudo fichar"
    - "Empleado en vacaciones desde 2025-04-01"
    - "Consultor externo - prueba de sistema"
    - "Falta de salida, empleado olvido fichaje"
13) Hacer clic en "Guardar".

### Pantalla 5: Reprocesar Período
14) Ir a **Asistencia** → **Cálculos** (o pantalla de Reportes).
15) Completar formulario:
    - `start_date`: Fecha inicial (YYYY-MM-DD).
    - `end_date`: Fecha final (YYYY-MM-DD).
    - Opcionalmente, `department_id` para filtrar por departamento.
16) Hacer clic en "Procesar" o "Calcular".
17) Esperar confirmación: "Calculadas XXX registros".

### Pantalla 6: Revisar Resultados
18) Ir a **Asistencia** → **Asistencia Diaria**.
19) Filtrar por:
    - Rango de fechas (date__gte, date__lte).
    - Empleado específico (opcional).
    - Estado (por defecto mostrar todos).
20) Revisar la columna **"Motivo Excepción"** para ver por qué un día es "Ausente":
    - "Shift assigned but has no timetable hours configured" = Error de configuración.
    - "No schedule configured for this date" = Sin horario asignado.
    - NULL = Ausencia real (no hay logs del dia).
21) Hacer clic en un registro para ver detalles completos.

### Pantalla 7: Revisar Ausencias
22) Ir a **Asistencia** → **Ausencias** (o Licencias/Leaves).
23) Revisar licencias registradas vs. lo que aparece en Asistencia Diaria.
24) Validar consistencia: si hay una licencia, el dia debe estar marcado como Absent con motivo "Licencia" o similar.

## Validaciones de QA
- [ ] Crear un empleado de prueba sin turno asignado → debe aparecer como "Ausente" sin horas.
- [ ] Editar un log crudo con motivo → reprocesar → debe reflejarse el cambio en vista diaria.
- [ ] Crear una licencia → verificar que aparezca en ausencias.
- [ ] Reprocesar un rango amplio → verificar tiempo de respuesta y cantidad de registros calculados.
- [ ] Revisar que motivos técnicos (sin timetables) se diferencien de ausencias reales.

## Notas
- El sistema no se detiene por errores de configuración; los registra como motivo.
- Las ausencias pueden ser reales, administrativas o técnicas. RRHH decide el criterio final.
- QA debe validar que los cambios manuales se reflejen después del reprocesamiento dentro de 30 segundos.
- Si un filtro no devuelve resultados, verificar que el rango de fechas incluya datos existentes.
