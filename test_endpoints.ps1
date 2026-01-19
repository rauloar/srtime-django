# Test endpoints script
$baseUrl = "http://127.0.0.1:9000/api/v1"

Write-Host "🔐 Probando login..." -ForegroundColor Cyan
$loginBody = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
$token = $loginResponse.access_token
Write-Host "✅ Token obtenido: $($token.Substring(0,20))..." -ForegroundColor Green

$headers = @{
    "Authorization" = "Bearer $token"
}

# Test companies
Write-Host "`n📊 Probando /companies/..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/companies/?skip=0&limit=5" -Headers $headers
    Write-Host "✅ Status 200 - Registros: $($response.Count)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test departments
Write-Host "`n🏢 Probando /departments/..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/departments/?skip=0&limit=5" -Headers $headers
    Write-Host "✅ Status 200 - Registros: $($response.Count)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test employees
Write-Host "`n👥 Probando /employees/..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/employees/?skip=0&limit=5" -Headers $headers
    Write-Host "✅ Status 200 - Registros: $($response.Count)" -ForegroundColor Green
    if ($response.Count -gt 0) {
        $emp = $response[0]
        Write-Host "  Campos nuevos de ZKTimeWeb:" -ForegroundColor Yellow
        Write-Host "    - mobile_phone: $(if ($emp.PSObject.Properties['mobile_phone']) {'✅'} else {'❌'})" -ForegroundColor $(if ($emp.PSObject.Properties['mobile_phone']) {'Green'} else {'Red'})
        Write-Host "    - country: $(if ($emp.PSObject.Properties['country']) {'✅'} else {'❌'})" -ForegroundColor $(if ($emp.PSObject.Properties['country']) {'Green'} else {'Red'})
        Write-Host "    - birthday: $(if ($emp.PSObject.Properties['birthday']) {'✅'} else {'❌'})" -ForegroundColor $(if ($emp.PSObject.Properties['birthday']) {'Green'} else {'Red'})
    }
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test devices
Write-Host "`n🖥️  Probando /devices/..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/devices/?skip=0&limit=5" -Headers $headers
    Write-Host "✅ Status 200 - Registros: $($response.Count)" -ForegroundColor Green
    if ($response.Count -gt 0) {
        $dev = $response[0]
        Write-Host "  Campos nuevos de ZKTimeWeb:" -ForegroundColor Yellow
        Write-Host "    - zone_rel: $(if ($dev.PSObject.Properties['zone_rel']) {'✅'} else {'❌'})" -ForegroundColor $(if ($dev.PSObject.Properties['zone_rel']) {'Green'} else {'Red'})
        Write-Host "    - zone_name: $(if ($dev.PSObject.Properties['zone_name']) {'✅'} else {'❌'})" -ForegroundColor $(if ($dev.PSObject.Properties['zone_name']) {'Green'} else {'Red'})
    }
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test timetables
Write-Host "`n⏰ Probando /schedules/timetables/..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/schedules/timetables/?skip=0&limit=5" -Headers $headers
    Write-Host "✅ Status 200 - Registros: $($response.Count)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test shifts
Write-Host "`n🔄 Probando /schedules/shifts/..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/schedules/shifts/?skip=0&limit=5" -Headers $headers
    Write-Host "✅ Status 200 - Registros: $($response.Count)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test employee-shifts
Write-Host "`n📅 Probando /schedules/employee-shifts/..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/schedules/employee-shifts/?skip=0&limit=5" -Headers $headers
    Write-Host "✅ Status 200 - Registros: $($response.Count)" -ForegroundColor Green
    if ($response.Count -gt 0) {
        $shift = $response[0]
        Write-Host "  Campos nuevos de ZKTimeWeb:" -ForegroundColor Yellow
        Write-Host "    - scope: $(if ($shift.PSObject.Properties['scope']) {'✅'} else {'❌'})" -ForegroundColor $(if ($shift.PSObject.Properties['scope']) {'Green'} else {'Red'})
        Write-Host "    - department: $(if ($shift.PSObject.Properties['department']) {'✅'} else {'❌'})" -ForegroundColor $(if ($shift.PSObject.Properties['department']) {'Green'} else {'Red'})
    }
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test attendance logs
Write-Host "`n📝 Probando /attendance/logs/..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/attendance/logs/?skip=0&limit=5" -Headers $headers
    Write-Host "✅ Status 200 - Registros: $($response.Count)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test daily attendance
Write-Host "`n📊 Probando /attendance/daily-attendance/..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/attendance/daily-attendance/?skip=0&limit=5" -Headers $headers
    Write-Host "✅ Status 200 - Registros: $($response.Count)" -ForegroundColor Green
    if ($response.Count -gt 0) {
        $att = $response[0]
        Write-Host "  Campos nuevos de ZKTimeWeb:" -ForegroundColor Yellow
        Write-Host "    - schedule_type: $(if ($att.PSObject.Properties['schedule_type']) {'✅'} else {'❌'})" -ForegroundColor $(if ($att.PSObject.Properties['schedule_type']) {'Green'} else {'Red'})
        Write-Host "    - source_logs_count: $(if ($att.PSObject.Properties['source_logs_count']) {'✅'} else {'❌'})" -ForegroundColor $(if ($att.PSObject.Properties['source_logs_count']) {'Green'} else {'Red'})
        Write-Host "    - is_absent: $(if ($att.PSObject.Properties['is_absent']) {'✅'} else {'❌'})" -ForegroundColor $(if ($att.PSObject.Properties['is_absent']) {'Green'} else {'Red'})
    }
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test auth users list
Write-Host "`n👤 Probando /auth/users/..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/auth/users/" -Headers $headers
    Write-Host "✅ Status 200 - Usuarios: $($response.Count)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n✅ Pruebas completadas!" -ForegroundColor Green
