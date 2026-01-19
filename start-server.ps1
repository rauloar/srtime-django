# ========================================
# Script para iniciar servidor Django
# ========================================

# Colores
$cyan = [System.ConsoleColor]::Cyan
$green = [System.ConsoleColor]::Green
$yellow = [System.ConsoleColor]::Yellow

# Cambiar al directorio del proyecto
$projectPath = $PSScriptRoot
Set-Location $projectPath

Write-Host "`n========================================" -ForegroundColor $cyan
Write-Host "  SRTime Django Server" -ForegroundColor $green
Write-Host "========================================`n" -ForegroundColor $cyan

# Activar entorno virtual
Write-Host "[1/3] Activando entorno virtual..." -ForegroundColor $yellow
& "$projectPath\.venv\Scripts\Activate.ps1"

if ($LASTEXITCODE -eq 0 -or $?) {
    Write-Host "  ✓ Entorno virtual activado`n" -ForegroundColor $green
} else {
    Write-Host "  ✗ Error al activar entorno virtual" -ForegroundColor Red
    exit 1
}

# Verificar estado de Django
Write-Host "[2/3] Verificando configuración de Django..." -ForegroundColor $yellow
python manage.py check --deploy 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Configuración correcta`n" -ForegroundColor $green
} else {
    Write-Host "  ⚠ Advertencias en configuración (continuando...)`n" -ForegroundColor $yellow
}

# Iniciar servidor Django
Write-Host "[3/3] Iniciando servidor Django en puerto 9000..." -ForegroundColor $yellow
Write-Host "`n----------------------------------------" -ForegroundColor $cyan
Write-Host "  Servidor disponible en:" -ForegroundColor $green
Write-Host "  → http://localhost:9000" -ForegroundColor $cyan
Write-Host "  → http://127.0.0.1:9000" -ForegroundColor $cyan
Write-Host "`n  Presiona Ctrl+C para detener" -ForegroundColor $yellow
Write-Host "----------------------------------------`n" -ForegroundColor $cyan

python manage.py runserver 9000
