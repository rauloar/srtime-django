from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
def api_root(request):
    """
    Raíz de la API SRTimeWeb.
    Proporciona información general sobre los endpoints disponibles.
    """
    return Response({
        'message': 'Bienvenido a SRTimeWeb API',
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
                'GET/POST /api/v1/auth-users/',
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
                'GET/POST /api/v1/holidays/'
            ],
            'asistencia': [
                'GET/POST /api/v1/daily-attendance/'
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
