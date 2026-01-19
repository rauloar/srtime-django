# SRTimeWeb - Django 6.0.1 Backend
# Migración desde FastAPI + MariaDB

## Instalación

```bash
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate      # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar .env con credenciales reales

# Crear base de datos PostgreSQL
createdb srtimeweb

# Ejecutar migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Correr servidor
python manage.py runserver 9000
```

## Estructura

```
srtime-django/
├── SRTimeWeb/          # Proyecto principal
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/               # App principal (modelos de dominio)
├── devices/            # App para integración ZKTeco
├── scripts/            # Scripts de migración
└── manage.py
```

## Endpoints API

Base URL: `http://localhost:9000/api/v1/`

- `/api/v1/auth/login/` - Login JWT
- `/api/v1/auth/refresh/` - Refresh token
- `/api/v1/employees/` - CRUD empleados
- `/api/v1/devices/` - CRUD dispositivos
- `/api/v1/attendance-logs/` - Logs de asistencia
- Y más...

## Admin

`http://localhost:9000/admin/`

Usuario: (creado con createsuperuser)
