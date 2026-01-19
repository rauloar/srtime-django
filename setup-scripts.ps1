# ========================================
# Script de configuración inicial
# Habilita la ejecución de scripts PowerShell
# ========================================

$cyan = [System.ConsoleColor]::Cyan
$green = [System.ConsoleColor]::Green
$yellow = [System.ConsoleColor]::Yellow
$red = [System.ConsoleColor]::Red

Write-Host "`n========================================" -ForegroundColor $cyan
Write-Host "  Configuración de Scripts PowerShell" -ForegroundColor $green
Write-Host "========================================`n" -ForegroundColor $cyan

# Verificar política actual
Write-Host "[1/2] Verificando política de ejecución actual..." -ForegroundColor $yellow
$currentPolicy = Get-ExecutionPolicy -Scope CurrentUser
Write-Host "  Política actual (CurrentUser): $currentPolicy" -ForegroundColor $cyan

if ($currentPolicy -eq "RemoteSigned" -or $currentPolicy -eq "Unrestricted") {
    Write-Host "  ✓ La ejecución de scripts ya está habilitada`n" -ForegroundColor $green
    Write-Host "========================================" -ForegroundColor $cyan
    Write-Host "  ✓ Todo listo para usar los scripts" -ForegroundColor $green
    Write-Host "========================================`n" -ForegroundColor $cyan
    Write-Host "Puedes ejecutar:" -ForegroundColor $yellow
    Write-Host "  .\start-server.ps1" -ForegroundColor $cyan
    Write-Host "  .\start-all.ps1`n" -ForegroundColor $cyan
    exit 0
}

# Habilitar ejecución de scripts
Write-Host "`n[2/2] Habilitando ejecución de scripts..." -ForegroundColor $yellow
Write-Host "  Se aplicará: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned" -ForegroundColor $cyan

try {
    Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force -ErrorAction Stop
    Write-Host "  ✓ Política actualizada exitosamente`n" -ForegroundColor $green
    
    # Verificar cambio
    $newPolicy = Get-ExecutionPolicy -Scope CurrentUser
    Write-Host "Nueva política (CurrentUser): $newPolicy`n" -ForegroundColor $green
    
    Write-Host "========================================" -ForegroundColor $cyan
    Write-Host "  ✓ Configuración completada" -ForegroundColor $green
    Write-Host "========================================`n" -ForegroundColor $cyan
    
    Write-Host "Ahora puedes ejecutar:" -ForegroundColor $yellow
    Write-Host "  .\start-server.ps1  - Solo backend" -ForegroundColor $cyan
    Write-Host "  .\start-all.ps1     - Backend + Frontend`n" -ForegroundColor $cyan
    
} catch {
    Write-Host "`n  ✗ Error al cambiar política" -ForegroundColor $red
    Write-Host "  Motivo: $($_.Exception.Message)`n" -ForegroundColor $red
    
    Write-Host "========================================" -ForegroundColor $cyan
    Write-Host "  Solución Alternativa" -ForegroundColor $yellow
    Write-Host "========================================`n" -ForegroundColor $cyan
    
    Write-Host "Ejecuta esto manualmente como Administrador:" -ForegroundColor $yellow
    Write-Host "  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force`n" -ForegroundColor $cyan
    
    Write-Host "O ejecuta scripts con bypass:" -ForegroundColor $yellow
    Write-Host "  powershell -ExecutionPolicy Bypass -File .\start-server.ps1`n" -ForegroundColor $cyan
    
    exit 1
}
