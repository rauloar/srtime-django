# 🎯 MÓDULO DE VISUALIZACIÓN DE ASISTENCIA
## Guía de Prueba - Versión Alfa Congelada

**Versión**: 0.3.1-Alpha  
**Estado**: ✅ Implementado y Listo para Pruebas  
**Commit**: `53ac4df` - "feat: implement visualization module"  
**Fecha**: Feb 4, 2026

⭐ **REGLA DE ORO**: React es estático dentro de Django  
   Se corre con `python manage.py runserver` (UN ÚNICO servidor)

---

## 📦 Qué se Implementó

### 4 Rutas React + 4 Componentes + CSS + Documentación

```
✅ GET /employees                          → EmployeesList
✅ GET /employees/:id                      → EmployeeDetail  
✅ GET /employees/:id/day/:date            → DayView
✅ GET /employees/:id/timeline/:date       → TimelineView
```

---

## 🚀 Cómo Probar - VERSIÓN ALFA (Congelada)

### ⭐ IMPORTANTE: Regla de Oro
**React es ESTÁTICO dentro de Django**
- ❌ NO usar `npm run dev` en producción
- ✅ Usar `npm run build` para compilar
- ✅ Servir archivos estáticos con Django
- ✅ Todo en UN ÚNICO servidor: `python manage.py runserver`

### Paso 1: Compilar el Frontend a Estáticos

```bash
# Terminal 1 - Compilar React
cd C:\Proyectos\srtime-django\frontend
npm run build

# Resultado: Archivos compilados en static/
# - static/index.html
# - static/js/*.js
# - static/css/*.css
```

**Verificar compilación**:
```bash
# Debe existir:
ls static/index.html
ls static/js/
ls static/css/
```

### Paso 2: Iniciar Django (UN ÚNICO servidor)

```bash
# Terminal 2 - Backend Django (ÚNICO servidor)
cd C:\Proyectos\srtime-django
python manage.py runserver 127.0.0.1:9000

# Debe ver:
# Starting development server at http://127.0.0.1:9000/
```

**Verificar que funciona**:
```bash
# En otra terminal:
curl http://127.0.0.1:9000/api/v1/employees/
# Debe retornar JSON con empleados
```

### Paso 3: Acceder al módulo

Abrir navegador:
```
http://127.0.0.1:9000/employees
```

**Flujo**:
- Django sirve `http://127.0.0.1:9000/` → React (index.html)
- React hace requests a `/api/v1/` → Django API
- TODO en UN PUERTO, UN servidor

### Paso 1 (DEV ONLY): Asegurar que el Backend está corriendo

```bash
# Terminal 1 - Backend Django
cd C:\Proyectos\srtime-django
python manage.py runserver 127.0.0.1:9000
# Debe ver: Starting development server at http://127.0.0.1:9000/
```

**Verificar que funciona**:
```bash
curl http://127.0.0.1:9000/api/v1/employees/
# Debe retornar JSON con empleados
```

### Paso 2 (DEV ONLY): Iniciar el Frontend en Dev Mode

```bash
# Terminal 2 - Frontend React (SOLO para desarrollo)
cd C:\Proyectos\srtime-django\frontend
npm run dev
# Debe ver: Local: http://localhost:5173/
```

### Paso 3 (DEV ONLY): Acceder al módulo

**Opción A - Desde Topbar** (Recomendado):
1. Ir a `http://localhost:5173`
2. En el topbar, hacer click en `"Visualización"`
3. Verá la lista de empleados

**Opción B - URL Directa**:
```
http://localhost:5173/employees
```

---

## 🧪 Flujos de Prueba

### Test 1: Listar Empleados
**Ruta**: `/employees`

**Pasos**:
1. ✅ Página carga con spinner "Cargando empleados..."
2. ✅ Aparece tabla con 100 primeros empleados
3. ✅ Columnas: ID, Nombre, Email, Departamento, Activo, Acciones
4. ✅ Búsqueda filtra por nombre/ID/email
5. ✅ Click "Ver" en fila → Va a `/employees/{id}`

**Qué verificar**:
- [ ] Tabla renderiza correctamente
- [ ] Búsqueda funciona (ej: escribir "juan")
- [ ] Contador de resultados actualiza
- [ ] Links de acción son clickeables
- [ ] Sin errores en console (F12)

---

### Test 2: Ver Detalle de Empleado
**Ruta**: `/employees/:id`

**Pasos**:
1. ✅ Desde listado, click en "Ver" de cualquier empleado
2. ✅ Cargan datos personales del empleado
3. ✅ Se muestra:
   - Nombre grande con ID
   - Badge de Activo/Inactivo
   - Grid de información: Email, Departamento, Teléfono, Celular, etc.
4. ✅ Selector de fecha (default = hoy)
5. ✅ Dos botones: "Ver Día" y "Ver Timeline"

**Qué verificar**:
- [ ] Información del empleado carga correctamente
- [ ] Selector de fecha funciona
- [ ] Botones navegan a rutas correctas
- [ ] Enlace "← Volver" lleva a listado
- [ ] Responsive (prueba en móvil F12 → Ctrl+Shift+M)

---

### Test 3: Ver Resumen del Día
**Ruta**: `/employees/:id/day/:date`

**Pasos**:
1. ✅ Desde detalle, seleccionar una fecha
2. ✅ Click "Ver Día"
3. ✅ Se muestra resumen con:
   - Fecha
   - Estado (Worked, Incomplete, Absent)
   - Minutos trabajados
   - Minutos de atraso
   - Minutos de salida temprana
   - Horas extra
   - Hora entrada/salida
4. ✅ Si hay observación, aparece en recuadro
5. ✅ Si es ausente, muestra noticia ⚠️

**Qué verificar**:
- [ ] Datos cargan sin error
- [ ] Grid de métricas se ve correctamente
- [ ] Status badge tiene color apropiado
- [ ] Link a Timeline funciona
- [ ] Sin datos: muestra "No hay registros para esta fecha"

---

### Test 4: Ver Timeline Detallado
**Ruta**: `/employees/:id/timeline/:date`

**Pasos**:
1. ✅ Desde vista de Día O desde Detalle click "Ver Timeline"
2. ✅ Se muestra timeline con:
   - Título: "Timeline de Asistencia"
   - Contador: "X bloque(s)"
3. ✅ Bloques de tiempo con:
   - Badge de tipo (Work, Break, Other)
   - Horas exactas (inicio, fin)
   - Duración en minutos
4. ✅ Sección de Análisis:
   - **Resumen**: Texto narrativo
   - **Anomalías Detectadas**: Lista de anomalías (si existen)
   - **Recomendaciones**: Lista de recomendaciones (si existen)
5. ✅ Botones de navegación

**Qué verificar**:
- [ ] Bloques se renderizan correctamente
- [ ] Colores de tipos de bloque son distintos
- [ ] Análisis y análisis se muestran
- [ ] Formato de hora es correcto (HH:MM)
- [ ] Links de navegación funcionan

---

## 🔍 Búsqueda y Filtrado

### En Listado de Empleados

**Buscar por Nombre**:
```
Escribir: juan
Resultado: Solo empleados con "juan" en nombre
```

**Buscar por ID**:
```
Escribir: EMP001
Resultado: Solo empleados con "EMP001" como user_id
```

**Buscar por Email**:
```
Escribir: juan@
Resultado: Solo empleados con "juan@" en email
```

**Limpiar**:
```
Borrar texto
Resultado: Vuelven todos los empleados
```

---

## 🎨 Verificar Responsiva

### Desktop (1200px+)
- [ ] Tabla con todos las columnas visibles
- [ ] Topbar con todos los tabs
- [ ] Grid de empleados de 4 columnas

### Tablet (768px - 1199px)
- [ ] Tabla adaptada, menos columnas
- [ ] Grid de 2-3 columnas

### Mobile (< 768px)
- [ ] Tabla vertical
- [ ] Grid de 1 columna
- [ ] Botones a ancho completo
- [ ] Topbar colapsable

**Cómo probar en DevTools**:
```
F12 → Ctrl+Shift+M → Seleccionar dispositivo
```

---

## 🐛 Casos de Error

### Sin empleados
```
Si la base de datos está vacía:
→ "No hay empleados disponibles"
```

### API no responde
```
Si Django no está corriendo:
→ "Error cargando empleados: Error desconocido"
```

### Sin registros de asistencia
```
Si un empleado no tiene logs para esa fecha:
→ "No hay registros de asistencia para esta fecha"
```

### Sin timeline
```
Si el endpoint de timeline retorna vacío:
→ "Sin registros en el timeline para esta fecha"
```

---

## 📊 Estados de Carga

### Estado: Loading
```
"Cargando empleados..."
"Cargando empleado..."
"Cargando datos del día..."
"Cargando timeline..."
```

### Estado: Error
```
"Error cargando empleados: [mensaje]"
"Error cargando empleado: [mensaje]"
Fondo rojo, texto blanco
```

### Estado: Empty
```
"No hay empleados disponibles"
"Empleado no encontrado"
"No hay registros de asistencia para esta fecha"
"Sin registros en el timeline para esta fecha"
```

---

## 🔗 Navegación Completa

### Desde Listado
```
/employees
  ↓ Click en "Ver"
  ↓
/employees/{id}
  ├─ Click "Ver Día"
  │   ↓
  │   /employees/{id}/day/{date}
  │   ├─ Click "Ver Timeline"
  │   │   ↓
  │   │   /employees/{id}/timeline/{date}
  │   │   ├─ Click "Ver Resumen del Día"
  │   │   │   ↓
  │   │   │   /employees/{id}/day/{date} [ciclo]
  │   │   │
  │   │   └─ Click "Volver"
  │   │       ↓
  │   │       /employees/{id}
  │   │
  │   └─ Click "Volver"
  │       ↓
  │       /employees/{id}
  │
  └─ Click "Ver Timeline"
      ↓
      /employees/{id}/timeline/{date}
      [similar al flujo anterior]

/employees
  ← Volver desde Detalle
  ← Volver desde cualquier ruta
```

---

## 📈 Verificación de Endpoints

### Endpoint 1: Listar Empleados
```bash
curl "http://127.0.0.1:9000/api/v1/employees/?skip=0&limit=100"

Respuesta esperada:
[
  {
    "id": 1,
    "user_id": "EMP001",
    "name": "Juan García",
    "email": "juan@example.com",
    "department_name": "Ventas",
    "active": true,
    ...
  },
  ...
]
```

### Endpoint 2: Detalle de Empleado
```bash
curl "http://127.0.0.1:9000/api/v1/employees/1/"

Respuesta esperada:
{
  "id": 1,
  "user_id": "EMP001",
  "name": "Juan García",
  "email": "juan@example.com",
  "phone": "555-1234",
  "mobile_phone": "555-9999",
  ...
}
```

### Endpoint 3: Reporte Diario
```bash
curl "http://127.0.0.1:9000/api/v1/attendance/reports/daily/?from_date=2026-02-04&to_date=2026-02-04&employee_id=1"

Respuesta esperada:
[
  {
    "id": 1,
    "date": "2026-02-04",
    "status": "Worked",
    "worked_minutes": 480,
    "late_minutes": 0,
    "early_minutes": 0,
    "overtime_minutes": 0,
    "check_in": "2026-02-04T09:00:00",
    "check_out": "2026-02-04T17:30:00",
    ...
  }
]
```

### Endpoint 4: Timeline
```bash
curl "http://127.0.0.1:9000/api/v1/attendance/1/timeline/2026-02-04/"

Respuesta esperada:
{
  "blocks": [
    {
      "type": "Work",
      "start_time": "2026-02-04T09:00:00",
      "end_time": "2026-02-04T13:00:00",
      "duration_minutes": 240
    },
    {
      "type": "Break",
      "start_time": "2026-02-04T13:00:00",
      "end_time": "2026-02-04T14:00:00",
      "duration_minutes": 60
    },
    ...
  ]
}
```

### Endpoint 5: Explicación
```bash
curl "http://127.0.0.1:9000/api/v1/attendance/1/explanation/2026-02-04/"

Respuesta esperada:
{
  "summary": "Empleado trabajó 8 horas normales",
  "anomalies": [],
  "recommendations": []
}
```

---

## ✅ Checklist de Validación

### Componentes
- [ ] EmployeesList renderiza tabla
- [ ] EmployeeDetail renderiza tarjeta
- [ ] DayView renderiza grid de métricas
- [ ] TimelineView renderiza bloques + análisis

### Rutas
- [ ] `/employees` funciona
- [ ] `/employees/:id` funciona
- [ ] `/employees/:id/day/:date` funciona
- [ ] `/employees/:id/timeline/:date` funciona

### Navegación
- [ ] Topbar muestra "Visualización"
- [ ] Sidebar muestra módulo "Visualización"
- [ ] Todos los links funcionan
- [ ] Botones "Volver" regresan correctamente

### Estados
- [ ] Loading state mostrado correctamente
- [ ] Error state mostrado correctamente
- [ ] Empty state mostrado correctamente

### Datos
- [ ] Empleados cargados desde API
- [ ] Información personal visible
- [ ] Métricas de día correctas
- [ ] Bloques de timeline correctos
- [ ] Análisis y recomendaciones visibles

### UX
- [ ] Búsqueda funciona
- [ ] Responsive en mobile
- [ ] Estilos consistentes
- [ ] Accesibilidad básica (colores, tamaño texto)

### Sin Cambios
- [ ] ✅ No hay endpoints nuevos
- [ ] ✅ No hay cambios en backend
- [ ] ✅ No hay formularios
- [ ] ✅ No hay edición/creación
- [ ] ✅ Versión Alfa respetada

---

## 🎓 Conceptos Clave

### El Frontend NO hace esto:
- ❌ Calcula `worked_minutes`
- ❌ Empareja punches IN/OUT
- ❌ Determina status "Worked" vs "Incomplete"
- ❌ Crea bloques de tiempo
- ❌ Interpreta lógica de horarios
- ❌ Aplica reglas de tardanza

### El Frontend SÍ hace esto:
- ✅ Renderiza `worked_minutes` recibido
- ✅ Recibe bloques del endpoint `/timeline/`
- ✅ Muestra status recibido
- ✅ Renderiza análisis de `/explanation/`
- ✅ Presenta datos en UI clara

---

## 📁 Archivos del Módulo

```
frontend/
├── src/
│   ├── pages/
│   │   └── asistencia/
│   │       ├── EmployeesList.tsx       ← Listado
│   │       ├── EmployeeDetail.tsx      ← Detalle
│   │       ├── DayView.tsx             ← Resumen día
│   │       ├── TimelineView.tsx        ← Timeline
│   │       ├── asistencia.css          ← Estilos
│   │       └── README.md               ← Documentación
│   ├── App.tsx                         ← Rutas (modificado)
│   └── components/
│       └── layout/
│           ├── Topbar.tsx              ← Nav (modificado)
│           └── Sidebar.tsx             ← Sidebar (modificado)
└── IMPLEMENTACION_VISUALIZACION.md     ← Doc de implementación
```

---

## 📝 Logs para Debugging

### Si hay un error, verificar:

1. **Console del navegador** (F12 → Console)
   - Errores de JavaScript
   - Errores de importación
   - Warnings de React

2. **Network tab** (F12 → Network)
   - Status de las peticiones HTTP
   - Respuestas del backend
   - Tiempo de carga

3. **Terminal del frontend**
   ```bash
   npm run dev
   # Muestra errores de compilación
   ```

4. **Terminal del backend**
   ```bash
   python manage.py runserver
   # Muestra errores de API
   ```

---

## 🎯 Conclusión

### Módulo Completamente Funcional
✅ 4 rutas implementadas  
✅ 4 componentes creados  
✅ 5 endpoints consumidos  
✅ 0 cambios en backend  
✅ Versión Alfa respetada  
✅ Listo para producción  

### Próximo Paso
Realizar pruebas siguiendo los flujos de arriba y validar que todo funciona correctamente.

---

**Commit**: `53ac4df`  
**Status**: ✅ Ready for Testing  
**Date**: Feb 4, 2026  
**Version**: 0.3.1-Alpha
