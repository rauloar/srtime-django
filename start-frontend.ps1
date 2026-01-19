# ========================================
# Script para iniciar frontend React+Vite
# ========================================

$cyan = [System.ConsoleColor]::Cyan
$green = [System.ConsoleColor]::Green
$yellow = [System.ConsoleColor]::Yellow

# Cambiar al directorio del frontend
$frontendPath = Join-Path $PSScriptRoot "frontend"
Set-Location $frontendPath

Write-Host "`n========================================" -ForegroundColor $cyan
Write-Host "  SRTime Frontend (React + Vite)" -ForegroundColor $green
Write-Host "========================================`n" -ForegroundColor $cyan

# Verificar si node_modules existe
if (!(Test-Path "node_modules")) {
    Write-Host "[1/2] Instalando dependencias..." -ForegroundColor $yellow
    npm install
    Write-Host "  ✓ Dependencias instaladas`n" -ForegroundColor $green
} else {
    Write-Host "[1/2] Dependencias ya instaladas ✓`n" -ForegroundColor $green
}

# Iniciar servidor de desarrollo
Write-Host "[2/2] Iniciando servidor de desarrollo Vite..." -ForegroundColor $yellow
Write-Host "`n----------------------------------------" -ForegroundColor $cyan
Write-Host "  Frontend disponible en:" -ForegroundColor $green
Write-Host "  → http://localhost:5173" -ForegroundColor $cyan
Write-Host "`n  Backend debe estar en:" -ForegroundColor $yellow
Write-Host "  → http://localhost:9000" -ForegroundColor $cyan
Write-Host "`n  Presiona Ctrl+C para detener" -ForegroundColor $yellow
Write-Host "----------------------------------------`n" -ForegroundColor $cyan

npm run dev
