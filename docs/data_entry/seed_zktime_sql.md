# Seed controlado desde ZKTimeNet SQL

## Objetivo
Cargar datos reales desde un dump .sql de ZKTimeNet como texto (sin ejecutar SQL), poblando solo:
- Employee
- AttendanceLog

## Reglas
- NO se ejecuta SQL
- NO se modifica el esquema
- NO se crean modelos nuevos

## Comando
Archivo: core/management/commands/seed_zk_sql.py

### Uso basico
```bash
python manage.py seed_zk_sql
```

### Opciones
- `--sql-path` Ruta del dump (default: `caso_real_sql/ZKTimeNet.db.sql`)
- `--skip-employees` No crea empleados
- `--skip-logs` No crea logs
- `--limit-employees` Limita empleados importados
- `--limit-logs` Limita logs importados
- `--batch-size` Tamano de batch para logs (default 5000)
- `--device-name` Nombre del dispositivo dummy para logs
- `--dry-run` Parsea sin escribir en DB
- `--clear-existing-logs` Borra logs antes de importar
- `--clear-existing-employees` Borra empleados antes de importar

## Mapeos
### Employee
- `user_id` <- `emp_pin` (fallback: `emp_pin2`, `emp_username`, `id`)
- `name` <- `emp_firstname` + `emp_lastname`
- `hire_date` <- `emp_hiredate`
- `active` <- `emp_active`
- `email` <- `emp_email`
- `phone` <- `emp_phone`
- `address/city/country/ssn` <- columnas homonimas

### AttendanceLog
- `user_id` <- `att_punches.employee_id` -> `hr_employee.emp_pin`
- `timestamp` <- `punch_time`
- `status` <- `status`
- `punch` <- `punch_type`
- `verify_mode` <- `verifycode`
- `workstate` <- `workstate`
- `workcode` <- `workcode`
- `punch_source` <- `terminal_id`
- `raw_json` <- resto de campos relevantes

## Validacion sugerida
1. `Employee.objects.count()` > 0
2. `AttendanceLog.objects.count()` > 0
3. UI lista empleados y fichadas reales
4. Timeline renderiza multiples punches
