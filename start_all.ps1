# ========================================
# Script para iniciar Backend + Frontend
# ========================================

$cyan = [System.ConsoleColor]::Cyan
$green = [System.ConsoleColor]::Green
$yellow = [System.ConsoleColor]::Yellow
$red = [System.ConsoleColor]::Red

Write-Host "`n========================================" -ForegroundColor $cyan
Write-Host "  SRTime - Backend + Frontend" -ForegroundColor $green
Write-Host "========================================`n" -ForegroundColor $cyan

$projectPath = $PSScriptRoot

# Validar que estamos en el directorio correcto
if (-not (Test-Path "$projectPath\manage.py")) {
    Write-Host "✗ Error: manage.py no encontrado en $projectPath" -ForegroundColor $red
    exit 1
}

if (-not (Test-Path "$projectPath\frontend\package.json")) {
    Write-Host "✗ Error: package.json no encontrado en frontend/" -ForegroundColor $red
    exit 1
}

# Iniciar Backend Django en nueva ventana
Write-Host "[1/2] Iniciando Backend (Django)..." -ForegroundColor $yellow
$backendScript = @"
    `$projectPath = "$projectPath"
    Set-Location "`$projectPath"
    
    # Activar venv
    & .\.venv\Scripts\Activate.ps1
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  Django Backend - Puerto 9000" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    python manage.py runserver 9000
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

# Pequeña pausa para que el backend inicie
Start-Sleep -Seconds 2

# Iniciar Frontend React en nueva ventana
Write-Host "[2/2] Iniciando Frontend (React)..." -ForegroundColor $yellow
$frontendScript = @"
    `$projectPath = "$projectPath"
    Set-Location "`$projectPath\frontend"
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  React Frontend - Puerto 5173" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    npm run dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript

# Mensaje final
Write-Host "`n========================================" -ForegroundColor $green
Write-Host "  ✅ Servidores iniciados:" -ForegroundColor $green
Write-Host "========================================" -ForegroundColor $green
Write-Host "  • Backend (Django): http://localhost:9000" -ForegroundColor $cyan
Write-Host "  • API REST: http://localhost:9000/api/v1/" -ForegroundColor $cyan
Write-Host "  • Frontend (React): http://localhost:5173" -ForegroundColor $cyan
Write-Host "`n  📝 Admin: http://localhost:9000/admin/" -ForegroundColor $yellow
Write-Host "  📝 Docs: http://localhost:9000/api/v1/docs" -ForegroundColor $yellow
Write-Host "`n  💡 Presiona Ctrl+C en cada ventana para detener`n" -ForegroundColor $yellow
