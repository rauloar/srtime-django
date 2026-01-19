# 🔔 REMINDER: Pasar de Local a SSH (Debian 13)

Este recordatorio es para cuando te conectas por SSH al servidor Debian y quieres retomar trabajo sin perder contexto.

## Objetivo
- Reanudar tareas rápidamente en producción/servidor
- Ubicaciones, comandos y orden correcto
- Enlaces a docs completas

## Conexión y Ubicaciones
- Conéctate: `ssh debianuser@yourdomain.com`
- Proyecto: `/home/debianuser/srtime-django/`
- Venv: `/home/debianuser/srtime-django/venv/`
- Frontend dist: `/home/debianuser/srtime-django/frontend/dist/`
- Logs Django: `/var/log/srtime/django_*.log`
- Logs Nginx: `/var/log/nginx/srtime_*.log`
- Backups DB: `/home/debianuser/backups/`

## Ruta Rápida para "Volver al Trabajo"
```bash
# 1) Entrar al proyecto
cd /home/debianuser/srtime-django

# 2) Activar venv
source venv/bin/activate

# 3) Actualizar código
git pull origin main

# 4) Instalar dependencias
pip install -r requirements.txt --upgrade

# 5) Migraciones y estáticos
python manage.py migrate
python manage.py collectstatic --noinput

# 6) Frontend (si hubo cambios)
cd frontend
npm install
npm run build
cd ..

# 7) Reiniciar servicios
sudo systemctl restart srtime-django
sudo systemctl restart nginx
```

## PostgreSQL Rápido (si falta)
```bash
sudo apt update && sudo apt install -y postgresql postgresql-contrib
sudo -u postgres psql

CREATE DATABASE srtime_db;
CREATE USER srtime_user WITH PASSWORD 'cambia-este-pass';
GRANT ALL PRIVILEGES ON DATABASE srtime_db TO srtime_user;
\q
```

## Variables de Entorno Clave (.env)
- `DEBUG=False` (en producción)
- `ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-ip`
- `DATABASE_*` apuntando a PostgreSQL
- `SECRET_KEY` fuerte y privado
- `CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com`

## Monitoreo y Debug
```bash
# Django
sudo systemctl status srtime-django
sudo journalctl -u srtime-django -n 100 -f

# Nginx
sudo nginx -t
sudo systemctl status nginx
sudo tail -f /var/log/nginx/srtime_error.log

# PostgreSQL
sudo systemctl status postgresql
psql -U srtime_user -h localhost -d srtime_db -c "SELECT COUNT(*) FROM core_employee;"
```

## Cargar Datos Mock (opcional)
```bash
# Django management command
source venv/bin/activate
python manage.py load_zk_prod_data --both

# Script de tests (alternativa)
python tests/load_zk_prod.py
```

## Diferencias Local vs Servidor
- Local: `python manage.py runserver`, `npm run dev`
- Servidor: **Gunicorn + Nginx**, frontend servido desde `dist/`
- Logs en servidor, DEBUG desactivado

## Enlaces Útiles
- Guía completa: [DEPLOY_DEBIAN13.md](DEPLOY_DEBIAN13.md)
- Rol/contexto persistente: [DEPLOY_ROLE.md](DEPLOY_ROLE.md)
- Inicio local combinado: [start_all.ps1](start_all.ps1)
- Carga mock data: [tests/load_zk_prod.py](tests/load_zk_prod.py)

## Estado de Tareas (resumen)
- Deploy guía completa: ✅
- Rol/Contexto SSH: ✅
- Push `main` remoto: ✅
- Instalar PostgreSQL en Debian: 🟡 pendiente si no está
- Configurar Nginx + SSL: 🟡 según dominio

Mantén este archivo actualizado tras cambios importantes para que el próximo SSH sea plug-and-play.