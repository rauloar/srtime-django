# start-server.ps1
# Script para iniciar el servidor Django en localhost:9000 por defecto

$env:DJANGO_SETTINGS_MODULE = "SRTimeWeb.settings"
$pythonPath = ".venv/Scripts/python.exe"

if (-Not (Test-Path $pythonPath)) {
    Write-Host "[ERROR] No se encontró el entorno virtual. Ejecuta primero python -m venv .venv" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Activando entorno virtual..." -ForegroundColor Cyan
. .venv/Scripts/Activate.ps1

Write-Host "[INFO] Iniciando servidor Django en http://localhost:9000 ..." -ForegroundColor Green
python manage.py runserver localhost:9000
