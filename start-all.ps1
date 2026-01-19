# ========================================
# Script para iniciar Backend + Frontend
# ========================================

$cyan = [System.ConsoleColor]::Cyan
$green = [System.ConsoleColor]::Green
$yellow = [System.ConsoleColor]::Yellow

Write-Host "`n========================================" -ForegroundColor $cyan
Write-Host "  SRTime - Iniciar Aplicación Completa" -ForegroundColor $green
Write-Host "========================================`n" -ForegroundColor $cyan

$projectPath = $PSScriptRoot

# Iniciar Backend Django en nueva ventana
Write-Host "[1/2] Iniciando Backend Django..." -ForegroundColor $yellow
$backendScript = Join-Path $projectPath "start-server.ps1"
Start-Process powershell -ArgumentList "-NoExit", "-File", "`"$backendScript`"" -WindowStyle Normal
Write-Host "  ✓ Backend iniciado en nueva ventana`n" -ForegroundColor $green

# Esperar 3 segundos para que Django inicie
Write-Host "Esperando que Django inicie..." -ForegroundColor $yellow
Start-Sleep -Seconds 3

# Iniciar Frontend React+Vite en nueva ventana
Write-Host "`n[2/2] Iniciando Frontend React+Vite..." -ForegroundColor $yellow
$frontendScript = Join-Path $projectPath "start-frontend.ps1"
Start-Process powershell -ArgumentList "-NoExit", "-File", "`"$frontendScript`"" -WindowStyle Normal
Write-Host "  ✓ Frontend iniciado en nueva ventana`n" -ForegroundColor $green

Write-Host "========================================" -ForegroundColor $cyan
Write-Host "  ✓ Aplicación iniciada correctamente" -ForegroundColor $green
Write-Host "========================================`n" -ForegroundColor $cyan

Write-Host "URLs disponibles:" -ForegroundColor $yellow
Write-Host "  Backend:  http://localhost:9000" -ForegroundColor $cyan
Write-Host "  Frontend: http://localhost:5173`n" -ForegroundColor $cyan

Write-Host "Presiona cualquier tecla para cerrar esta ventana..." -ForegroundColor $yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
