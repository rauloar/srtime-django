# API Endpoints Reference

## Overview

El sistema utiliza Django REST Framework con un prefijo de ruta `/api/v1/` para todos los endpoints.

### Base URL
```
http://localhost:9000/api/v1/
```

---

## 🚨 PROBLEMAS COMUNES

### ❌ INCORRECTO
```
GET /employees/              ← Sirve el frontend (HTML)
GET /attendance/day/         ← Incorrecto (falta /api/v1/)
```

### ✅ CORRECTO
```
GET /api/v1/employees/       ← API endpoint
GET /api/v1/attendance/day/  ← Endpoint correcto
```

---

## Endpoint: `GET /api/v1/employees/`

### Descripción
Retorna lista de **todos los empleados activos** del sistema.

### Características
- ✅ Paginado automático (por defecto 50 registros por página)
- ✅ Incluye todos los campos: nombre, ID de usuario, departamento, etc.
- ✅ Datos **ESTÁTICOS** - No varía según el día o fecha

### Parámetros de Query
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `limit` | int | Registros por página (default: 50) |
| `offset` | int | Desplazamiento para paginación |
| `active` | bool | Filtrar por estado activo (true/false) |

### Ejemplo de Respuesta
```json
{
    "count": 54,
    "next": "http://localhost:9000/api/v1/employees/?page=2",
    "previous": null,
    "results": [
        {
            "id": 223,
            "user_id": "99999",
            "name": "99999 99999",
            "department": 22,
            "department_name": "04 a 13",
            "hire_date": "2018-05-24",
            "active": true,
            "email": null,
            "phone": null
        },
        {
            "id": 226,
            "user_id": "4",
            "name": "Alberto Avalos",
            "department": 14,
            "department_name": "Moldeo",
            "hire_date": "1977-10-15",
            "active": true
        }
    ]
}
```

### Status Codes
| Código | Descripción |
|--------|-------------|
| 200 | OK - Datos retornados correctamente |
| 401 | No autenticado |
| 500 | Error servidor |

### Casos de Uso
- ✅ Cargar lista de empleados para dropdown/select
- ✅ Mostrar tabla de empleados
- ✅ Filtros en reportes
- ✅ Inicializar UI con datos

### ❌ NO USAR PARA
- ❌ Obtener estado del día (usar `/attendance/day/`)
- ❌ Obtener registros de fichadas (usar `/attendance-logs/`)

---

## Endpoint: `GET /api/v1/attendance/day/`

### Descripción
Retorna el **estado de asistencia de UN EMPLEADO PARA UN DÍA ESPECÍFICO**.

Calcula automáticamente:
- Estado (Normal, Absent, Late, Partial, etc.)
- Minutos trabajados
- Hora entrada/salida detectadas
- Minutos de tardanza

### Parámetros (REQUERIDOS)
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `employee_id` | int | ID del empleado (de la tabla employees) |
| `date` | string | Fecha en formato ISO (YYYY-MM-DD) |

### Ejemplo de Llamada
```bash
GET /api/v1/attendance/day/?employee_id=223&date=2026-02-04
```

### Ejemplo de Respuesta
```json
{
    "employee_id": "223",
    "employee_name": "99999 99999",
    "date": "2026-02-04",
    "status": "Absent",
    "worked_minutes": 0,
    "check_in": null,
    "check_out": null,
    "late_minutes": 0,
    "logs": []
}
```

### Cálculo de Estado
El endpoint **busca registros de fichadas (logs) del día especificado** y calcula:

```python
if no logs:
    status = "Absent"  # Ausente - no fichó
elif check_in y check_out y worked_minutes >= expected:
    status = "Normal"  # Presentismo
elif check_in pero no check_out:
    status = "Incomplete"  # Não finalizó jornada
elif check_in con retraso:
    status = "Late"  # Llegó tarde
```

### Status Codes
| Código | Descripción |
|--------|-------------|
| 200 | OK |
| 400 | Parámetros faltantes o inválidos |
| 404 | Empleado no encontrado |
| 500 | Error servidor |

### Casos de Uso
- ✅ Obtener estado del día de un empleado
- ✅ Dashboard por empleado
- ✅ Reportes diarios
- ✅ Validar asistencia actual

---

## Endpoint: `GET /api/v1/attendance-logs/`

### Descripción
Retorna **registros de fichadas (logs)** con filtros por empleado, fecha, dispositivo, etc.

### Parámetros de Query
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `user_id` | string | ID del empleado a filtrar |
| `from_date` | string | Fecha inicio (ISO format) |
| `to_date` | string | Fecha fin (ISO format) |
| `device_id` | int | Filtrar por dispositivo |
| `limit` | int | Registros por página |
| `offset` | int | Desplazamiento |

### Ejemplo de Respuesta
```json
{
    "count": 97282,
    "next": "...",
    "results": [
        {
            "id": 485958,
            "user_id": "909",
            "timestamp": "2026-02-04T07:08:54-03:00",
            "status": 0,
            "status_label": "Entrada",
            "verify_mode": null,
            "verify_mode_label": null,
            "device_name": "ZKTimeNet Import"
        }
    ]
}
```

### Campos Importantes
| Campo | Descripción |
|-------|-------------|
| `status` | Código de estado (0=Entrada, 1=Salida, etc.) |
| `status_label` | Etiqueta traducida (desde backend) |
| `verify_mode` | Método verificación (1=Huella, 3=Contraseña, etc.) |
| `verify_mode_label` | Etiqueta de método (desde backend) |
| `timestamp` | Fecha/hora del registro |

---

## Endpoint: `GET /api/v1/daily-attendance/`

### Descripción
Retorna **asistencia diaria CALCULADA** (resumida por día).

### Parámetros
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `employee_id` | int | Filtrar por empleado |
| `date` | string | Filtrar por fecha |
| `status` | string | Filtrar por estado (Normal, Absent, Late, etc.) |

### Ejemplo de Respuesta
```json
{
    "count": 5400,
    "results": [
        {
            "id": 1234,
            "employee_id": 223,
            "employee_name": "99999 99999",
            "date": "2026-02-04",
            "status": "Absent",
            "status_info": {
                "code": "Absent",
                "label": "Absent",
                "display": "Ausente",
                "color": "#c62828",
                "color_dark": "#f87171",
                "icon": "x-circle"
            },
            "check_in": null,
            "check_out": null,
            "worked_minutes": 0,
            "late_minutes": 0,
            "early_minutes": 0,
            "overtime_minutes": 0
        }
    ]
}
```

---

## Endpoint: `GET /api/v1/enums/`

### Descripción
Retorna **todas las enumeraciones del sistema** - Definiciones de valores de estatus, modos de verificación, etc.

### Respuesta
```json
{
    "message": "API Enumerations - Source of truth for all enum values",
    "version": "1.0.0",
    "punch_status": {
        "0": {"code": 0, "label": "Entrada", "display": "Entrada"},
        "1": {"code": 1, "label": "Salida", "display": "Salida"},
        ...
    },
    "verify_mode": {
        "1": {"code": 1, "label": "Huella", "display": "Huella Dactilar"},
        "3": {"code": 3, "label": "Contraseña", "display": "Contraseña"},
        ...
    },
    "attendance_status": {
        "Normal": {"code": "Normal", "label": "Normal", "display": "Presentismo", ...},
        "Absent": {"code": "Absent", "label": "Absent", "display": "Ausente", ...},
        ...
    }
}
```

### Casos de Uso
- ✅ Inicializar UI con valores posibles
- ✅ Mapeo de códigos a etiquetas
- ✅ Colores para estados
- ✅ Source of truth para enumeraciones

---

## Endpoint: `GET /api/v1/dashboard/summary/`

### Descripcion
Retorna **resumen historico y datos maestros** para el Home del dashboard.
No usa datos en vivo ni captura del dia actual.

### Parametros de Query
| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `limit` | int | Cantidad de fechas historicas a retornar (default: 5) |

### Ejemplo de Respuesta
```json
{
    "message": "Dashboard summary (historical and master data only)",
    "version": "1.0.0",
    "company_name": "Service Reloj",
    "counts": {
        "employees": 54,
        "departments": 3,
        "shifts": 12,
        "timetables": 8,
        "groups": 4
    },
    "recent_reports": [
        {
            "date": "2026-02-04",
            "total_records": 54,
            "present": 52,
            "absent": 2,
            "avg_worked_minutes": 482
        }
    ],
    "meta": {
        "limit": 5
    }
}
```

### Casos de Uso
- ✅ Home del dashboard (datos maestros + historico)
- ✅ Ultimos reportes procesados
- ✅ Conteos de configuracion (empleados, departamentos, turnos, horarios)

---

## Errores Comunes

### Error: `GET /employees/` retorna HTML
**Causa**: Falta el prefijo `/api/v1/`
```bash
❌ curl http://localhost:9000/employees/
✅ curl http://localhost:9000/api/v1/employees/
```

### Error: `GET /attendance/day/` retorna 404
**Causa**: Endpoint no existe
```bash
❌ GET /attendance/day/          (no existe)
✅ GET /api/v1/attendance/day/   (correcto)
```

### Error: Dashboard muestra "Absent" para todos
**Causa**: No hay registros de fichadas para hoy
- El endpoint `/api/v1/attendance/day/` busca logs del día especificado
- Si no hay registros = `status: "Absent"`
- Esto es correcto - El empleado no fichó

---

## Rate Limiting
- Paginación: 50 registros por defecto
- Máximo por página: 1000
- Sin rate limiting específico (desarrollo)

## Autenticación
- Endpoints disponibles sin autenticación especial
- Sistema usa sesiones Django estándar

---

## Changelog
- **2026-02-06**: Removido Dashboard Operativo que dependía de datos del día actual
- **2026-02-06**: Creado endpoint `/api/v1/enums/` como source of truth
- **2026-02-06**: Agregados campos `status_label` y `verify_mode_label` a attendance-logs
- **2026-02-06**: Agregado endpoint `/api/v1/dashboard/summary/` para Home historico
