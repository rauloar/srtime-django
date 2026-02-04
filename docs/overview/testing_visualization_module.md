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