from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import (
    AuthUserViewSet, CompanyViewSet, PositionViewSet,
    ZoneViewSet, DepartmentViewSet, EmployeeViewSet,
    DeviceViewSet, AttendanceLogViewSet, ImportBatchViewSet,
    UserViewSet, BiometricTemplateViewSet, SettingViewSet,
    JobViewSet, JobLogViewSet, TimetableViewSet,
    ShiftViewSet, ShiftTimetableViewSet, ScheduleOverrideViewSet,
    EmployeeShiftViewSet, LeaveViewSet, HolidayViewSet,
    DailyAttendanceViewSet
)
from .auth_views import (
    auth_login, auth_users_list, auth_user_delete, auth_user_password_update
)
from .views_attendance import calculate_attendance, daily_reports, calculate_single_day
from .views_devices import (
    test_connection, test_connection_sync, import_attendance,
    clear_attendance, download_users, sync_users, clear_all_data,
    all_devices_status
)
from .views_jobs import get_job, get_job_logs, get_device_jobs

router = DefaultRouter()

# Autenticación y usuarios
router.register(r'auth-users', AuthUserViewSet, basename='authuser')

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
    
    # Auth endpoints compatibles con frontend React
    path('auth/login', auth_login, name='auth_login'),
    path('auth/users', auth_users_list, name='auth_users_list'),
    path('auth/users/<int:user_id>', auth_user_delete, name='auth_user_delete'),
    path('auth/users/<int:user_id>/password', auth_user_password_update, name='auth_user_password_update'),
    
    # Attendance Calculation Endpoints
    path('attendance/calculate/', calculate_attendance, name='calculate_attendance'),
    path('attendance/calculate/<int:employee_id>/', calculate_single_day, name='calculate_single_day'),
    path('attendance/reports/daily/', daily_reports, name='daily_reports'),
    
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
    
    # Job Endpoints
    path('jobs/<int:job_id>/', get_job, name='get_job'),
    path('jobs/<int:job_id>/logs/', get_job_logs, name='get_job_logs'),
    
    # Alias para endpoints compatibles con FastAPI (frontend espera estos paths)
    path('attendance/', AttendanceLogViewSet.as_view({'get': 'list'}), name='attendance_list_alias'),
    
    # Alias para schedules (frontend espera /schedules/*)
    path('schedules/timetables/', TimetableViewSet.as_view({'get': 'list', 'post': 'create'}), name='schedules_timetables'),
    path('schedules/timetables/<int:pk>/', TimetableViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='schedules_timetable_detail'),
    path('schedules/shifts/', ShiftViewSet.as_view({'get': 'list', 'post': 'create'}), name='schedules_shifts'),
    path('schedules/shifts/<int:pk>/', ShiftViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='schedules_shift_detail'),
    path('schedules/employee-shifts/', EmployeeShiftViewSet.as_view({'get': 'list', 'post': 'create'}), name='schedules_employee_shifts'),
    path('schedules/employee-shifts/<int:pk>/', EmployeeShiftViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='schedules_employee_shift_detail'),
    
    # Alias para attendance (frontend espera /attendance/*)
    path('attendance/logs/', AttendanceLogViewSet.as_view({'get': 'list'}), name='attendance_logs'),
    path('attendance/daily-attendance/', DailyAttendanceViewSet.as_view({'get': 'list', 'post': 'create'}), name='attendance_daily'),
    path('attendance/daily-attendance/<int:pk>/', DailyAttendanceViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='attendance_daily_detail'),
]
