# 🎯 Módulo de Visualización de Asistencia - Frontend

## Descripción

El módulo de Visualización de Asistencia es una interfaz React que conecta con el backend Django para mostrar la información de asistencia de empleados en Versión Alfa. 

**Principio fundamental**: El frontend **NO calcula asistencia**, **NO interpreta IN/OUT**, solo **renderiza** lo que recibe del backend.

---

## 🗂️ Estructura de Rutas

### 1. **Listado de Empleados**
**Ruta**: `/employees`

- Muestra tabla de todos los empleados
- Búsqueda por nombre, ID o email
- Estados de carga, error y sin datos
- Link rápido a detalle de cada empleado

**Componente**: `EmployeesList.tsx`

**Endpoint consumido**:
```
GET /api/v1/employees/?skip=0&limit=100
```

---

### 2. **Detalle de Empleado**
**Ruta**: `/employees/:id`

- Información completa del empleado
- Datos personales (nombre, email, departamento, etc.)
- Selector de fecha para visualizar asistencia
- Botones para navegar a "Ver Día" y "Ver Timeline"

**Componente**: `EmployeeDetail.tsx`

**Endpoints consumidos**:
```
GET /api/v1/employees/{id}
```

---

### 3. **Vista de Día**
**Ruta**: `/employees/:id/day/:date`

- Resumen de asistencia para una fecha específica
- Muestra estado (Trabajado, Incompleto, Ausente, etc.)
- Minutos: trabajados, atraso, salida temprana, horas extra
- Horas de entrada/salida registradas
- Observaciones si existen

**Componente**: `DayView.tsx`

**Endpoints consumidos**:
```
GET /api/v1/employees/{id}
GET /api/v1/attendance/reports/daily/?from_date={date}&to_date={date}&employee_id={id}
```

---

### 4. **Vista de Timeline**
**Ruta**: `/employees/:id/timeline/:date`

- Bloques de tiempo registrados (IN/OUT, descansos)
- Tipo de bloque (Work, Break, etc.)
- Horas exactas de inicio/fin y duración
- Análisis y explicación del día
- Anomalías detectadas
- Recomendaciones

**Componente**: `TimelineView.tsx`

**Endpoints consumidos**:
```
GET /api/v1/employees/{id}
GET /api/v1/attendance/{id}/timeline/{date}/ 
GET /api/v1/attendance/{id}/explanation/{date}/
```

---

## 🎨 Interfaz de Usuario

### Estilos y CSS

**Archivo**: `pages/asistencia/asistencia.css`

Incluye:
- Grid de empleados responsivo
- Tablas con hover effects
- Tarjetas de información
- Badges de estado (Activo/Inactivo, Trabajado/Incompleto, etc.)
- Timeline visual con bloques
- Secciones de análisis y recomendaciones
- Responsive design para mobile

### Variables CSS utilizadas

El proyecto utiliza variables CSS globales de tema:
- `--text-primary` / `--text-secondary`
- `--bg-primary` / `--bg-secondary` / `--bg-hover`
- `--link-color` / `--link-color-alpha`
- `--border-color`
- `--status-success` / `--status-warning` / `--status-error` / `--status-info`

---

## 🧭 Navegación

### Topbar
Se agregó un nuevo enlace en el menú principal:
- **"Visualización"** → `/employees`

Acceso rápido desde cualquier página del sistema.

### Sidebar
Cuando estás en `/employees/*`:
- Aparece un sidebar con la sección "Visualización"
- Única opción: "Empleados"

### Navegación interna
- Desde listado → Detalle del empleado
- Desde detalle → Vista de Día / Vista de Timeline
- Desde vista de Día → Vista de Timeline
- Desde vista de Timeline → Resumen del Día
- Botones de retroceso ("← Volver a...")

---

## 🔧 Características Técnicas

### Estados de Carga

Cada componente maneja tres estados:

1. **Loading** - Spinner/mensaje de carga
2. **Error** - Mensaje de error controlado
3. **Empty** - Sin datos disponibles

```tsx
if (loading) return <div className="asistencia-loading">Cargando...</div>;
if (error) return <div className="asistencia-error">{error}</div>;
if (employees.length === 0) return <div className="asistencia-empty">Sin datos</div>;
```

### Gestión de Errores

Los errores de API se capturan y muestran al usuario de forma amigable:
```tsx
try {
  const data = await getEmployees(0, 100);
  setEmployees(data);
} catch (err) {
  setError(`Error cargando empleados: ${err instanceof Error ? err.message : 'Error desconocido'}`);
}
```

### Importaciones de Tipo (TypeScript)

Se utilizan importaciones de tipo con la palabra clave `type` para evitar errores con `verbatimModuleSyntax`:

```tsx
import { getEmployees } from '../../api';
import type { Employee } from '../../api';
```

---

## 📊 Datos que se Renderizan

### Listado de Empleados

| Campo | Fuente | Uso |
|-------|--------|-----|
| user_id | API | ID del empleado (mostrado como "ID") |
| name | API | Nombre completo |
| email | API | Email de contacto |
| department_name | API | Departamento asignado |
| active | API | Badge Activo/Inactivo |

### Detalle de Empleado

| Campo | Fuente | Uso |
|-------|--------|-----|
| name | API | Título principal |
| user_id | API | ID único |
| email | API | Contacto |
| phone | API | Teléfono principal |
| mobile_phone | API | Celular |
| ssn | API | Documento de identidad |
| gender | API | Género |
| birthday | API | Fecha de nacimiento |
| address | API | Dirección |
| active | API | Estado (Activo/Inactivo) |

### Resumen de Día

| Campo | Fuente | Uso |
|-------|--------|-----|
| date | API | Fecha |
| status | API | Estado (Worked/Incomplete/Absent) |
| worked_minutes | API | Total de minutos trabajados |
| late_minutes | API | Minutos de atraso |
| early_minutes | API | Minutos de salida temprana |
| overtime_minutes | API | Horas extra en minutos |
| check_in | API | Hora de entrada |
| check_out | API | Hora de salida |
| exception_reason | API | Observaciones |
| is_absent | API | Bandera de ausencia |

### Timeline

| Campo | Fuente | Uso |
|-------|--------|-----|
| blocks[] | `/timeline/` | Bloques de tiempo (start_time, end_time, duration_minutes, type) |
| summary | `/explanation/` | Resumen narrativo |
| anomalies | `/explanation/` | Lista de anomalías detectadas |
| recommendations | `/explanation/` | Recomendaciones |

---

## 🚀 Uso

### Acceder al módulo

1. **Desde el Topbar**: Click en "Visualización"
2. **Desde URL**: Ir a `http://localhost:3000/employees`

### Flujo típico

1. **Selecciona un empleado** de la lista
2. **Ve su información personal** en la tarjeta de detalle
3. **Elige una fecha** en el selector
4. **Ver Día** para resumen rápido
5. **Ver Timeline** para análisis detallado con bloques

### Búsqueda

En el listado, filtra empleados escribiendo:
- Nombre (ej: "Juan")
- ID (ej: "EMP001")
- Email (ej: "juan@")

---

## ✅ Principios Respetados

### ✓ Sin cálculos en frontend
- El frontend **no calcula** minutos de atraso
- No determina estado "Worked" vs "Incomplete"
- Solo renderiza lo que viene del API

### ✓ Sin interpretación IN/OUT
- No emparea punches manualmente
- No genera bloques de tiempo
- Los bloques vienen de `/timeline/`

### ✓ Sin cambios en backend
- Cero endpoints nuevos creados
- Cero cambios en backend Django
- Solo consume endpoints existentes

### ✓ Solo renderiza
- Listas simples
- Tablas de datos
- Bloques de información
- Badges de estado

### ✓ Sin formularios
- No hay edición
- No hay importación
- No hay creación de registros
- Solo lectura de datos

---

## 🔗 Endpoints Consumidos

| Método | Endpoint | Componente |
|--------|----------|-----------|
| GET | `/api/v1/employees/` | EmployeesList |
| GET | `/api/v1/employees/{id}` | EmployeeDetail, DayView, TimelineView |
| GET | `/api/v1/attendance/reports/daily/` | DayView |
| GET | `/api/v1/attendance/{id}/timeline/{date}/` | TimelineView |
| GET | `/api/v1/attendance/{id}/explanation/{date}/` | TimelineView |

---

## 📱 Responsive Design

- ✓ Desktop (1200px+)
- ✓ Tablet (768px - 1199px)
- ✓ Mobile (< 768px)

En dispositivos móviles:
- Tablas se adaptan a dos columnas
- Botones ocupan ancho completo
- Navegación es más compacta

---

## 🐛 Troubleshooting

### "Error cargando empleados"
- Verificar que el backend está corriendo en `http://127.0.0.1:9000`
- Verificar que hay empleados en la base de datos
- Revisar la consola del navegador (DevTools → Console)

### "Sin datos disponibles"
- Selecciona otra fecha si el empleado no tiene registros ese día
- Verifica que el empleado tiene logs de asistencia

### Componente en blanco
- Revisar que el token está en `sessionStorage` (DEV: Auth disabled)
- Revisar errores en console
- Forzar recarga (F5)

### Estilos no se aplican
- Verificar que `asistencia.css` está en el mismo folder que los componentes
- Verificar que el CSS tiene variables globales disponibles

---

## 📝 Estructura de Carpetas

```
frontend/src/
├── pages/
│   └── asistencia/
│       ├── EmployeesList.tsx      ← Listado
│       ├── EmployeeDetail.tsx      ← Detalle
│       ├── DayView.tsx             ← Vista de Día
│       ├── TimelineView.tsx        ← Vista de Timeline
│       └── asistencia.css          ← Estilos
├── App.tsx                         ← Rutas actualizadas
└── components/
    └── layout/
        ├── Topbar.tsx              ← Nav actualizado
        └── Sidebar.tsx             ← Sidebar actualizado
```

---

## 🎓 Aprendizajes

### Versión Alfa - Congelada
Este módulo fue desarrollado cumpliendo:
- ✓ Sin endpoints nuevos
- ✓ Sin cambios en backend
- ✓ Solo consumo de endpoints existentes
- ✓ Renderizado simple y limpio

### Base para futuro
Las rutas y componentes creados son la base para:
- UI definitiva en FASE B
- Funcionalidades de exportación
- Filtros avanzados
- Dashboard personalizado

---

## 📞 Contacto

Si encuentras issues:
1. Revisa errores en console (DevTools)
2. Verifica que backend está corriendo
3. Comprueba connectivity a `/api/v1/employees/`
4. Revisa logs del backend Django

---

**Versión**: 0.3.1-Alpha  
**Fecha**: Feb 4, 2026  
**Estado**: Congelado - Solo lectura, visualización end-to-end funcional
