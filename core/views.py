from django.db.models import Count, Avg, Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .enums import (
    PUNCH_STATUS,
    VERIFY_MODE,
    ATTENDANCE_STATUS,
    ATTENDANCE_PRESENT_STATUSES,
    ATTENDANCE_ABSENT_STATUS
)
from .models import Company, Employee, Department, Shift, Timetable, DailyAttendance, User


@api_view(['GET'])
def api_root(request):
    """
    Raíz de la API config.
    Proporciona información general sobre los endpoints disponibles.
    """
    return Response({
        'message': 'Bienvenido a config API',
        'version': '1.0.0',
        'documentation': 'http://127.0.0.1:9000/admin/',
        'admin': {
            'url': '/admin/',
            'username': 'admin',
            'note': 'Django Admin panel'
        },
        'api': {
            'base_url': '/api/v1/',
            'description': 'REST API con 24 endpoints para gestión de empleados, dispositivos ZKTeco, asistencia y horarios'
        },
        'endpoints': {
            'autenticacion': [
                'POST /api/token/ - Obtener token JWT',
                'POST /api/token/refresh/ - Refrescar token'
            ],
            'organizacion': [
                'GET/POST /api/v1/companies/',
                'GET/POST /api/v1/positions/',
                'GET/POST /api/v1/zones/',
                'GET/POST /api/v1/departments/',
                'GET/POST /api/v1/employees/'
            ],
            'dispositivos': [
                'GET/POST /api/v1/devices/',
                'GET/POST /api/v1/attendance-logs/',
                'GET/POST /api/v1/import-batches/',
                'GET/POST /api/v1/users/',
                'GET/POST /api/v1/biometric-templates/'
            ],
            'sistema': [
                'GET/POST /api/v1/settings/',
                'GET/POST /api/v1/jobs/',
                'GET/POST /api/v1/job-logs/'
            ],
            'horarios': [
                'GET/POST /api/v1/timetables/',
                'GET/POST /api/v1/shifts/',
                'GET/POST /api/v1/shift-timetables/',
                'GET/POST /api/v1/schedule-overrides/',
                'GET/POST /api/v1/employee-shifts/'
            ],
            'ausencias': [
                'GET/POST /api/v1/leaves/',
                'GET/POST /api/v1/holidays/',
                'GET /api/v1/attendance/absences/'
            ],
            'asistencia': [
                'GET/POST /api/v1/daily-attendance/',
                'POST /api/v1/attendance/calculate/',
                'POST /api/v1/attendance/calculate/detailed/',
                'GET /api/v1/attendance/reports/daily/',
                'GET /api/v1/attendance/logs/',
                'GET /api/v1/attendance/'
            ]
        },
        'caracteristicas': {
            'filtros': 'Disponible en todos los endpoints: ?field=value',
            'busqueda': 'Disponible con ?search=texto',
            'ordenamiento': 'Disponible con ?ordering=campo o ?ordering=-campo',
            'paginacion': 'Automática: 100 items por página',
            'autenticacion': 'JWT Bearer Token en header Authorization'
        },
        'ejemplos': {
            'obtener_token': 'curl -X POST http://127.0.0.1:9000/api/token/ -d "username=admin&password=admin123"',
            'listar_empleados': 'curl -H "Authorization: Bearer <token>" http://127.0.0.1:9000/api/v1/employees/',
            'filtrar': 'curl -H "Authorization: Bearer <token>" http://127.0.0.1:9000/api/v1/employees/?department=1',
            'buscar': 'curl -H "Authorization: Bearer <token>" http://127.0.0.1:9000/api/v1/employees/?search=Juan'
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def api_v1_info(request):
    """
    Información sobre la API v1.
    """
    return Response({
        'version': '1.0.0',
        'message': 'SRTimeWeb API v1',
        'endpoints_count': 24,
        'models': [
            'Company', 'Position', 'Zone', 'Department', 'Employee',
            'Device', 'AttendanceLog', 'ImportBatch', 'User', 'BiometricTemplate',
            'Setting', 'Job', 'JobLog', 'Timetable', 'Shift', 'ShiftTimetable',
            'ScheduleOverride', 'EmployeeShift', 'Leave', 'Holiday', 'DailyAttendance'
        ],
        'database': {
            'engine': 'PostgreSQL 18',
            'name': 'srtimeweb',
            'timezone': 'America/Argentina/Buenos_Aires',
            'language': 'es-ar'
        },
        'features': {
            'jwt_authentication': True,
            'cors_enabled': True,
            'filtering': True,
            'searching': True,
            'ordering': True,
            'pagination': True
        }
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def enums_list(request):
    """
    API Enumerations endpoint
    Provides all enum definitions used across the system for frontend consumption.
    
    This is the source of truth for:
    - Punch status codes (0, 1, 2, etc.)
    - Verify mode codes (1, 3, 4, 15, 25)
    - Attendance status values (Normal, Absent, Late, etc.)
    
    Frontend should use these values to avoid hardcoding enums.
    """
    return Response({
        'message': 'API Enumerations - Source of truth for all enum values',
        'version': '1.0.0',
        'punch_status': PUNCH_STATUS,
        'verify_mode': VERIFY_MODE,
        'attendance_status': ATTENDANCE_STATUS,
        'usage': {
            'punch_status': 'Use status_label from AttendanceLog response instead of mapping locally',
            'verify_mode': 'Use verify_mode_label from AttendanceLog response instead of mapping locally',
            'attendance_status': 'Use backend returned status with color info from this endpoint'
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def dashboard_summary(request):
    """
    Dashboard summary endpoint.
    Provides master counts and historical report summaries only (no live data).
    """
    try:
        limit = int(request.query_params.get('limit', 5))
    except (TypeError, ValueError):
        limit = 5

    counts = {
        'employees': Employee.objects.count(),
        'departments': Department.objects.count(),
        'shifts': Shift.objects.count(),
        'timetables': Timetable.objects.count(),
        'groups': User.objects.exclude(group_id__isnull=True).values('group_id').distinct().count()
    }

    company_name = Company.objects.values_list('name', flat=True).first()

    recent_reports = list(
        DailyAttendance.objects
        .values('date')
        .annotate(
            total_records=Count('id'),
            present=Count('id', filter=Q(status__in=ATTENDANCE_PRESENT_STATUSES)),
            absent=Count('id', filter=Q(status=ATTENDANCE_ABSENT_STATUS)),
            avg_worked_minutes=Avg('worked_minutes')
        )
        .order_by('-date')[:limit]
    )

    return Response({
        'message': 'Dashboard summary (historical and master data only)',
        'version': '1.0.0',
        'counts': counts,
        'company_name': company_name,
        'recent_reports': recent_reports,
        'meta': {
            'limit': limit
        }
    }, status=status.HTTP_200_OK)