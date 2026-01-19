# ========================================
# Script para detener servidor Django
# ========================================

$cyan = [System.ConsoleColor]::Cyan
$green = [System.ConsoleColor]::Green
$red = [System.ConsoleColor]::Red

Write-Host "`n========================================" -ForegroundColor $cyan
Write-Host "  Deteniendo SRTime Django Server" -ForegroundColor $green
Write-Host "========================================`n" -ForegroundColor $cyan

# Buscar procesos Python corriendo manage.py en puerto 9000
$djangoProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*manage.py*runserver*9000*"
}

if ($djangoProcesses) {
    Write-Host "Procesos encontrados: $($djangoProcesses.Count)" -ForegroundColor $cyan
    foreach ($proc in $djangoProcesses) {
        Write-Host "  → Deteniendo PID: $($proc.Id)" -ForegroundColor $red
        Stop-Process -Id $proc.Id -Force
    }
    Write-Host "`n✓ Servidor Django detenido`n" -ForegroundColor $green
} else {
    Write-Host "✓ No hay servidores Django corriendo en puerto 9000`n" -ForegroundColor $green
}
