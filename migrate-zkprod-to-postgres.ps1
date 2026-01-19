# ================================================================
# Migrar datos de MariaDB (zk_prod) a PostgreSQL (srtimeweb_mock)
# Requiere: MariaDB (Wampserver) corriendo en 127.0.0.1:3307 (root sin pass)
#           PostgreSQL 18 en C:\PostgreSQL\18 (psql/createdb)
# Edita variables de conexión si difieren.
# ================================================================

$cyan   = [ConsoleColor]::Cyan
$green  = [ConsoleColor]::Green
$yellow = [ConsoleColor]::Yellow
$red    = [ConsoleColor]::Red

Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor $cyan
Write-Host "  📦 Migración zk_prod → PostgreSQL (srtimeweb_mock)" -ForegroundColor $green
Write-Host "════════════════════════════════════════════════════════════`n" -ForegroundColor $cyan

# ------------ Configuración MariaDB (origen) ------------
$MyHost = '127.0.0.1'
$MyPort = '3307'
$MyUser = 'root'
$MyPass = ''
$MyDb   = 'zk_prod'
$MyBin  = 'C:\wamp64\bin\mariadb\mariadb11.5.2\bin'
$MyCli  = Join-Path $MyBin 'mysql.exe'

# ------------ Configuración PostgreSQL (destino) ------------
$PgHost = '127.0.0.1'
$PgPort = '5432'
$PgUser = 'postgres'   # <-- cambia si usas otro usuario
$PgPass = 'sqlr15ldi12' # <-- provisto
$PgDb   = 'srtimeweb_mock'
$PgBin  = 'C:\PostgreSQL\18\bin'
$Psql   = Join-Path $PgBin 'psql.exe'
$Createdb = Join-Path $PgBin 'createdb.exe'

# ------------ Rutas de trabajo ------------
$BasePath = Split-Path -Parent $MyInvocation.MyCommand.Path
$CsvDir = Join-Path $BasePath 'migration_data\csv'
if (!(Test-Path $CsvDir)) { New-Item -ItemType Directory -Path $CsvDir | Out-Null }

# Tablas a migrar (orden respetando FKs básicos)
$tables = @(
    'companies',
    'zones',
    'departments',
    'positions',
    'employees',
    'devices',
    'users',
    'attendance_logs',
    'biometric_templates',
    'import_batches',
    'jobs',
    'job_logs',
    'att_timetables',
    'att_shifts',
    'att_shift_timetables',
    'att_schedule_overrides',
    'att_employee_shifts',
    'att_leaves',
    'att_holidays',
    'att_daily_attendance',
    'settings'
)

function Fail($msg) {
    Write-Host "✗ $msg" -ForegroundColor $red
    exit 1
}

# ------------ Validaciones previas ------------
if (!(Test-Path $MyCli)) { Fail "mysql.exe no encontrado en $MyCli" }
if (!(Test-Path $Psql)) { Fail "psql.exe no encontrado en $Psql" }
if (!(Test-Path $Createdb)) { Fail "createdb.exe no encontrado en $Createdb" }

Write-Host "[1/5] Verificando conexión MariaDB..." -ForegroundColor $yellow
& $MyCli -u $MyUser -P $MyPort -h $MyHost -e "USE $MyDb;" 2>$null
if ($LASTEXITCODE -ne 0) { Fail "No se pudo conectar a MariaDB ($MyDb)" }
Write-Host "  ✓ Conexión MariaDB OK" -ForegroundColor $green

Write-Host "[2/5] Preparando base PostgreSQL ($PgDb)..." -ForegroundColor $yellow
# Export password env for psql/createdb
$env:PGPASSWORD = $PgPass
# Drop/Create DB
& $Psql -U $PgUser -h $PgHost -p $PgPort -c "DROP DATABASE IF EXISTS \"$PgDb\";" 2>$null
if ($LASTEXITCODE -ne 0) { Fail "No se pudo dropear BD destino" }
& $Createdb -U $PgUser -h $PgHost -p $PgPort $PgDb 2>$null
if ($LASTEXITCODE -ne 0) { Fail "No se pudo crear BD destino" }
Write-Host "  ✓ BD creada: $PgDb" -ForegroundColor $green

Write-Host "[3/5] Ejecutando migrations de Django en BD destino..." -ForegroundColor $yellow
# Variables de entorno temporales para apuntar a la nueva BD
$env:POSTGRES_DB = $PgDb
$env:POSTGRES_USER = $PgUser
$env:POSTGRES_PASSWORD = $PgPass
$env:POSTGRES_HOST = $PgHost
$env:POSTGRES_PORT = $PgPort

# Activar venv y migrar
$venv = Join-Path $BasePath '.venv\Scripts\Activate.ps1'
if (!(Test-Path $venv)) { Fail ".venv no encontrado en $BasePath" }
& $venv
python manage.py migrate 2>$null
if ($LASTEXITCODE -ne 0) { Fail "Fallo migrate" }
Write-Host "  ✓ Schema Django creado" -ForegroundColor $green

Write-Host "[4/5] Exportando tablas a CSV desde MariaDB..." -ForegroundColor $yellow
foreach ($t in $tables) {
    $csv = Join-Path $CsvDir "$t.csv"
    & $MyCli -u $MyUser -P $MyPort -h $MyHost -B -e "USE $MyDb; SELECT * FROM $t;" > $csv
    if (!(Test-Path $csv)) { Fail "No se pudo exportar $t" }
    $size = [math]::Round((Get-Item $csv).Length/1KB,2)
    Write-Host "  ✓ $t -> $size KB" -ForegroundColor $green
}

Write-Host "[5/5] Importando CSV en PostgreSQL..." -ForegroundColor $yellow
$copyOpts = "WITH (FORMAT csv, DELIMITER E'\t', HEADER, NULL '\\N')"
foreach ($t in $tables) {
    $csv = Join-Path $CsvDir "$t.csv"
    Write-Host "  → $t" -ForegroundColor $cyan
    & $Psql -U $PgUser -h $PgHost -p $PgPort -d $PgDb -c "SET session_replication_role = replica; \copy $t FROM '$csv' $copyOpts; SET session_replication_role = DEFAULT;" 2>$null
    if ($LASTEXITCODE -ne 0) { Fail "Falló import de $t" }
}

Write-Host "[Ajustando sequences]" -ForegroundColor $yellow
$setvalSql = @"
DO $$
DECLARE r record;
BEGIN
  FOR r IN
    SELECT c.oid, n.nspname AS schema, c.relname AS tab, pg_get_serial_sequence(format('%I.%I', n.nspname, c.relname), 'id') AS seq
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'public'
  LOOP
    IF r.seq IS NOT NULL THEN
      EXECUTE format('SELECT setval(%L, COALESCE((SELECT max(id) FROM %I),0)+1, false);', r.seq, r.tab);
    END IF;
  END LOOP;
END$$;
"@
& $Psql -U $PgUser -h $PgHost -p $PgPort -d $PgDb -c $setvalSql 2>$null
if ($LASTEXITCODE -ne 0) { Fail "No se pudieron ajustar sequences" }
Write-Host "  ✓ Sequences ajustadas" -ForegroundColor $green

Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor $cyan
Write-Host "  ✅ Migración completada hacia $PgDb" -ForegroundColor $green
Write-Host "════════════════════════════════════════════════════════════`n" -ForegroundColor $cyan

# Limpieza de env vars temporales
Remove-Item Env:POSTGRES_DB, Env:POSTGRES_USER, Env:POSTGRES_PASSWORD, Env:POSTGRES_HOST, Env:POSTGRES_PORT
