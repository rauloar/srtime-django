# 🎯 DEPLOY_ROLE.md - Contexto Persistente para SSH

**Archivo:** `DEPLOY_ROLE.md`  
**Propósito:** Mantener contexto de tareas y decisiones cuando se conecta a Debian 13 por SSH  
**Ubicación en Servidor:** `/home/debianuser/srtime-django/DEPLOY_ROLE.md`  
**Actualización:** Manual después de cambios importantes

---

## 📋 IDENTIFICACIÓN DEL PROYECTO

```
Nombre: SRTime (Sistema de Registro de Tiempo - ZK Attendance)
Repo: github.com/rauloar/srtime-django
Rama: master
Ambiente: Debian 13 "Trix" Production
Responsable: Equipo de Desarrollo
```

---

## 🏗️ ARQUITECTURA

```
Cliente (Browser)
    ↓
Internet
    ↓
Nginx (Reverse Proxy) - puerto 443 (HTTPS)
    ├─→ /api/* → Django Gunicorn (puerto 8000)
    ├─→ /admin/* → Django Gunicorn (puerto 8000)
    ├─→ /static/* → Files estáticos de Django
    ├─→ /media/* → Files generados por usuarios
    └─→ /* → React compilado (dist/)
    
Backend:
- Python 3.13 + Django 6.0.1
- PostgreSQL 18 (Base de Datos)
- Redis (Cache/Celery)
- Gunicorn (WSGI Server)

Frontend:
- React 18.2 + TypeScript
- Vite (Build Tool)
- Axios (HTTP Client)
- Archivos compilados en /dist

Data:
- PostgreSQL: srtime_db
- User: srtime_user
- Backups: /home/debianuser/backups/
```

---

## 🔑 INFORMACIÓN CRÍTICA

### Credenciales & Configuración
```
PostgreSQL:
- Database: srtime_db
- User: srtime_user
- Host: localhost
- Port: 5432
- Password: [SEE .env IN PROJECT ROOT]

Django Admin:
- URL: https://yourdomain.com/admin/
- Username: [CREATED AT DEPLOY TIME]
- Password: [SEE SECURE NOTES]

Redis:
- Host: localhost
- Port: 6379
- URL: redis://localhost:6379/0
```

### Paths Importantes
```
Proyecto:        /home/debianuser/srtime-django/
Python venv:     /home/debianuser/srtime-django/venv/
Backend:         /home/debianuser/srtime-django/SRTimeWeb/
Frontend src:    /home/debianuser/srtime-django/frontend/src/
Frontend dist:   /home/debianuser/srtime-django/frontend/dist/
PostgreSQL:      /var/lib/postgresql/
Nginx config:    /etc/nginx/sites-available/srtime
Logs Django:     /var/log/srtime/django_*.log
Logs Nginx:      /var/log/nginx/srtime_*.log
Backups DB:      /home/debianuser/backups/
```

### Puertos en Uso
```
80   → Nginx (HTTP → redirect HTTPS)
443  → Nginx (HTTPS) ← PÚBLICO
8000 → Django Gunicorn (interno)
5432 → PostgreSQL (localhost only)
6379 → Redis (localhost only)
```

---

## 📊 ESTADO ACTUAL (Última actualización: 2026-01-19)

### ✅ Completado
- [x] Proyecto Django inicializado con PostgreSQL
- [x] Frontend React integrado con Vite
- [x] Modelos Django definidos (Employee, Department, Device, AttendanceLog, etc.)
- [x] APIs REST implementadas (`/api/v1/`)
- [x] Autenticación JWT configurada
- [x] Base de datos migrada desde MariaDB zk_prod → PostgreSQL
- [x] Mock data cargado en desarrollo
- [x] Documentación de deploy en Debian completada
- [x] Scripts de inicio unificados (start_all.ps1 para dev)

### 🔄 En Progreso
- [ ] Deploy en Debian 13 (seguir DEPLOY_DEBIAN13.md)
- [ ] SSL/TLS certificado con Let's Encrypt
- [ ] Servicios systemd configurados y habilitados
- [ ] Monitoreo en producción establecido

### 📝 Pendiente
- [ ] Pruebas de carga/stress
- [ ] Configurar CI/CD (GitHub Actions)
- [ ] Documentar endpoints críticos
- [ ] Implementar alertas de salud

---

## 🚀 COMANDOS FRECUENTES EN PRODUCCIÓN

### Ver Estado
```bash
# Todos los servicios
sudo systemctl status srtime-django nginx redis-server postgresql

# Solo Django
sudo systemctl status srtime-django
sudo journalctl -u srtime-django -n 50 -f

# Logs Nginx
sudo tail -f /var/log/nginx/srtime_error.log
```

### Reiniciar/Recargar
```bash
# Django (después de cambios de código)
sudo systemctl restart srtime-django

# Nginx (después de cambiar config)
sudo systemctl reload nginx
sudo nginx -t  # Verificar sintaxis primero

# Todo
sudo systemctl restart srtime-django nginx redis-server
```

### Mantenimiento
```bash
# Update backend
cd /home/debianuser/srtime-django
source venv/bin/activate
git pull origin master
pip install -r requirements.txt --upgrade
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart srtime-django

# Update frontend
cd /home/debianuser/srtime-django/frontend
git pull origin master
npm install
npm run build
# Nginx sirve automáticamente la nueva versión

# Ver espacio en disco
df -h
du -sh /home/debianuser/

# Ver uso de recursos
free -h
ps aux | grep -E '(gunicorn|node|postgres)'
```

### Debugging
```bash
# Verificar que Python está corriendo bien
python3.13 --version
source /home/debianuser/srtime-django/venv/bin/activate
pip list | grep -E '(django|drf|gunicorn)'

# Ver si PostgreSQL responde
psql -U srtime_user -h localhost -d srtime_db -c "SELECT COUNT(*) FROM core_employee;"

# Verificar Django
cd /home/debianuser/srtime-django
source venv/bin/activate
python manage.py check

# Test API desde servidor
curl -s https://localhost/api/v1/devices/ | head -20
```

---

## 📚 DOCUMENTOS RELACIONADOS

| Documento | Ubicación | Propósito |
|-----------|-----------|----------|
| **DEPLOY_DEBIAN13.md** | Proyecto root | Guía paso-a-paso para deploy inicial |
| **README.md** | Proyecto root | Instrucciones de desarrollo local |
| **.env** | Proyecto root (no en git) | Variables de entorno (MANTENER SEGURO) |
| **requirements.txt** | Proyecto root | Dependencias Python |
| **frontend/package.json** | frontend/ | Dependencias Node.js |
| **SRTimeWeb/settings.py** | SRTimeWeb/ | Configuración Django |

---

## 🔐 SEGURIDAD - CHECKLIST

### En Servidor
- [ ] `.env` tiene permisos 600 (chmod 600 .env)
- [ ] SSH key configurada (sin password)
- [ ] Firewall habilitado (UFW)
- [ ] Fail2Ban instalado para proteger SSH
- [ ] SSL certificado renovado (auto-renew con certbot)
- [ ] SECRET_KEY de Django es fuerte y privado
- [ ] DEBUG = False en producción
- [ ] ALLOWED_HOSTS correcto
- [ ] CSRF_TRUSTED_ORIGINS configurado

### Backup
- [ ] Backups automáticos PostgreSQL ejecutándose
- [ ] Backups guardados en `/home/debianuser/backups/`
- [ ] Copia de seguridad en location externa (opcionales: cloud)
- [ ] .env respaldado en lugar seguro

---

## 🔧 PROCEDIMIENTOS ESTÁNDAR

### Agregar Nueva Dependencia Python
```bash
cd /home/debianuser/srtime-django
source venv/bin/activate
pip install nombre-paquete
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Add: nombre-paquete"
sudo systemctl restart srtime-django
```

### Crear Nueva API Endpoint
1. Definir modelo en `SRTimeWeb/core/models.py`
2. Crear serializer en `SRTimeWeb/core/serializers.py`
3. Crear viewset en `SRTimeWeb/core/viewsets.py`
4. Registrar en `SRTimeWeb/core/urls.py` (router)
5. `python manage.py makemigrations`
6. `python manage.py migrate`
7. Reiniciar: `sudo systemctl restart srtime-django`

### Cambios en Frontend
1. Editar componentes en `frontend/src/`
2. Testear localmente con `npm run dev`
3. Build: `npm run build`
4. Nginx sirve `frontend/dist/` automáticamente
5. (No necesita reiniciar servicio)

### Monitoreo a Largo Plazo
```bash
# Cron diario - checar salud
0 8 * * * /home/debianuser/srtime-django/scripts/health-check.sh

# Cron semanal - generar reporte de recursos
0 6 * * 0 /home/debianuser/srtime-django/scripts/weekly-report.sh
```

---

## 📞 CONTACTOS & ESCALACIÓN

```
⚠️ ERROR CRÍTICO:
  1. Ver logs: sudo journalctl -u srtime-django -n 100
  2. Reintentar: sudo systemctl restart srtime-django
  3. Si persiste → Reboot: sudo reboot (último recurso)

🆘 ESCALACIÓN:
  - Django no responde → Check: /var/log/srtime/django_error.log
  - Nginx 502 → Check: ps aux | grep gunicorn
  - PostgreSQL error → Check: sudo systemctl status postgresql
  - Disco lleno → Check: df -h && du -sh /home/debianuser/
```

---

## 📅 MANTENIMIENTO RECURRENTE

### Diario
- [ ] Revisar alertas/logs (5 min)

### Semanal
- [ ] Verificar backups creados (2 min)
- [ ] Revisar uso de disco (2 min)
- [ ] Check de Updates disponibles (1 min)

### Mensual
- [ ] Actualizar dependencias menores (30 min)
- [ ] Revisar logs de error (10 min)
- [ ] Probar restore de backup (30 min)

### Trimestral
- [ ] Actualizar dependencias mayores (1-2 hrs)
- [ ] Revisar configuración de seguridad (30 min)
- [ ] Benchmarks de performance (1 hr)

---

## 🎓 REFERENCIAS RÁPIDAS

**Debian 13 "Trix":**
- https://wiki.debian.org/DebianTrix
- https://www.debian.org/releases/trix/

**Django 6.0:**
- https://docs.djangoproject.com/en/6.0/

**PostgreSQL 18:**
- https://www.postgresql.org/docs/18/

**Nginx:**
- https://nginx.org/en/docs/

**Systemd:**
- https://www.freedesktop.org/software/systemd/man/

---

## ✅ ÚLTIMO CHEQUEO

**Fecha:** 2026-01-19  
**Checkeado por:** Equipo Copilot  
**Estado:** ✅ Listo para deploy  

**Próxima revisión recomendada:** 2026-03-19 (cada 2 meses)

---

> 💡 **Tip:** Actualiza este archivo cada vez que hagas cambios importantes en producción.  
> Sirve como referencia rápida para nuevos developers que se conecten al servidor.
