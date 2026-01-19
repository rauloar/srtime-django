# 📦 DEPLOY EN DEBIAN 13 "TRIX"

## Tabla de Contenidos
1. [Requisitos](#requisitos)
2. [Preparación del Servidor](#preparación-del-servidor)
3. [Backend Django](#backend-django)
4. [Frontend React](#frontend-react)
5. [Nginx (Reverse Proxy)](#nginx-reverse-proxy)
6. [Base de Datos PostgreSQL](#base-de-datos-postgresql)
7. [Servicios Systemd](#servicios-systemd)
8. [Monitoreo](#monitoreo)
9. [Troubleshooting](#troubleshooting)

---

## Requisitos

**Stack de Producción:**
- Debian 13 "Trix"
- Python 3.13+
- Node.js 20+ (para compilar frontend)
- PostgreSQL 18
- Redis (para cache/celery)
- Nginx (reverse proxy)
- Gunicorn (WSGI server)

**Acceso:**
- Usuario: `debianuser` (o similar, con privilegios sudo)
- SSH key configurada
- Dominio/IP pública

---

## Preparación del Servidor

### 1. Actualizar Sistema
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
```

### 2. Instalar Dependencias Base
```bash
sudo apt install -y \
  python3.13 \
  python3.13-venv \
  python3-pip \
  postgresql \
  postgresql-contrib \
  redis-server \
  nginx \
  git \
  curl \
  wget \
  vim \
  htop
```

### 3. Instalar Node.js (para build del frontend)
```bash
# Usando NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

### 4. Verificar Versiones
```bash
python3.13 --version
node --version
npm --version
psql --version
redis-server --version
nginx -v
```

---

## Backend Django

### 1. Clonar Repositorio
```bash
cd /home/debianuser
git clone https://github.com/rauloar/srtime-django.git
cd srtime-django
```

### 2. Crear Virtual Environment
```bash
python3.13 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
```

### 3. Instalar Dependencias Python
```bash
pip install -r requirements.txt
pip install gunicorn[gevent]
```

### 4. Configurar Variables de Entorno
```bash
cat > .env << 'EOF'
# Django
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-ip

# Database
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=srtime_db
DATABASE_USER=srtime_user
DATABASE_PASSWORD=your-secure-password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Optional: Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EOF

chmod 600 .env
```

### 5. Preparar Base de Datos
```bash
# Activar venv
source venv/bin/activate

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Cargar datos mock (opcional, si tienes archivos de migración)
# python manage.py load_zk_prod_data --both

# Recolectar archivos estáticos
python manage.py collectstatic --noinput
```

### 6. Compilar Frontend
```bash
cd frontend
npm install
npm run build
cd ..
```

### 7. Verificar que Todo Funciona
```bash
# Test rápido con Gunicorn
gunicorn SRTimeWeb.wsgi:application --bind 127.0.0.1:8000 --workers 4

# Debería mostrar: Listening at: http://127.0.0.1:8000
# Ctrl+C para detener
```

---

## Nginx (Reverse Proxy)

### 1. Crear Configuración de Nginx
```bash
sudo tee /etc/nginx/sites-available/srtime << 'EOF'
upstream django {
    server 127.0.0.1:8000;
}

upstream frontend {
    server 127.0.0.1:3000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirigir HTTP a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # Certificados SSL (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Configuraciones SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Cliente
    client_max_body_size 100M;

    # Logs
    access_log /var/log/nginx/srtime_access.log;
    error_log /var/log/nginx/srtime_error.log;

    # API Django
    location /api/ {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Admin Django
    location /admin/ {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files Django
    location /static/ {
        alias /home/debianuser/srtime-django/static/;
        expires 30d;
    }

    # Media files
    location /media/ {
        alias /home/debianuser/srtime-django/media/;
        expires 7d;
    }

    # Frontend React (SPA)
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Soporte para SPA routing
        error_page 404 =200 /index.html;
    }
}
EOF

# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/srtime /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Verificar configuración
sudo nginx -t

# Reiniciar nginx
sudo systemctl restart nginx
```

### 2. Configurar SSL (Let's Encrypt)
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renovación
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## Base de Datos PostgreSQL

### 1. Crear Base de Datos y Usuario
```bash
sudo su - postgres

# En la consola psql
psql

# Dentro de psql:
CREATE DATABASE srtime_db;
CREATE USER srtime_user WITH PASSWORD 'your-secure-password';
ALTER ROLE srtime_user SET client_encoding TO 'utf8';
ALTER ROLE srtime_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE srtime_user SET default_transaction_deferrable TO on;
ALTER ROLE srtime_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE srtime_db TO srtime_user;
\q

# Salir de postgres
exit
```

### 2. Configurar Respaldo Automático
```bash
# Crear carpeta de backups
mkdir -p /home/debianuser/backups

# Crear script de backup
cat > /home/debianuser/backups/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/debianuser/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="srtime_db"

pg_dump -U srtime_user -h localhost $DB_NAME | gzip > $BACKUP_DIR/srtime_${TIMESTAMP}.sql.gz

# Mantener solo últimos 7 días
find $BACKUP_DIR -name "srtime_*.sql.gz" -mtime +7 -delete
EOF

chmod +x /home/debianuser/backups/backup-db.sh

# Agregar a cron (diario a las 2 AM)
sudo crontab -e
# Agregar línea:
# 0 2 * * * /home/debianuser/backups/backup-db.sh
```

---

## Servicios Systemd

### 1. Servicio Django (Gunicorn)
```bash
sudo tee /etc/systemd/system/srtime-django.service << 'EOF'
[Unit]
Description=SRTime Django Application
After=network.target postgresql.service

[Service]
Type=notify
User=debianuser
WorkingDirectory=/home/debianuser/srtime-django
Environment="PATH=/home/debianuser/srtime-django/venv/bin"
ExecStart=/home/debianuser/srtime-django/venv/bin/gunicorn \
    --workers 4 \
    --worker-class gevent \
    --bind 127.0.0.1:8000 \
    --access-logfile /var/log/srtime/django_access.log \
    --error-logfile /var/log/srtime/django_error.log \
    SRTimeWeb.wsgi:application

Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo mkdir -p /var/log/srtime
sudo chown debianuser:debianuser /var/log/srtime
```

### 2. Servicio Frontend (Node.js)
```bash
sudo tee /etc/systemd/system/srtime-frontend.service << 'EOF'
[Unit]
Description=SRTime React Frontend
After=network.target

[Service]
Type=simple
User=debianuser
WorkingDirectory=/home/debianuser/srtime-django/frontend
Environment="NODE_ENV=production"
Environment="PORT=3000"
ExecStart=/usr/bin/node /home/debianuser/srtime-django/frontend/dist/index.js

Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

> **Nota:** Si usas Vite/React para servir estática (recomendado), omite este servicio y deja que Nginx sirva `/dist`

### 3. Habilitar y Iniciar Servicios
```bash
sudo systemctl daemon-reload

# Django
sudo systemctl enable srtime-django
sudo systemctl start srtime-django
sudo systemctl status srtime-django

# Nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# Redis (ya debería estar)
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 4. Verificar Estado
```bash
sudo systemctl status srtime-django
sudo systemctl status nginx
sudo journalctl -u srtime-django -n 50 -f  # Ver logs en tiempo real
```

---

## Monitoreo

### 1. Ver Logs
```bash
# Django
sudo journalctl -u srtime-django -n 100 -f

# Nginx
sudo tail -f /var/log/nginx/srtime_error.log
sudo tail -f /var/log/nginx/srtime_access.log

# PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### 2. Monitoreo de Recursos
```bash
# Ver consumo de CPU/RAM
htop

# Ver puertos abiertos
sudo netstat -tlnp | grep -E ':(8000|3000|80|443)'
```

### 3. Health Check
```bash
# API alive?
curl -I https://yourdomain.com/api/v1/

# Frontend alive?
curl -I https://yourdomain.com/
```

---

## Updates y Mantenimiento

### Actualizar Backend
```bash
cd /home/debianuser/srtime-django
git pull origin master
source venv/bin/activate
pip install -r requirements.txt --upgrade
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart srtime-django
```

### Actualizar Frontend
```bash
cd /home/debianuser/srtime-django/frontend
git pull origin master
npm install
npm run build
sudo systemctl restart nginx
```

---

## Troubleshooting

### Django no inicia
```bash
# Verificar errores
sudo journalctl -u srtime-django -n 50
python manage.py check
```

### Nginx 502 Bad Gateway
```bash
# Verificar que Django está escuchando
sudo netstat -tlnp | grep 8000

# Reiniciar Django
sudo systemctl restart srtime-django
```

### Permiso denegado en /media o /static
```bash
sudo chown -R debianuser:debianuser /home/debianuser/srtime-django/media
sudo chown -R debianuser:debianuser /home/debianuser/srtime-django/static
```

### PostgreSQL connection refused
```bash
# Verificar que PostgreSQL está corriendo
sudo systemctl status postgresql

# Verificar credenciales en .env
psql -U srtime_user -h localhost -d srtime_db
```

---

## Checklist Final

- [ ] Debian actualizado
- [ ] Python 3.13, Node.js 20 instalados
- [ ] Git clone del repo
- [ ] Venv creado y dependencias instaladas
- [ ] .env configurado (cambiar secretos)
- [ ] PostgreSQL DB + user creados
- [ ] Migraciones ejecutadas
- [ ] Superusuario creado
- [ ] Frontend compilado
- [ ] Nginx configurado
- [ ] SSL certificado
- [ ] Servicios systemd creados y habilitados
- [ ] Backups automáticos configurados
- [ ] URLs accesibles
- [ ] Logs monitoreados

---

## Scripts Útiles

### Script de Deploy Completo
```bash
#!/bin/bash
# deploy.sh - Ejecutar después de git pull

cd /home/debianuser/srtime-django
source venv/bin/activate
pip install -r requirements.txt --upgrade
python manage.py migrate
python manage.py collectstatic --noinput

cd frontend
npm install
npm run build
cd ..

sudo systemctl restart srtime-django
sudo systemctl restart nginx
sudo systemctl restart redis-server

echo "✅ Deploy completado"
```

### Monitoreo Rápido
```bash
#!/bin/bash
# monitor.sh

echo "=== Estado de Servicios ==="
sudo systemctl status srtime-django --no-pager
sudo systemctl status nginx --no-pager

echo -e "\n=== Puertos Abiertos ==="
sudo netstat -tlnp | grep -E ':(8000|3000|80|443|5432)'

echo -e "\n=== Uso de Recursos ==="
free -h
df -h

echo -e "\n=== Últimos Errores Django ==="
sudo journalctl -u srtime-django -n 10 --no-pager
```

---

**Preguntas?** Consulta los logs con `journalctl` o revisa el archivo de rol en `DEPLOY_ROLE.md`
