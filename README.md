# SRTimeWeb - Django 6.0.1 + PostgreSQL

Sistema de control de asistencia y gestión de personal con integración a dispositivos biométricos ZKTeco.

**Migración completa desde FastAPI + MariaDB** manteniendo compatibilidad total con el frontend React existente.

## 🚀 Características

### Backend
- **Django 6.0.1** con Django REST Framework 3.16.1
- **PostgreSQL 18** como base de datos
- **JWT Authentication** con djangorestframework-simplejwt
- **24 Modelos** completos con relaciones y constraints
- **Schema ZKTimeWeb** actualizado (mobile_phone, country, birthday, zone_rel, scope, etc.)
- **Frontend React** integrado y servido por Django

### Funcionalidades Core
- ✅ **Gestión de Personal**: Empleados, Departamentos, Posiciones, Zonas
- ✅ **Horarios Flexibles y Fijos**: Timetables con soporte is_flexible
- ✅ **Turnos y Asignaciones**: Shifts con ciclos de 7 días, scope EMPLOYEE/DEPARTMENT
- ✅ **Dispositivos Biométricos**: Integración ZKTeco con pyzk
- ✅ **Cálculo de Asistencia**: Motor completo con lógica flexible/fija
- ✅ **Reportes**: DailyAttendance con métricas completas
- ✅ **Jobs Asíncronos**: Sistema de trabajos en background

### Services Layer (Business Logic)
```
core/services/
├── attendance_engine.py  # Motor de cálculo (387 líneas)
├── day_context.py        # Contexto de día laboral
├── obligation.py         # Resolución de obligaciones
├── zk.py                 # Wrapper pyzk (268 líneas)
├── jobs.py               # Gestión de trabajos
└── zk_workers.py         # Workers para dispositivos
```

## 📋 Requisitos

- Python 3.14+
- PostgreSQL 18+
- Node.js 18+ (para frontend)
- pyzk 0.9+ (dispositivos ZKTeco)

## 🛠️ Instalación

### 1. Clonar repositorio
```bash
git clone https://github.com/rauloar/srtime-django.git
cd srtime-django
```

### 2. Crear entorno virtual
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate      # Linux/Mac
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar PostgreSQL
```sql
CREATE DATABASE srtimeweb;
CREATE USER srtimeweb_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE srtimeweb TO srtimeweb_user;
```

### 5. Configurar settings (SRTimeWeb/settings.py)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'srtimeweb',
        'USER': 'srtimeweb_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 6. Migrar base de datos
```bash
python manage.py migrate
```

### 7. Crear usuario admin
```bash
python manage.py shell
>>> from core.models import AuthUser
>>> from django.contrib.auth.hashers import make_password
>>> AuthUser.objects.create(username='admin', password_hash=make_password('admin123'), role='admin', active=True)
>>> exit()
```

### 8. Poblar datos de prueba (opcional)
```bash
python tests/seed_django.py
```

### 9. Ejecutar servidor
```bash
python manage.py runserver 0.0.0.0:9000
```

## 📡 API Endpoints

Base URL: `http://localhost:9000/api/v1/`

### Autenticación
- `POST /auth/login` - Login JWT

### Catálogos
- `/companies/` - Empresas
- `/zones/` - Zonas
- `/departments/` - Departamentos  
- `/positions/` - Posiciones
- `/employees/` - Empleados

### Dispositivos
- `/devices/` - Dispositivos biométricos
- `GET /devices/connection-status/all/` - Estado de todos
- `POST /devices/{id}/test-connection/` - Test async
- `GET /devices/{id}/test-connection-sync/` - Test sync
- `POST /devices/{id}/import-attendance/` - Importar registros
- `POST /devices/{id}/sync-users/` - Sincronizar usuarios
- `GET /devices/{id}/jobs/` - Jobs del dispositivo

### Horarios
- `/timetables/` - Horarios (flexible/fijo)
- `/shifts/` - Turnos
- `/schedules/employee-shifts/` - Asignaciones

### Asistencia
- `/attendance-logs/` - Registros de entrada/salida
- `POST /attendance/calculate/` - Calcular periodo
- `GET /attendance/reports/daily/` - Reportes diarios
- `/daily-attendance/` - Asistencia calculada

### Jobs
- `GET /jobs/{id}/` - Estado del job
- `GET /jobs/{id}/logs/` - Logs del job

## 🗄️ Estructura del Proyecto

```
srtime-django/
├── SRTimeWeb/              # Proyecto Django
│   ├── settings.py         # Configuración
│   └── urls.py            # Rutas principales
├── core/                   # App principal
│   ├── models.py          # 24 modelos de dominio
│   ├── serializers.py     # DRF Serializers
│   ├── viewsets.py        # ViewSets CRUD
│   ├── auth_views.py      # Login JWT
│   ├── views_attendance.py # Cálculo asistencia
│   ├── views_devices.py   # Operaciones dispositivos
│   ├── views_jobs.py      # Jobs asíncronos
│   └── services/          # Business Logic Layer
│       ├── attendance_engine.py
│       ├── zk.py
│       ├── jobs.py
│       └── zk_workers.py
├── frontend/              # React 18 + Vite
│   ├── src/
│   └── dist/             # Build producción
├── static/               # Assets servidos por Django
├── tests/                # Scripts de testing
└── requirements.txt      # Dependencias Python
```

## 🧪 Testing

### Verificar instalación
```bash
python manage.py check
```

### Poblar datos de prueba
```bash
python tests/seed_django.py
# Crea: 5 empleados, 4 timetables, 4 shifts, 70 attendance logs
```

### Probar endpoints
```powershell
# Login
$body = @{username="admin";password="admin123"} | ConvertTo-Json
$response = Invoke-RestMethod -Uri "http://localhost:9000/api/v1/auth/login" -Method POST -Body $body -ContentType "application/json"
$token = $response.access_token

# Listar empleados
$headers = @{Authorization="Bearer $token"}
Invoke-RestMethod -Uri "http://localhost:9000/api/v1/employees/" -Headers $headers

# Calcular asistencia
$calcBody = @{start_date="2026-01-08";end_date="2026-01-14"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:9000/api/v1/attendance/calculate/" -Method POST -Headers $headers -Body $calcBody -ContentType "application/json"
```

## 🔧 Configuración Avanzada

### Frontend React
```bash
cd frontend
npm install
npm run dev  # Desarrollo en puerto 5173
npm run build  # Build para producción
```

### Variables de Entorno Frontend
```bash
# frontend/.env.development
VITE_API_BASE_URL=http://127.0.0.1:9000/api/v1
VITE_ENV=development
```

### Dispositivos ZKTeco
El sistema usa la librería `pyzk` para comunicarse con dispositivos biométricos:
- Test de conexión
- Importación de registros
- Sincronización de usuarios
- Descarga de plantillas de huellas

## 📊 Modelos de Datos

### Principales
- **Employee**: first_name, last_name, user_id, mobile_phone, country, birthday
- **Device**: name, ip, port, zone_rel (FK)
- **Timetable**: name, on_duty_time, off_duty_time, is_flexible, required_minutes
- **Shift**: name + 7 ShiftTimetable (ciclo semanal)
- **EmployeeShift**: employee/department, shift, scope (EMPLOYEE/DEPARTMENT)
- **AttendanceLog**: device, user_id, timestamp, punch (0=in, 1=out)
- **DailyAttendance**: employee, date, status, worked_minutes, schedule_type

### Audit Fields (DailyAttendance)
- `schedule_type`: OVERRIDE/DEPT/FIXED/FLEX
- `source_logs_count`: Cantidad de logs procesados
- `is_absent`: Boolean para ausencias

## 🎯 Lógica de Negocio

### Cálculo de Asistencia (attendance_engine.py)

#### Horario Fijo
1. Buscar primer check-in y último check-out
2. Aplicar rounding si configurado
3. Calcular tardanza vs on_duty_time
4. Calcular salida temprana vs off_duty_time
5. Calcular horas trabajadas - break_minutes
6. Calcular overtime si check_out > off_duty_time

#### Horario Flexible
1. Buscar TODOS los check-in/check-out en el rango
2. Sumar todos los períodos trabajados
3. Restar break_minutes del total
4. Comparar vs required_minutes
5. NO calcular tardanza ni salida temprana
6. Calcular overtime si worked > required

### Resolución de Horarios (resolve_schedule)
Prioridad:
1. **ScheduleOverride** (fecha específica)
2. **EmployeeShift** scope=EMPLOYEE (asignación individual)
3. **EmployeeShift** scope=DEPARTMENT (asignación departamental)
4. **Sin horario** = Implicit Rest (ausencia)

## 🚢 Deployment

### Producción con Gunicorn
```bash
pip install gunicorn
gunicorn SRTimeWeb.wsgi:application --bind 0.0.0.0:9000 --workers 4
```

### Con Nginx (reverse proxy)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /api/ {
        proxy_pass http://127.0.0.1:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /path/to/srtime-django/static/;
    }
}
```

## 📝 Credenciales Default

**Admin:**
- Username: `admin`
- Password: `admin123`

**⚠️ IMPORTANTE:** Cambiar contraseña en producción

## 🔗 Links

- **Repositorio:** https://github.com/rauloar/srtime-django
- **Frontend React:** Incluido en /frontend
- **ZKTimeWeb Original:** Proyecto de referencia (FastAPI + MariaDB)

## 📄 Licencia

MIT License

## 👥 Contribuir

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 🐛 Reportar Issues

https://github.com/rauloar/srtime-django/issues

---

**Desarrollado con ❤️ para la gestión moderna de asistencia**
