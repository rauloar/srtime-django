# ========================================
# Script para EXPORTAR datos de MariaDB (zk_prod) a JSON
# Preparación para migración a PostgreSQL Django
# ========================================

$cyan = [System.ConsoleColor]::Cyan
$green = [System.ConsoleColor]::Green
$yellow = [System.ConsoleColor]::Yellow
$red = [System.ConsoleColor]::Red

Write-Host "`n═══════════════════════════════════════════════════════════════" -ForegroundColor $cyan
Write-Host "  📦 EXPORTACIÓN DE DATOS: MariaDB → JSON" -ForegroundColor $green
Write-Host "═══════════════════════════════════════════════════════════════`n" -ForegroundColor $cyan

# Configuración
$mysqlPath = "C:\wamp64\bin\mariadb\mariadb11.5.2\bin\mysql.exe"
$mysqldumpPath = "C:\wamp64\bin\mariadb\mariadb11.5.2\bin\mysqldump.exe"
$dbName = "zk_prod"
$dbHost = "127.0.0.1"
$dbPort = "3307"
$dbUser = "root"
$exportDir = "C:\Proyectos\srtime-django\migration_data"

# Crear directorio si no existe
if (!(Test-Path $exportDir)) {
    New-Item -ItemType Directory -Path $exportDir | Out-Null
    Write-Host "✅ Directorio creado: $exportDir`n" -ForegroundColor $green
}

# Verificar conexión
Write-Host "[1/3] Verificando conexión a MariaDB..." -ForegroundColor $yellow
try {
    & $mysqlPath -u $dbUser -P $dbPort -h $dbHost -e "USE $dbName;" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Conexión exitosa a $dbName`n" -ForegroundColor $green
    } else {
        throw "No se pudo conectar"
    }
} catch {
    Write-Host "  ✗ Error de conexión" -ForegroundColor $red
    Write-Host "  Asegúrate de que WampServer esté corriendo`n" -ForegroundColor $yellow
    exit 1
}

# Exportar schema completo
Write-Host "[2/3] Exportando schema de base de datos..." -ForegroundColor $yellow
$schemaFile = Join-Path $exportDir "zk_prod_schema.sql"
& $mysqldumpPath -u $dbUser -P $dbPort -h $dbHost --no-data --routines $dbName > $schemaFile 2>&1
if (Test-Path $schemaFile) {
    $schemaSize = [math]::Round((Get-Item $schemaFile).Length / 1KB, 2)
    Write-Host "  ✓ Schema exportado: $schemaSize KB`n" -ForegroundColor $green
} else {
    Write-Host "  ✗ Error al exportar schema`n" -ForegroundColor $red
    exit 1
}

# Exportar datos completos
Write-Host "[3/3] Exportando datos completos..." -ForegroundColor $yellow
$dataFile = Join-Path $exportDir "zk_prod_data.sql"
& $mysqldumpPath -u $dbUser -P $dbPort -h $dbHost --complete-insert --extended-insert=FALSE $dbName > $dataFile 2>&1
if (Test-Path $dataFile) {
    $dataSize = [math]::Round((Get-Item $dataFile).Length / 1KB, 2)
    Write-Host "  ✓ Datos exportados: $dataSize KB`n" -ForegroundColor $green
} else {
    Write-Host "  ✗ Error al exportar datos`n" -ForegroundColor $red
    exit 1
}

# Resumen
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor $cyan
Write-Host "  ✅ EXPORTACIÓN COMPLETADA" -ForegroundColor $green
Write-Host "═══════════════════════════════════════════════════════════════`n" -ForegroundColor $cyan

Write-Host "📁 Archivos generados en: $exportDir`n" -ForegroundColor $yellow
Get-ChildItem $exportDir | Select-Object Name, @{Name='Size (KB)';Expression={[math]::Round($_.Length / 1KB, 2)}} | Format-Table -AutoSize

Write-Host "`n📋 Estadísticas de datos exportados:`n" -ForegroundColor $cyan
$tables = @('employees', 'attendance_logs', 'devices', 'companies', 'departments', 'users', 'att_daily_attendance')
foreach ($table in $tables) {
    $count = & $mysqlPath -u $dbUser -P $dbPort -h $dbHost -s -N -e "SELECT COUNT(*) FROM $dbName.$table;" 2>&1
    Write-Host "  $table : $count registros" -ForegroundColor White
}

Write-Host "`n═══════════════════════════════════════════════════════════════" -ForegroundColor $cyan
Write-Host "  ✅ Listo para migración a PostgreSQL Django" -ForegroundColor $green
Write-Host "═══════════════════════════════════════════════════════════════`n" -ForegroundColor $cyan

Write-Host "Siguiente paso:" -ForegroundColor $yellow
Write-Host "  python manage.py migrate_from_mariadb`n" -ForegroundColor $cyan
