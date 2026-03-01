# 📋 AUDITORÍA DE INTEGRACIÓN UI - SRTime-Django

**Fecha:** 2026-02-05  
**Objetivo:** Plan para extraer patrones UI de Employee-Management-System e integrarlos en srtime-django frontend  
**Scope:** Solo UI/UX - sin cambios en backend Django ni lógica de negocio  
**Estado:** 📝 En Planificación

---

## 📍 TABLA DE CONTENIDOS

1. [Análisis Actual](#análisis-actual)
2. [Componentes a Extraer](#componentes-a-extraer)
3. [Mapeo de Rutas y Endpoints](#mapeo-de-rutas-y-endpoints)
4. [Estructura de Directorios](#estructura-de-directorios)
5. [Plan por Sprints](#plan-por-sprints)
6. [Componentes Base a Crear](#componentes-base-a-crear)
7. [Ejemplos de Refactorización](#ejemplos-de-refactorización)
8. [Lista de No-Hacer](#lista-de-no-hacer)
9. [Timeline](#timeline)
10. [Checklist](#checklist)

---

## 🔍 ANÁLISIS ACTUAL

### SRTime-Django Frontend (Estado Actual)

**Stack Tecnológico:**
- ✅ TypeScript + React 18 + Vite
- ✅ Tailwind CSS
- ✅ React Router v6
- ✅ Axios con API client tipado
- ✅ Arquitectura modular por dominio

**Componentes Existentes:**
- `DataGrid.tsx` - Tabla base sin tipos genéricos
- `PageToolbar.tsx` - Barra de herramientas
- `ConfirmDialog.tsx` - Confirmación genérica
- `Modal.tsx` - Modal base
- Componentes por módulo (personnel, asistencia, organization, system)

**Estructura Actual (funcional pero mejorable):**
- Páginas monolíticas con mucha lógica
- Componentes no reutilizables
- Falta de abstracción en tablas/listas
- Styling inconsistente

**Endpoints disponibles en Backend:**

> Convención de este repo: el frontend es estático y lo sirve Django; usar endpoints relativos con `API_PREFIX` configurable (default: `/api/v1`).

```
GET {API_PREFIX}/companies/
GET {API_PREFIX}/positions/
GET {API_PREFIX}/zones/
GET {API_PREFIX}/departments/
GET {API_PREFIX}/employees/
GET {API_PREFIX}/devices/
GET {API_PREFIX}/shifts/
GET {API_PREFIX}/timetables/
GET {API_PREFIX}/leaves/
GET {API_PREFIX}/holidays/
GET {API_PREFIX}/daily-attendance/
```

---

### Employee-Management-System (Referencia Externa)

**Stack Tecnológico:**
- JavaScript + React 18 + Vite
- Tailwind CSS
- React Router v6
- Redux (innecesario para nuestro caso)
- Shadcn/ui components

**Componentes Reutilizables Valiosos:**
- `ListWrapper.jsx` - Contenedor con borde y styling
- `HeadingBar.jsx` - Cabecera de tabla adaptativa
- `ListContainer.jsx` - Cuerpo de lista
- `ListItems.jsx` - Mapeo de elementos
- Componentes Shadcn: Button, Card, Tabs, Dialog, etc.

**Patrones a Copyar:**
- Layout responsivo con grid
- Componentes de tabla modular
- Estructura de diálogos/modales
- Tabs para navegación de categorías

---

## 🧩 COMPONENTES A EXTRAER

### Mapeo Detallado

| Componente EMS | Ubicación | Tipo | Uso en SRTime | Adaptación | Prioridad |
|---|---|---|---|---|---|
| `ListWrapper` | common/Dashboard | Wrapper | Contenedor de tablas | TypeScript + genérico | 🔴 Alta |
| `HeadingBar` | common/Dashboard | Componente | Cabecera de tablas | Tipos genéricos `T` | 🔴 Alta |
| `ListContainer` | common/Dashboard | Wrapper | Body de lista | Refactorizar como `TableBody` | 🔴 Alta |
| `ListItems` | common/Dashboard | Render | Mapeo de elementos | Usar `Column<T>` tipado | 🔴 Alta |
| `Table` (shadcn) | ui/table.jsx | Primitivo | Referencia de estructura | Copiar y adaptar | 🟠 Media |
| `Button` (shadcn) | ui/button.jsx | Primitivo | Botones base | Ya existe similar | 🟢 Baja |
| `Card` (shadcn) | ui/card.jsx | Primitivo | Cards de info | Copiar para EntityCard | 🟠 Media |
| `Dialog` (shadcn) | ui/dialog.jsx | Primitivo | Modales | Usar para EntityModal | 🔴 Alta |
| `Tabs` (shadcn) | ui/tabs.jsx | Navegación | Vistas alternas | Copiar para DepartmentTabs | 🟠 Media |
| `Loading` | common/loading.jsx | Componente | Indicador de carga | Ya existe, mejorar | 🟢 Baja |

---

## 🗺️ MAPEO DE RUTAS Y ENDPOINTS

### Módulo: Personnel (Recursos Humanos)

| Ruta | Endpoint Backend | Página Actual | Mejora | Estado | Componentes |
|---|---|---|---|---|---|
| `/personnel/employees` | `GET /employees/` | ✅ Existe | Usar GenericTable | 📝 En Planificación | EmployeeTable |
| `/personnel/departments` | `GET /departments/` | ✅ Existe | Mejorar con Tabs | 📝 En Planificación | DepartmentTabs |

**Datos reales esperados:**
- Employees: id, user_id, name, email, department, position, hire_date, phone
- Departments: id, name, code, company, employees (relación)

**Restricciones:**
- ❌ GET únicamente (por ahora)
- ❌ Sin formularios POST/PUT activos
- ✅ Placeholder para funcionalidad futura

---

### Módulo: Organization (Catálogos)

| Ruta | Endpoint Backend | Estado | Acción | Componentes |
|---|---|---|---|---|
| `/organization/companies` | `GET /companies/` | 📝 Planificado | Crear nueva página | CompanyList, CompanyCard |
| `/organization/positions` | `GET /positions/` | 📝 Planificado | Crear nueva página | PositionList |
| `/organization/zones` | `GET /zones/` | 📝 Planificado | Crear nueva página | ZoneList |

**Nota:** Todas las vistas serán de **lectura solamente**, con placeholders para POST/PUT

---

### Módulo: Asistencia (Turnos y Horarios)

| Ruta | Endpoint Backend | Página Actual | Mejora | Componentes |
|---|---|---|---|---|
| `/asistencia/devices` | `GET /devices/` | ✅ DeviceList | Usar Cards + Grid | DeviceCard |
| `/asistencia/shifts` | `GET /shifts/` | 📝 Planificado | Crear tabla | ShiftTable |
| `/asistencia/timetables` | `GET /timetables/` | 📝 Planificado | Grid responsivo | TimetableGrid |
| `/asistencia/leaves` | `GET /leaves/` | 📝 Planificado | Tabla simple | LeavesTable |
| `/asistencia/holidays` | `GET /holidays/` | 📝 Planificado | Tabla simple | HolidaysTable |

---

## 📁 ESTRUCTURA DE DIRECTORIOS

### Árbol de Directorios Propuesto

```
src/
├── components/
│   ├── ui/
│   │   ├── TableComponents/
│   │   │   ├── index.ts
│   │   │   ├── TableCard.tsx          ← [NUEVO] Contenedor de tabla
│   │   │   ├── GenericTable.tsx       ← [NUEVO] Tabla tipada configurable
│   │   │   ├── TableRow.tsx           ← [NUEVO] Fila genérica
│   │   │   └── TableHeader.tsx        ← [NUEVO] Encabezado genérico
│   │   ├── Forms/
│   │   │   ├── index.ts
│   │   │   ├── EntityModal.tsx        ← [NUEVO] Modal genérico para entidades
│   │   │   ├── FormField.tsx          ← [NUEVO] Campo de formulario tipado
│   │   │   └── SubmitButton.tsx       ← [NUEVO] Botón de envío
│   │   ├── Cards/
│   │   │   ├── index.ts
│   │   │   ├── EntityCard.tsx         ← [NUEVO] Card reutilizable
│   │   │   ├── StatCard.tsx           ← [NUEVO] Card para estadísticas
│   │   │   └── InfoCard.tsx           ← [NUEVO] Card para información
│   │   ├── Breadcrumbs.tsx            ← [EXISTENTE]
│   │   ├── ConfirmationModal.tsx      ← [EXISTENTE]
│   │   ├── ConfirmDialog.tsx          ← [EXISTENTE]
│   │   ├── DataGrid.tsx               ← [MEJORAR] Reemplazar por GenericTable
│   │   ├── JobProgressModal.tsx       ← [EXISTENTE]
│   │   ├── Modal.tsx                  ← [EXISTENTE]
│   │   ├── PageToolbar.tsx            ← [EXISTENTE]
│   │   ├── ThemeToggle.tsx            ← [EXISTENTE]
│   │   └── Toast/                     ← [EXISTENTE]
│   ├── personnel/
│   │   ├── index.ts
│   │   ├── EmployeeTable.tsx          ← [NUEVO] Tabla tipada de empleados
│   │   ├── EmployeeCard.tsx           ← [NUEVO] Card individual de empleado
│   │   ├── EmployeeModal.tsx          ← [NUEVO] Modal para ver/editar empleado
│   │   ├── DepartmentTabs.tsx         ← [NUEVO] Tabs por departamento
│   │   └── DepartmentList.tsx         ← [NUEVO] Lista de departamentos
│   ├── organization/
│   │   ├── index.ts
│   │   ├── CompanyList.tsx            ← [NUEVO] Tabla de empresas
│   │   ├── CompanyCard.tsx            ← [NUEVO] Card de empresa
│   │   ├── PositionList.tsx           ← [NUEVO] Tabla de puestos
│   │   ├── ZoneList.tsx               ← [NUEVO] Tabla de zonas
│   │   └── CatalogCard.tsx            ← [NUEVO] Card genérico para catálogos
│   ├── asistencia/
│   │   ├── index.ts
│   │   ├── DeviceCard.tsx             ← [NUEVO] Card mejorada para dispositivo
│   │   ├── ShiftTable.tsx             ← [NUEVO] Tabla de turnos
│   │   ├── TimetableGrid.tsx          ← [NUEVO] Grid de horarios
│   │   ├── LeaveTable.tsx             ← [NUEVO] Tabla de ausencias
│   │   └── HolidayTable.tsx           ← [NUEVO] Tabla de feriados
│   ├── common/
│   │   ├── index.ts
│   │   ├── PlaceholderSection.tsx     ← [NUEVO] Section para placeholders POST/PUT
│   │   ├── LoadingSpinner.tsx         ← [EXISTENTE - mejorar]
│   │   └── ErrorBoundary.tsx          ← [EXISTENTE]
│   ├── layout/
│   │   ├── MainLayout.tsx             ← [EXISTENTE]
│   │   └── ...
│   └── auth/
│       └── ...
├── pages/
│   ├── personnel/
│   │   ├── Employees.tsx              ← [MEJORAR] Usar GenericTable
│   │   ├── Departments.tsx            ← [MEJORAR] Usar DepartmentTabs
│   │   └── index.ts
│   ├── organization/
│   │   ├── index.ts
│   │   ├── Company.tsx                ← [NUEVO] Página de empresas
│   │   ├── Positions.tsx              ← [NUEVO] Página de puestos
│   │   ├── Zones.tsx                  ← [NUEVO] Página de zonas
│   │   └── index.ts
│   ├── asistencia/
│   │   ├── Shifts.tsx                 ← [MEJORAR] Usar ShiftTable
│   │   ├── Timetables.tsx             ← [MEJORAR] Usar TimetableGrid
│   │   ├── Leaves.tsx                 ← [NUEVO] Tabla de ausencias
│   │   ├── Holidays.tsx               ← [NUEVO] Tabla de feriados
│   │   ├── DeviceList.tsx             ← [MEJORAR] Usar Grid de DeviceCards
│   │   └── index.ts
│   └── ...
├── types/
│   ├── index.ts
│   ├── personnel.ts                   ← [NUEVO] Interfaces para Personal
│   ├── organization.ts                ← [NUEVO] Interfaces para Organización
│   ├── asistencia.ts                  ← [NUEVO] Interfaces para Asistencia
│   └── ui.ts                          ← [NUEVO] Interfaces de UI genéricas
├── hooks/
│   ├── index.ts
│   ├── useTable.ts                    ← [NUEVO] Hook para manejar tablas
│   ├── useModal.ts                    ← [NUEVO] Hook para manejar modales
│   ├── useFetch.ts                    ← [NUEVO] Hook para llamadas API
│   └── ...
├── api.ts                             ← [MEJORAR] Ampliar con interfaces y endpoints
├── App.tsx                            ← [MEJORAR] Agregar rutas nuevas
└── main.tsx
```

---

## 🚀 PLAN POR SPRINTS

### 🎯 SPRINT 1: Componentes Base Tipados (Semana 1)

**Objetivo:** Crear la infraestructura de componentes reutilizables

#### Tarea 1.1: Crear `TableCard.tsx`

Ubicación: `src/components/ui/TableComponents/TableCard.tsx`

```typescript
/**
 * TableCard: Contenedor reutilizable para tablas/listas
 * Reemplaza: ListWrapper de EMS
 * Props:
 *   - title: string (título)
 *   - description?: string (descripción)
 *   - children: React.ReactNode (contenido)
 *   - actions?: React.ReactNode (botones de acción)
 *   - className?: string (clases Tailwind adicionales)
 * 
 * Ejemplo:
 *   <TableCard 
 *     title="Empleados" 
 *     description="Lista de todos los empleados"
 *     actions={<AddButton />}
 *   >
 *     <GenericTable data={employees} columns={columns} />
 *   </TableCard>
 */
```

**Requerimientos:**
- ✅ Borde azul similar a EMS (adaptado a Tailwind)
- ✅ Header con título y descripción
- ✅ Slot para acciones (botón agregar, etc)
- ✅ Responsivo (padding adaptativo)

---

#### Tarea 1.2: Crear `GenericTable.tsx`

Ubicación: `src/components/ui/TableComponents/GenericTable.tsx`

```typescript
/**
 * GenericTable: Tabla tipada y configurable
 * Reemplaza: ListContainer + ListItems + HeadingBar de EMS
 * 
 * Props:
 *   - data: T[] (datos a mostrar)
 *   - columns: Column<T>[] (definición de columnas)
 *   - onRowClick?: (item: T) => void
 *   - loading?: boolean
 *   - pagination?: boolean
 *   - sortable?: boolean
 * 
 * Column Interface:
 *   - key: keyof T
 *   - label: string
 *   - render?: (value, item) => ReactNode
 *   - width?: string
 *   - hidden?: boolean (ocular en mobile)
 *   - sortable?: boolean
 *   - align?: 'left' | 'center' | 'right'
 * 
 * Ejemplo:
 *   const columns: Column<Employee>[] = [
 *     { key: 'name', label: 'Nombre', sortable: true },
 *     { key: 'email', label: 'Email', hidden: true },
 *     { 
 *       key: 'department', 
 *       label: 'Depto',
 *       render: (dept) => dept?.name || 'N/A'
 *     },
 *   ];
 */
```

**Requerimientos:**
- ✅ Renderizado flexible de columnas
- ✅ Responsive (ocultar columnas en mobile con `hidden`)
- ✅ Función `render` personalizada por columna
- ✅ Soporte para ordenamiento (opcional)
- ✅ Manejo de casos vacíos
- ✅ Tipado completo con TypeScript

---

#### Tarea 1.3: Crear `EntityModal.tsx`

Ubicación: `src/components/ui/Forms/EntityModal.tsx`

```typescript
/**
 * EntityModal: Modal genérico para crear/editar entidades
 * Props:
 *   - isOpen: boolean
 *   - onClose: () => void
 *   - title: string
 *   - entity?: T (entidad a editar, undefined = crear)
 *   - fields: FieldConfig[]
 *   - onSubmit: (data: T) => Promise<void>
 *   - isLoading?: boolean
 *   - readOnly?: boolean (para placeholders)
 * 
 * FieldConfig Interface:
 *   - name: keyof T
 *   - label: string
 *   - type: 'text' | 'email' | 'number' | 'select' | 'textarea'
 *   - required?: boolean
 *   - disabled?: boolean
 *   - options?: { value, label }[] (para select)
 *   - validation?: (value) => string | undefined
 */
```

**Requerimientos:**
- ✅ Soporte completo de tipos de campos
- ✅ Validación por campo
- ✅ Estado cargando
- ✅ Modo read-only para placeholders
- ✅ Integración con API

---

#### Tarea 1.4: Ampliar `api.ts` con Interfaces

Ubicación: `src/api.ts`

**Agregar interfaces para:**
- Company
- Position
- Zone
- Shift
- Timetable
- Leave
- Holiday
- DailyAttendance

**Agregar funciones GET:**
```typescript
export const getCompanies = () => api.get<Company[]>('/companies/')
export const getPositions = () => api.get<Position[]>('/positions/')
export const getZones = () => api.get<Zone[]>('/zones/')
export const getShifts = () => api.get<Shift[]>('/shifts/')
export const getTimetables = () => api.get<Timetable[]>('/timetables/')
export const getLeaves = () => api.get<Leave[]>('/leaves/')
export const getHolidays = () => api.get<Holiday[]>('/holidays/')
```

---

#### Tarea 1.5: Crear `PlaceholderSection.tsx`

Ubicación: `src/components/common/PlaceholderSection.tsx`

```typescript
/**
 * PlaceholderSection: Sección de placeholder para funcionalidad futura
 * Props:
 *   - title: string
 *   - message: string
 *   - icon?: React.ReactNode
 *   - action?: { label: string, onClick: () => void }
 * 
 * Uso:
 *   <PlaceholderSection 
 *     title="Crear nuevo empleado"
 *     message="Funcionalidad POST: En desarrollo"
 *     icon={<Plus />}
 *   />
 */
```

---

### 🎯 SPRINT 2: Módulo Personnel (Semana 2)

**Objetivo:** Mejorar vistas de Empleados y Departamentos

#### Tarea 2.1: Refactorizar `Employees.tsx`

Ubicación: `src/pages/personnel/Employees.tsx`

**Cambios:**
- ✅ Reemplazar DataGrid por GenericTable
- ✅ Usar TableCard como contenedor
- ✅ Agregar botón "Agregar Empleado" (placeholder)
- ✅ Mejorar responsividad

**Ejemplo antes/después:**

```typescript
// ANTES: ~70 líneas con lógica manual
export const Employees = () => {
  const [employees, setEmployees] = useState([]);
  // ... más estado
  return (
    <div>
      {/* UI manual */}
    </div>
  );
};

// DESPUÉS: ~30 líneas usando componentes
export const Employees: React.FC = () => {
  const [employees, setEmployees] = useState<Employee[]>([]);

  useEffect(() => {
    getEmployees().then(setEmployees);
  }, []);

  const columns: Column<Employee>[] = [
    { key: 'name', label: 'Nombre', sortable: true },
    { key: 'email', label: 'Email', hidden: true },
  ];

  return (
    <TableCard 
      title="Empleados"
      actions={<Button>+ Agregar</Button>}
    >
      <GenericTable data={employees} columns={columns} />
    </TableCard>
  );
};
```

#### Tarea 2.2: Crear `DepartmentTabs.tsx`

Ubicación: `src/components/personnel/DepartmentTabs.tsx`

**Inspiración:** `departmenttabs.jsx` de EMS, pero tipado y simplificado

**Características:**
- ✅ Tabs para seleccionar departamento
- ✅ Vista "Todos" por defecto
- ✅ Mostrar empleados por departamento
- ✅ Placeholder para agregar empleados a departamento

#### Tarea 2.3: Mejorar `Departments.tsx`

Ubicación: `src/pages/personnel/Departments.tsx`

**Cambios:**
- ✅ Usar DepartmentTabs como componente principal
- ✅ Integrar con datos reales
- ✅ Agregar funcionalidad de búsqueda

---

### 🎯 SPRINT 3: Módulo Organization (Semana 3)

**Objetivo:** Crear vistas de catálogos

#### Tarea 3.1: Crear `Company.tsx`

Ubicación: `src/pages/organization/Company.tsx`

```typescript
export const Company: React.FC = () => {
  const [companies, setCompanies] = useState<Company[]>([]);

  useEffect(() => {
    getCompanies().then(setCompanies).catch(console.error);
  }, []);

  const columns: Column<Company>[] = [
    { key: 'name', label: 'Empresa', sortable: true },
    { key: 'code', label: 'Código', hidden: true },
    { key: 'website', label: 'Sitio Web' },
  ];

  return (
    <TableCard 
      title="Empresas"
      description="Catálogo de empresas"
    >
      <GenericTable data={companies} columns={columns} />
      <PlaceholderSection 
        title="Crear nueva empresa"
        message="Funcionalidad POST: Scheduled para próximas releases"
      />
    </TableCard>
  );
};
```

#### Tarea 3.2: Crear `Positions.tsx`

Ubicación: `src/pages/organization/Positions.tsx`

**Mismo patrón que Company.tsx**

Columnas: name, code, description

#### Tarea 3.3: Crear `Zones.tsx`

Ubicación: `src/pages/organization/Zones.tsx`

**Mismo patrón que Company.tsx**

Columnas: name, code, description

#### Tarea 3.4: Actualizar rutas en `App.tsx`

Agregar:
```typescript
<Route path="organization/companies" element={<Company />} />
<Route path="organization/positions" element={<Positions />} />
<Route path="organization/zones" element={<Zones />} />
```

---

### 🎯 SPRINT 4: Módulo Asistencia (Semana 4)

**Objetivo:** Mejorar vistas de dispositivos, turnos y horarios

#### Tarea 4.1: Mejorar `DeviceList.tsx`

Ubicación: `src/pages/asistencia/DeviceList.tsx`

**Cambios:**
- ✅ Usar Grid de Cards en lugar de tabla
- ✅ Crear `DeviceCard.tsx` mejorada
- ✅ Mostrar estado de conexión
- ✅ Información de usuarios/huellas

#### Tarea 4.2: Crear `ShiftTable.tsx`

Ubicación: `src/components/asistencia/ShiftTable.tsx`

Columnas:
- name
- start_time
- end_time
- break_duration

#### Tarea 4.3: Crear `TimetableGrid.tsx`

Ubicación: `src/components/asistencia/TimetableGrid.tsx`

**Características:**
- ✅ Grid de horarios
- ✅ Vista por empleado
- ✅ Información de turnos

#### Tarea 4.4: Crear `LeaveTable.tsx` y `HolidayTable.tsx`

Siguiendo el mismo patrón

#### Tarea 4.5: Actualizar rutas en `App.tsx`

Agregar:
```typescript
<Route path="asistencia/shifts" element={<Shifts />} />
<Route path="asistencia/timetables" element={<Timetables />} />
<Route path="asistencia/leaves" element={<Absences />} />
<Route path="asistencia/holidays" element={<Holidays />} />
```

---

### 🎯 SPRINT 5: Integración y Refinamiento (Semana 5)

**Objetivo:** Polish, testing y documentación

#### Tarea 5.1: Testing responsivo

- ✅ Mobile (320px - 480px)
- ✅ Tablet (768px - 1024px)
- ✅ Desktop (1024px+)

#### Tarea 5.2: Ajustes de UX

- ✅ Asegurar que ocultar columnas funciona bien
- ✅ Mejorar estados de carga
- ✅ Validar mensajes de error

#### Tarea 5.3: Documentación

- ✅ Comentarios en componentes
- ✅ Ejemplos de uso
- ✅ Guía de estilos

#### Tarea 5.4: Performance

- ✅ Lazy loading si es necesario
- ✅ Memoization en componentes reutilizables

---

## 🧩 COMPONENTES BASE A CREAR

### 1. TableCard.tsx

**Tipo:** Wrapper/Layout Component  
**Reemplaza:** `ListWrapper` (EMS)  
**Responsabilidad:** Contenedor estilizado para tablas

**Props:**
```typescript
interface TableCardProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
  actions?: React.ReactNode;
  footer?: React.ReactNode;
}
```

**Estilos esperados:**
- Border: `border-2 border-blue-700`
- Padding: `p-4`
- Border-radius: `rounded-lg`
- Responsive: Padding adaptativo

---

### 2. GenericTable.tsx

**Tipo:** Data Display Component  
**Reemplaza:** `ListContainer + ListItems + HeadingBar` (EMS)  
**Responsabilidad:** Renderizar datos en tabla tipada

**Props:**
```typescript
interface Column<T> {
  key: keyof T;
  label: string;
  render?: (value: any, item: T, index?: number) => React.ReactNode;
  width?: string;
  hidden?: boolean;
  sortable?: boolean;
  align?: 'left' | 'center' | 'right';
}

interface GenericTableProps<T extends { id?: number }> {
  data: T[];
  columns: Column<T>[];
  onRowClick?: (item: T) => void;
  loading?: boolean;
  empty?: React.ReactNode;
  className?: string;
}
```

**Ejemplo de uso:**
```typescript
const columns: Column<Employee>[] = [
  { 
    key: 'name', 
    label: 'Nombre Completo',
    render: (name) => <span className="font-semibold">{name}</span>,
    sortable: true 
  },
  { 
    key: 'email', 
    label: 'Email',
    hidden: true // Oculto en mobile
  },
  {
    key: 'department',
    label: 'Departamento',
    render: (dept) => dept?.name || 'N/A'
  },
  {
    key: 'id',
    label: 'Acciones',
    render: (id, item) => (
      <div className="flex gap-2">
        <ViewButton onClick={() => handleView(item)} />
        <EditButton onClick={() => handleEdit(item)} disabled />
      </div>
    )
  }
];

<GenericTable 
  data={employees} 
  columns={columns}
  onRowClick={(emp) => navigate(`/employees/${emp.id}`)}
/>
```

---

### 3. EntityModal.tsx

**Tipo:** Form Component  
**Reemplaza:** Varias dialog boxes (EMS)  
**Responsabilidad:** Modal genérico para crear/editar entidades

**Props:**
```typescript
interface FieldConfig {
  name: string;
  label: string;
  type: 'text' | 'email' | 'number' | 'tel' | 'date' | 'select' | 'textarea';
  required?: boolean;
  disabled?: boolean;
  placeholder?: string;
  options?: Array<{ value: string | number; label: string }>;
  validation?: (value: any) => string | undefined;
  helperText?: string;
}

interface EntityModalProps<T> {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: T) => Promise<void>;
  title: string;
  entity?: Partial<T>;
  fields: FieldConfig[];
  isLoading?: boolean;
  readOnly?: boolean;
  submitLabel?: string;
  cancelLabel?: string;
}
```

**Estados:**
- `isOpen` = true: Modal visible
- `isLoading` = true: Deshabilitando botones durante submit
- `readOnly` = true: Campos deshabilitados (placeholders futuros)

---

### 4. PlaceholderSection.tsx

**Tipo:** UI Component  
**Responsabilidad:** Mostrar áreas de funcionalidad futura

**Props:**
```typescript
interface PlaceholderSectionProps {
  title: string;
  message: string;
  icon?: React.ReactNode;
  action?: {
    label: string;
    onClick: () => void;
    disabled?: boolean;
  };
  className?: string;
}
```

**Ejemplo:**
```typescript
<PlaceholderSection 
  title="Crear nuevo empleado"
  message="La funcionalidad de creación está plannificada para la próxima release"
  icon={<Plus className="w-8 h-8 text-blue-400" />}
  action={{
    label: "Ver documentación",
    onClick: () => window.open('/docs')
  }}
/>
```

---

### 5. Custom Hooks

#### `useTable.ts`

```typescript
interface UseTableOptions<T> {
  initialData?: T[];
  onSort?: (key: keyof T, direction: 'asc' | 'desc') => void;
  pageSize?: number;
}

export const useTable = <T extends { id?: number }>(
  options: UseTableOptions<T> = {}
) => {
  const [data, setData] = useState(options.initialData || []);
  const [sortKey, setSortKey] = useState<keyof T | null>(null);
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');
  const [page, setPage] = useState(0);

  const handleSort = (key: keyof T) => {
    const newDir = sortKey === key && sortDir === 'asc' ? 'desc' : 'asc';
    setSortKey(key);
    setSortDir(newDir);
    options.onSort?.(key, newDir);
  };

  return { data, setData, sortKey, sortDir, handleSort, page, setPage };
};
```

#### `useModal.ts`

```typescript
export const useModal = () => {
  const [isOpen, setIsOpen] = useState(false);

  return {
    isOpen,
    open: () => setIsOpen(true),
    close: () => setIsOpen(false),
    toggle: () => setIsOpen(x => !x),
  };
};
```

---

## 📝 EJEMPLOS DE REFACTORIZACIÓN

### Ejemplo 1: Refactorizar Employees.tsx

**ANTES:**
```typescript
// src/pages/personnel/Employees.tsx (70+ líneas)
export const Employees: React.FC = () => {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [departments, setDepartments] = useState<DepartmentNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingEmp, setEditingEmp] = useState<Employee | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [empToDelete, setEmpToDelete] = useState<number | null>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [empData, deptData] = await Promise.all([
        getEmployees(0, 2000), 
        getDepartments()
      ]);
      setEmployees(empData);
      setDepartments(sortDepartmentsTree(deptData));
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Más lógica...

  return (
    <div>
      {/* UI manual */}
    </div>
  );
};
```

**DESPUÉS:**
```typescript
// src/pages/personnel/Employees.tsx (30 líneas)
export const Employees: React.FC = () => {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getEmployees(0, 2000)
      .then(setEmployees)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const columns: Column<Employee>[] = [
    { key: 'name', label: 'Nombre', sortable: true },
    { key: 'email', label: 'Email', hidden: true },
    { 
      key: 'department', 
      label: 'Departamento',
      render: (dept) => dept?.name || 'Sin asignar'
    },
    { 
      key: 'position', 
      label: 'Posición',
      render: (pos) => pos?.name || '-'
    },
  ];

  return (
    <TableCard 
      title="Empleados"
      description="Gestión de personal"
      actions={<Button>+ Agregar</Button>}
    >
      {loading ? (
        <LoadingSpinner />
      ) : (
        <GenericTable data={employees} columns={columns} />
      )}
      <PlaceholderSection 
        title="Agregar nuevo empleado"
        message="Funcionalidad en desarrollo"
      />
    </TableCard>
  );
};
```

**Beneficios:**
- ✅ 53% menos código
- ✅ Más legible
- ✅ Reutilizable
- ✅ Mantenimiento más fácil
- ✅ Tipado completo

---

### Ejemplo 2: Nueva página Organization/Companies

```typescript
// src/pages/organization/Company.tsx
import { useState, useEffect } from 'react';
import { getCompanies, type Company } from '../../api';
import { TableCard, GenericTable, PlaceholderSection } from '../../components';
import { Column } from '../../components/ui/TableComponents/GenericTable';

export const Companies: React.FC = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCompanies()
      .then(setCompanies)
      .catch((err) => {
        console.error('Error cargando empresas:', err);
        // Toast o notificación de error
      })
      .finally(() => setLoading(false));
  }, []);

  const columns: Column<Company>[] = [
    { 
      key: 'name', 
      label: 'Empresa',
      sortable: true 
    },
    { 
      key: 'code', 
      label: 'Código',
      hidden: true 
    },
    { 
      key: 'website', 
      label: 'Sitio Web',
      render: (url) => url ? (
        <a href={url} target="_blank" className="text-blue-600 hover:underline">
          {url}
        </a>
      ) : '-'
    },
    { 
      key: 'address', 
      label: 'Dirección',
      hidden: true 
    },
  ];

  return (
    <TableCard title="Empresas" description="Catálogo organismos">
      {loading ? (
        <LoadingSpinner />
      ) : (
        <GenericTable 
          data={companies} 
          columns={columns}
          empty={<div className="text-center text-gray-500">Sin empresas registradas</div>}
        />
      )}
      <div className="mt-6">
        <PlaceholderSection 
          title="Crear nueva empresa"
          message="La funcionalidad de creación de empresas está planificada para futuras versiones"
          icon={<Building className="w-8 h-8 text-blue-400" />}
        />
      </div>
    </TableCard>
  );
};
```

---

## ❌ LISTA DE NO-HACER

### Componentes/Lógica a NO Copiar

| Elemento | Por qué | Alternativa |
|---|---|---|
| Redux (useDispatch, useSelector) | Overhead innecesario | useState + useContext |
| Lógica de autenticación | No entra en scope | PrivateRoute ya existe |
| useToast hook personalizado | Ya existe en el proyecto | Usar el existente |
| Loading.jsx de EMS | Versión propia más simple | LoadingSpinner mejorado |
| Lógica de PASSWORD RESET | Fuera de scope | Preservar actual |
| Componentes de SIGNUP | Fuera de scope | No aplica |
| Estilos hardcodeados | Usar Tailwind estándar | Theme consistente |
| Llamadas API a endpoint EMS | No existen en Django | Usar endpoint reales Django |
| Dialog boxes con acciones POST complejas | POST está disabled | Placeholders simples |
| Device filters complejos | No entra en scope | Implementar después |
| Paginación avanzada | Simplificar para MVP | Implementar en Sprint 2+ |

---

## 📅 TIMELINE

### Cronograma Propuesto

```
┌─────────────────────────────────────────────────────────────────┐
│ SPRINT 1 (Semana 1): Componentes Base                           │
├─────────────────────────────────────────────────────────────────┤
│ Día 1-2:  TableCard, GenericTable                               │
│ Día 3-4:  EntityModal, PlaceholderSection                       │
│ Día 5:    Testing + Aprobación                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ SPRINT 2 (Semana 2): Personnel Module                           │
├─────────────────────────────────────────────────────────────────┤
│ Día 1-2:  Refactorizar Employees.tsx                            │
│ Día 3-4:  DepartmentTabs + Departments.tsx                      │
│ Día 5:    Testing + Integration                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ SPRINT 3 (Semana 3): Organization Module                        │
├─────────────────────────────────────────────────────────────────┤
│ Día 1-2:  Companies, Positions, Zones pages                     │
│ Día 3:    Rutas en App.tsx                                      │
│ Día 4-5:  Testing responsivo                                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ SPRINT 4 (Semana 4): Asistencia Module                          │
├─────────────────────────────────────────────────────────────────┤
│ Día 1-2:  ShiftTable, TimetableGrid                             │
│ Día 3:    LeaveTable, HolidayTable                              │
│ Día 4-5:  Mejorar DeviceList con Cards                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ SPRINT 5 (Semana 5): Polish & Documentation                     │
├─────────────────────────────────────────────────────────────────┤
│ Día 1-2:  Testing responsivo (mobile/tablet/desktop)            │
│ Día 3:    Performance optimizations                             │
│ Día 4-5:  Documentación + Comentarios                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Phase 1: Estructura Base

- [ ] Crear carpeta `src/components/ui/TableComponents/`
- [ ] Crear carpeta `src/components/personnel/`
- [ ] Crear carpeta `src/components/organization/`
- [ ] Crear carpeta `src/components/asistencia/`
- [ ] Crear carpeta `src/types/`
- [ ] Crear carpeta `src/hooks/`

### Phase 2: Componentes Base

- [ ] Implementar `TableCard.tsx`
- [ ] Implementar `GenericTable.tsx` con tipos genéricos
- [ ] Implementar `EntityModal.tsx`
- [ ] Implementar `PlaceholderSection.tsx`
- [ ] Implementar `useTable.ts` hook
- [ ] Implementar `useModal.ts` hook
- [ ] Ampliar `api.ts` con nuevas interfaces

### Phase 3: Personnel Module

- [ ] Refactorizar `Employees.tsx`
- [ ] Crear `DepartmentTabs.tsx`
- [ ] Mejorar `Departments.tsx`
- [ ] Testing y validación

### Phase 4: Organization Module

- [ ] Crear `Company.tsx` página
- [ ] Crear `Positions.tsx` página
- [ ] Crear `Zones.tsx` página
- [ ] Agregar rutas a `App.tsx`
- [ ] Testing responsivo

### Phase 5: Asistencia Module

- [ ] Crear `ShiftTable.tsx`
- [ ] Crear `TimetableGrid.tsx`
- [ ] Crear `LeaveTable.tsx`
- [ ] Crear `HolidayTable.tsx`
- [ ] Mejorar `DeviceList.tsx` con Cards
- [ ] Agregar rutas a `App.tsx`

### Phase 6: Refinamiento

- [ ] Testing en mobile (320px-480px)
- [ ] Testing en tablet (768px-1024px)
- [ ] Testing en desktop (1024px+)
- [ ] Validar ocultar columnas
- [ ] Mejorar loading states
- [ ] Validar manejo de errores
- [ ] Documentar componentes
- [ ] Agregar ejemplos en README

### Phase 7: Deployment

- [ ] Code review
- [ ] Merge a rama principal
- [ ] Deploy a staging
- [ ] Testing en producción
- [ ] Documentación final

---

## 📊 MÉTRICAS DE ÉXITO

| KPI | Target | Actual |
|---|---|---|
| Reducción de líneas de código (~%) | -40% | Pendiente |
| Componentes reutilizables creados | 15+ | 0 |
| Cobertura de test (UI) | >80% | 0% |
| Nuevas páginas | 3+ | 0 |
| Time to implement (horas) | 30-40 | - |
| Mobile responsiveness | 100% | - |

---

## 📚 REFERENCIAS

### Employee-Management-System (Fuente)
- `common/Dashboard/ListDesigns.jsx` - Componentes de lista
- `common/Dashboard/departmenttabs.jsx` - Tabs component
- `ui/*.jsx` - Shadcn components
- `pages/HumanResources/Dashboard Childs/employeespage.jsx` - Patrón de página

### SRTime-Django (Target)
- `frontend/src/api.ts` - Cliente API
- `frontend/src/pages/` - Estructura de páginas
- `frontend/src/components/` - Componentes existentes
- `backend/core/urls.py` - Endpoints disponibles

---

## 🤝 DEPENDENCIAS

### Tecnologías Requeridas
- ✅ React 18+
- ✅ TypeScript 5+
- ✅ Tailwind CSS 3+
- ✅ Axios
- ✅ React Router v6

### Librerías Opcionales (No usadas en este plan)
- ❌ Redux (mantener simple con hooks)
- ❌ React Query (simple fetch hooks)
- ❌ Formik (validación inline)

---

## 🔗 RELACIONES ENTRE MÓDULOS

```
App.tsx
├── PersonnelLayout
│   ├── Employees (usa GenericTable)
│   └── Departments (usa DepartmentTabs)
├── OrganizationLayout
│   ├── Companies (usa GenericTable)
│   ├── Positions (usa GenericTable)
│   └── Zones (usa GenericTable)
└── AsistenciaLayout
    ├── DeviceList (usa Grid de Cards)
    ├── Shifts (usa GenericTable)
    ├── Timetables (usa TimetableGrid)
    ├── Leaves (usa GenericTable)
    └── Holidays (usa GenericTable)

Todos los módulos reutilizan:
├── TableCard (wrapper)
├── GenericTable (tablas tipadas)
├── EntityModal (modales genéricos)
├── PlaceholderSection (placeholders)
└── useTable, useModal hooks
```

---

## 📞 CONTACTO Y PREGUNTAS

**Preguntas frecuentes durante implementación:**

**Q1: ¿Qué pasa si los datos no coinciden?**  
A: Adaptar `Column<T>` render function. Ejemplo:
```typescript
{ 
  key: 'custom_field', 
  label: 'Mi Campo',
  render: (value, item) => {
    if (!value) return 'N/A';
    return <CustomRenderer value={value} />;
  }
}
```

**Q2: ¿Cómo agregar validación a EntityModal?**  
A: Usar callback de validación en FieldConfig:
```typescript
{
  name: 'email',
  label: 'Email',
  type: 'email',
  validation: (value) => {
    if (!value?.includes('@')) return 'Email inválido';
    return undefined;
  }
}
```

**Q3: ¿Cómo personalizar estilos?**  
A: Ampliar props con `className`:
```typescript
<TableCard 
  className="border-green-600"
  title="Custom"
/>
```

---

## 📝 NOTAS DE VERSIÓN

**v1.0 (Targeted)** - Integración de Patrones UI
- ✅ Componentes base tipados
- ✅ Módulo Personnel mejorado
- ✅ Módulo Organization creado
- ✅ Módulo Asistencia mejorado

**v1.1 (Future)** - Funcionalidad POST/PUT
- ⏳ Habilitar creación de entidades
- ⏳ Validar formularios complejos
- ⏳ Integrar permisos

**v1.2 (Future)** - Performance
- ⏳ Virtual scrolling para listas grandes
- ⏳ Lazy loading de módulos
- ⏳ Caché de datos

---

**Documento generado:** 2026-02-05  
**Versión:** 1.0  
**Estado:** 📝 Listo para implementación  
**Aprobación requerida:** Antes de Sprint 1
