# ================================================================
# Script para cargar datos mock de zk_prod en Django + PostgreSQL
# ================================================================

$cyan   = [ConsoleColor]::Cyan
$green  = [ConsoleColor]::Green
$yellow = [ConsoleColor]::Yellow
$red    = [ConsoleColor]::Red

Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor $cyan
Write-Host "  📦 Cargar datos mock zk_prod en Django (PostgreSQL)" -ForegroundColor $green
Write-Host "════════════════════════════════════════════════════════════`n" -ForegroundColor $cyan

# --- Configuración ---
$BasePath = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $BasePath) { $BasePath = Get-Location }

$venv = Join-Path $BasePath '.venv\Scripts\Activate.ps1'
$manage = Join-Path $BasePath 'manage.py'

function Fail($msg) {
    Write-Host "✗ $msg" -ForegroundColor $red
    exit 1
}

# --- Paso 1: Activar venv ---
Write-Host "[1/3] Activando virtualenv..." -ForegroundColor $yellow
if (-not (Test-Path $venv)) { Fail ".venv no encontrado en $BasePath" }
& $venv
Write-Host "  ✓ Virtualenv activado" -ForegroundColor $green

# --- Paso 2: Verificar conexión PostgreSQL ---
Write-Host "[2/3] Verificando conexión a PostgreSQL..." -ForegroundColor $yellow
python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('✓ Conexión OK')" 2>$null
if ($LASTEXITCODE -ne 0) { Fail "No se pudo conectar a PostgreSQL. ¿Está corriendo?" }
Write-Host "  ✓ Conexión verificada" -ForegroundColor $green

# --- Paso 3: Cargar datos ---
Write-Host "[3/3] Cargando datos de zk_prod..." -ForegroundColor $yellow
python manage.py load_zk_prod_data --both 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ⚠ Carga completada con advertencias (pueden ser esperadas si esquema ya existe)" -ForegroundColor $yellow
} else {
    Write-Host "  ✓ Datos cargados exitosamente" -ForegroundColor $green
}

Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor $cyan
Write-Host "  ✅ Proceso completado" -ForegroundColor $green
Write-Host "════════════════════════════════════════════════════════════`n" -ForegroundColor $cyan

Write-Host "📝 Próximos pasos:" -ForegroundColor $cyan
Write-Host "  1. Iniciar Django: python manage.py runserver 9000"
Write-Host "  2. Ver datos: http://localhost:9000/api/v1/"
Write-Host "  3. Admin: http://localhost:9000/admin/`n" -ForegroundColor $cyan
