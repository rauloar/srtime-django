# Sistema de Logs

Este directorio contiene los logs de la aplicación organizados por categoría.

## Archivos de Log

### 📋 django.log
Logs generales de la aplicación (nivel INFO y superior).
- Eventos del sistema
- Operaciones normales
- Mensajes informativos

### ❌ errors.log
Logs de errores y excepciones (nivel ERROR y superior).
- Errores no manejados
- Excepciones con traceback completo
- Fallos críticos del sistema

### 📊 attendance.log
Logs específicos del motor de asistencia (nivel DEBUG en desarrollo, INFO en producción).
- Cálculos de asistencia
- Modo shadow (validación V1 vs V2)
- Resolución de turnos y horarios
- Comparaciones y discrepancias

### 🌐 api.log
Logs de requests/responses de la API (nivel INFO).
- Todas las peticiones HTTP
- Códigos de respuesta
- Tiempo de ejecución
- IP del cliente
- Usuario autenticado

## Rotación de Archivos

Cada archivo de log:
- **Tamaño máximo:** 10 MB por archivo
- **Backups:** Se mantienen 5 versiones rotadas
- **Formato:** `.log`, `.log.1`, `.log.2`, etc.

Cuando un archivo alcanza 10 MB:
1. Se renombra a `.log.1` (el `.log.1` anterior se convierte en `.log.2`, etc.)
2. Se crea un nuevo archivo `.log` vacío
3. Los backups antiguos (más de 5) se eliminan automáticamente

## Formato de Log

```
LEVEL TIMESTAMP [logger_name] module.function:line - message
```

Ejemplo:
```
INFO 2026-02-10 10:30:45 [api] views.get_employees:125 - → GET /api/v1/employees/ | IP: 127.0.0.1 | User: admin
ERROR 2026-02-10 10:31:12 [core] serializers.validate:87 - Validation error in employee data: {'department': 'This field is required'}
```

## Uso en Código

```python
import logging

# Obtener logger específico
logger = logging.getLogger('core')  # o 'attendance', 'api', 'devices'

# Niveles de log
logger.debug('Mensaje de depuración detallado')
logger.info('Información general')
logger.warning('Advertencia - situación anómala pero manejable')
logger.error('Error - fallo que requiere atención', exc_info=True)  # Include traceback
logger.critical('Crítico - fallo grave del sistema')
```

## Loggers Disponibles

- **`django`** - Core de Django
- **`django.request`** - Requests HTTP (errores 4xx, 5xx)
- **`django.server`** - Servidor de desarrollo
- **`core`** - Aplicación principal (modelos, vistas, serializers)
- **`devices`** - Gestión de dispositivos biométricos
- **`attendance`** - Motor de asistencia y cálculos
- **`attendance.shadow`** - Modo shadow (V1 vs V2 validation)
- **`attendance.resolver`** - Resolución de turnos y horarios
- **`api`** - Requests/responses de la API REST

## Monitoreo

### Ver logs en tiempo real:

**Windows (PowerShell):**
```powershell
Get-Content -Path logs\errors.log -Wait -Tail 50
Get-Content -Path logs\api.log -Wait -Tail 20
```

**Linux/Mac:**
```bash
tail -f logs/errors.log
tail -f logs/api.log
```

### Buscar errores específicos:

**Windows (PowerShell):**
```powershell
Select-String -Path logs\errors.log -Pattern "Exception"
Select-String -Path logs\api.log -Pattern "500"
```

**Linux/Mac:**
```bash
grep "Exception" logs/errors.log
grep "500" logs/api.log
```

## Middleware de Logging

El sistema incluye 2 middlewares personalizados:

1. **RequestLoggingMiddleware**
   - Registra todas las peticiones HTTP
   - Incluye método, path, IP, usuario
   - Mide tiempo de respuesta
   - Captura request/response bodies para debugging

2. **ErrorCaptureMiddleware**
   - Captura excepciones no manejadas
   - Registra contexto completo (user, IP, params, body)
   - Incluye traceback completo
   - Actúa como red de seguridad

## Análisis de Logs

### Encontrar los endpoints más lentos:
```powershell
Select-String -Path logs\api.log -Pattern "Duration:" | 
    Sort-Object { [regex]::Match($_, 'Duration: ([\d.]+)ms').Groups[1].Value -as [double] } -Descending |
    Select-Object -First 10
```

### Contar errores por tipo:
```powershell
Select-String -Path logs\errors.log -Pattern "ERROR" | 
    Group-Object { ($_ -split '\[')[1].Split(']')[0] } | 
    Sort-Object Count -Descending
```

### Ver últimos errores únicos:
```powershell
Select-String -Path logs\errors.log -Pattern "ERROR.*Exception:" | 
    Select-Object -Last 20 -Unique
```

## Limpieza Manual

Para limpiar todos los logs:
```powershell
Remove-Item logs\*.log*
```

Para limpiar solo los backups (mantener archivos actuales):
```powershell
Remove-Item logs\*.log.[1-9]*
```

## Producción

En producción, considerar:
- Aumentar `backupCount` para mantener más histórico
- Usar un servicio centralizado de logs (ELK, Splunk, CloudWatch)
- Configurar alertas automáticas para errores críticos
- Reducir nivel de `api.log` a WARNING para reducir volumen
