from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import (
    CompanyViewSet, PositionViewSet,
    ZoneViewSet, DepartmentViewSet, EmployeeViewSet,
    DeviceViewSet, AttendanceLogViewSet, ImportBatchViewSet,
    UserViewSet, BiometricTemplateViewSet, SettingViewSet,
    JobViewSet, JobLogViewSet, TimetableViewSet,
    ShiftViewSet, ShiftTimetableViewSet, ScheduleOverrideViewSet,
    EmployeeShiftViewSet, LeaveViewSet, HolidayViewSet,
    DailyAttendanceViewSet
)
from .auth_views import (
    auth_login, auth_users_list, auth_user_delete, auth_user_password_update,
    server_info, auth_me
)
from .views import enums_list, dashboard_summary, get_csrf_token
from .views_attendance import calculate_attendance, daily_reports, daily_reports_v2, calculate_single_day, get_simple_day_view, calculate_attendance_detailed, get_all_absences, get_logs_with_validation
from .views_devices import (
    test_connection, test_connection_sync, import_attendance,
    clear_attendance, download_users, sync_users, clear_all_data,
    all_devices_status, restart_device, poweroff_device, sync_time,
    test_voice, get_memory_info, get_recent_attendance, get_device_templates,
    get_device_info, get_device_users
)
from .views_jobs import get_job, get_job_logs, get_device_jobs
from .views_system import (
    database_backup, list_backups, database_restore, 
    database_test, database_import
)
from .views_stubs import stub_timeline, stub_explanation
from .views_schedule import ScheduleCalendarView

router = DefaultRouter()

# Personnel router for /personnel/* endpoints
personnel_router = DefaultRouter()
personnel_router.register(r'employees', UserViewSet, basename='personnel-employees')

# Catálogos organizacionales
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'positions', PositionViewSet, basename='position')
router.register(r'zones', ZoneViewSet, basename='zone')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'employees', EmployeeViewSet, basename='employee')

# Dispositivos y logs
router.register(r'devices', DeviceViewSet, basename='device')
router.register(r'attendance-logs', AttendanceLogViewSet, basename='attendancelog')
router.register(r'import-batches', ImportBatchViewSet, basename='importbatch')
router.register(r'users', UserViewSet, basename='user')
router.register(r'biometric-templates', BiometricTemplateViewSet, basename='biometrictemplate')

# Configuración y trabajos
router.register(r'settings', SettingViewSet, basename='setting')
router.register(r'jobs', JobViewSet, basename='job')
router.register(r'job-logs', JobLogViewSet, basename='joblog')

# Horarios y turnos
router.register(r'timetables', TimetableViewSet, basename='timetable')
router.register(r'shifts', ShiftViewSet, basename='shift')
router.register(r'shift-timetables', ShiftTimetableViewSet, basename='shifttimetable')
router.register(r'schedule-overrides', ScheduleOverrideViewSet, basename='scheduleoverride')
router.register(r'employee-shifts', EmployeeShiftViewSet, basename='employeeshift')

# Ausencias y feriados
router.register(r'leaves', LeaveViewSet, basename='leave')
router.register(r'holidays', HolidayViewSet, basename='holiday')

# Asistencia calculada
router.register(r'daily-attendance', DailyAttendanceViewSet, basename='dailyattendance')

urlpatterns = [
    path('', include(router.urls)),
    path('personnel/', include(personnel_router.urls)),
    
    # Enums - Provides all enum definitions for front-end consumption
    path('enums/', enums_list, name='enums_list'),

    # Dashboard summary (historical only)
    path('dashboard/summary/', dashboard_summary, name='dashboard_summary'),
    
    # CSRF Token endpoint
    path('csrf/', get_csrf_token, name='get_csrf_token'),
    
    # Auth endpoints compatibles con frontend React
    path('auth/login', auth_login, name='auth_login'),
    path('auth/server-info', server_info, name='server_info'),
    path('auth/me', auth_me, name='auth_me'),
    path('auth/users', auth_users_list, name='auth_users_list'),
    path('auth/users/<int:user_id>', auth_user_delete, name='auth_user_delete'),
    path('auth/users/<int:user_id>/password', auth_user_password_update, name='auth_user_password_update'),
    
    # Attendance Calculation Endpoints
    path('attendance/calculate/', calculate_attendance, name='calculate_attendance'),
    path('attendance/calculate/detailed/', calculate_attendance_detailed, name='calculate_attendance_detailed'),
    path('attendance/calculate/<int:employee_id>/', calculate_single_day, name='calculate_single_day'),
    path('attendance/reports/daily/', daily_reports, name='daily_reports'),
    path('attendance/reports/daily/v2/', daily_reports_v2, name='daily_reports_v2'),
    
    # Schedule Calendar (new simple endpoint)
    path('attendance/schedule/', ScheduleCalendarView.as_view(), name='schedule_calendar'),
    
    # Device Operation Endpoints
    path('devices/connection-status/all/', all_devices_status, name='all_devices_status'),
    path('devices/<int:device_id>/test-connection/', test_connection, name='test_connection'),
    path('devices/<int:device_id>/test-connection-sync/', test_connection_sync, name='test_connection_sync'),
    path('devices/<int:device_id>/import-attendance/', import_attendance, name='import_attendance'),
    path('devices/<int:device_id>/clear-attendance/', clear_attendance, name='clear_attendance'),
    path('devices/<int:device_id>/download-users/', download_users, name='download_users'),
    path('devices/<int:device_id>/sync-users/', sync_users, name='sync_users'),
    path('devices/<int:device_id>/clear-all-data/', clear_all_data, name='clear_all_data'),
    path('devices/<int:device_id>/jobs/', get_device_jobs, name='device_jobs'),

    # Alias FastAPI-style endpoints for frontend compatibility
    path('devices/<int:device_id>/attendance/import', import_attendance, name='import_attendance_alias'),
    path('devices/<int:device_id>/attendance/clear', clear_attendance, name='clear_attendance_alias'),
    path('devices/<int:device_id>/users/download', download_users, name='download_users_alias'),
    path('devices/<int:device_id>/users/sync', sync_users, name='sync_users_alias'),
    path('devices/<int:device_id>/clear_all_data', clear_all_data, name='clear_all_data_alias'),
    path('devices/<int:device_id>/test_connection', test_connection, name='test_connection_alias'),
    path('devices/<int:device_id>/test_connection_sync', test_connection_sync, name='test_connection_sync_alias'),
    
    # New Device Operations
    path('devices/<int:device_id>/restart', restart_device, name='restart_device'),
    path('devices/<int:device_id>/poweroff', poweroff_device, name='poweroff_device'),
    path('devices/<int:device_id>/sync-time', sync_time, name='sync_time'),
    path('devices/<int:device_id>/test-voice', test_voice, name='test_voice'),
    path('devices/<int:device_id>/memory', get_memory_info, name='get_memory_info'),
    path('devices/<int:device_id>/attendance/recent', get_recent_attendance, name='get_recent_attendance'),
    path('devices/<int:device_id>/templates', get_device_templates, name='get_device_templates'),
    path('devices/<int:device_id>/users/', get_device_users, name='get_device_users'),
    path('devices/<int:device_id>/info/', get_device_info, name='get_device_info'),
    
    # Job Endpoints
    path('jobs/<int:job_id>/', get_job, name='get_job'),
    path('jobs/<int:job_id>/logs/', get_job_logs, name='get_job_logs'),
    
    # System Database Endpoints
    path('system/database/backup', database_backup, name='database_backup'),
    path('system/database/backups', list_backups, name='list_backups'),
    path('system/database/restore', database_restore, name='database_restore'),
    path('system/database/test', database_test, name='database_test'),
    path('system/database/import', database_import, name='database_import'),
    
    # Alias para endpoints compatibles con FastAPI (frontend espera estos paths)
    path('attendance/', AttendanceLogViewSet.as_view({'get': 'list'}), name='attendance_list_alias'),
    
    # Alias para schedules (frontend espera /schedules/*)
    path('schedules/timetables/', TimetableViewSet.as_view({'get': 'list', 'post': 'create'}), name='schedules_timetables'),
    path('schedules/shifts/', ShiftViewSet.as_view({'get': 'list', 'post': 'create'}), name='schedules_shifts'),
    
    # Attendance - Minimum Set
    path('attendance/logs/', AttendanceLogViewSet.as_view({'get': 'list'}), name='attendance_logs'),
    path('attendance/daily-attendance/', DailyAttendanceViewSet.as_view({'get': 'list', 'post': 'create'}), name='attendance_daily'),
    
    # Minimal Day View (Rollback Feature)
    path('attendance/day/', get_simple_day_view, name='simple_day_view'),
    
    # Attendance Logs with Validation (FASE 4)
    path('attendance/logs-validated/', get_logs_with_validation, name='logs_validated'),
    # Day View Stubs (DEV MODE - Frontend compatibility)
    path('attendance/<int:employee_id>/timeline/<str:date>/', stub_timeline, name='stub_timeline'),
    path('attendance/<int:employee_id>/explanation/<str:date>/', stub_explanation, name='stub_explanation'),
    
    # Endpoints de compatibilidad (Alias)
    path('attendance/absences/', get_all_absences, name='attendance_absences_alias'),
]
