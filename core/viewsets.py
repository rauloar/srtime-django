from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import (
    Company, Position, Zone, Department, Employee,
    Device, AttendanceLog, ImportBatch, User, BiometricTemplate,
    Setting, Job, JobLog, Timetable, Shift, ShiftTimetable,
    ScheduleOverride, EmployeeShift, Leave, Holiday, DailyAttendance
)
from .serializers import (
    CompanySerializer, PositionSerializer,
    ZoneSerializer, DepartmentSerializer, EmployeeSerializer,
    DeviceSerializer, AttendanceLogSerializer, ImportBatchSerializer,
    UserSerializer, BiometricTemplateSerializer, SettingSerializer,
    JobSerializer, JobLogSerializer, TimetableSerializer,
    ShiftSerializer, ShiftTimetableSerializer, ScheduleOverrideSerializer,
    EmployeeShiftSerializer, LeaveSerializer, HolidaySerializer,
    DailyAttendanceSerializer
)





class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code']
    ordering = ['name']
    
    def list(self, request, *args, **kwargs):
        """Devolver array directo (sin paginación) como FastAPI"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code']
    ordering = ['name']
    
    def list(self, request, *args, **kwargs):
        """Devolver array directo (sin paginación) como FastAPI"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code']
    ordering = ['name']
    
    def list(self, request, *args, **kwargs):
        """Devolver array directo (sin paginación) como FastAPI"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company', 'parent', 'code']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code']
    ordering = ['name']
    
    def list(self, request, *args, **kwargs):
        """Devolver array directo (sin paginación) como FastAPI"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'position', 'active', 'gender']
    search_fields = ['user_id', 'name', 'email', 'phone', 'ssn']
    ordering_fields = ['user_id', 'name', 'hire_date']
    ordering = ['name']
    
    def get_serializer_context(self):
        """Add target_date to serializer context if provided in query params"""
        context = super().get_serializer_context()
        
        date_str = self.request.query_params.get('date')
        if date_str:
            try:
                from datetime import datetime
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                context['target_date'] = target_date
            except ValueError:
                pass  # Invalid date format, use default (today)
        
        return context
    
    def list(self, request, *args, **kwargs):
        """Adaptar respuesta para ser compatible con frontend FastAPI"""
        # Si tiene skip/limit, devolver array directo (sin paginación DRF)
        skip = request.query_params.get('skip')
        limit = request.query_params.get('limit')
        
        if skip is not None or limit is not None:
            # Aplicar filtros primero (antes del slice)
            queryset = self.filter_queryset(self.get_queryset())
            
            # Luego aplicar paginación manual
            skip = int(skip) if skip is not None else 0
            limit = int(limit) if limit is not None else 100
            
            queryset = queryset[skip:skip+limit]
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        
        # Si no, usar paginación normal DRF
        return super().list(request, *args, **kwargs)


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['enabled', 'zone_rel', 'zone']
    search_fields = ['name', 'ip', 'serialnumber', 'device_name', 'location']
    ordering_fields = ['name', 'ip', 'last_seen']
    ordering = ['name']
    
    def list(self, request, *args, **kwargs):
        """Devolver array directo (sin paginación) como FastAPI"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AttendanceLogViewSet(viewsets.ModelViewSet):
    queryset = AttendanceLog.objects.all()
    serializer_class = AttendanceLogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'device': ['exact'],
        'user_id': ['exact', 'icontains'],
        'status': ['exact'],
        'punch': ['exact'],
        'is_manual': ['exact'],
        'timestamp': ['gte', 'lte', 'range'],  # Support date range filtering
    }
    search_fields = ['user_id', 'user_name', 'edited_reason', 'edited_by']
    ordering_fields = ['timestamp', 'user_id']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Optimize queries with select_related and handle custom date filters"""
        queryset = AttendanceLog.objects.select_related('device')
        
        # Handle from_date and to_date query params (frontend compatibility)
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        device_id = self.request.query_params.get('device_id')  # Support device_id alias
        
        if from_date:
            queryset = queryset.filter(timestamp__gte=from_date)
        if to_date:
            queryset = queryset.filter(timestamp__lte=to_date)
        if device_id:  # Allow device_id as alias for device
            queryset = queryset.filter(device_id=device_id)
            
        return queryset

    def perform_create(self, serializer):
        data = serializer.validated_data
        edited_reason = data.get('edited_reason')
        is_manual = data.get('is_manual')

        if edited_reason or is_manual:
            user = self.request.user
            edited_by = data.get('edited_by')
            if not edited_by and user and user.is_authenticated:
                edited_by = user.username
            serializer.save(edited_by=edited_by, edited_at=timezone.now())
            return

        serializer.save()

    def perform_update(self, serializer):
        data = serializer.validated_data
        edited_reason = data.get('edited_reason')
        is_manual = data.get('is_manual')

        if edited_reason or is_manual:
            user = self.request.user
            edited_by = data.get('edited_by')
            if not edited_by and user and user.is_authenticated:
                edited_by = user.username
            serializer.save(edited_by=edited_by, edited_at=timezone.now())
            return

        serializer.save()


class ImportBatchViewSet(viewsets.ModelViewSet):
    queryset = ImportBatch.objects.all()
    serializer_class = ImportBatchSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['device']
    search_fields = []
    ordering_fields = ['imported_at', 'count']
    ordering = ['-imported_at']


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['device', 'privilege', 'group_id']
    search_fields = ['user_id', 'name', 'card']
    ordering_fields = ['user_id', 'name', 'updated_at']
    ordering = ['user_id']


class BiometricTemplateViewSet(viewsets.ModelViewSet):
    queryset = BiometricTemplate.objects.all()
    serializer_class = BiometricTemplateSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'type', 'valid']
    search_fields = ['version']
    ordering_fields = ['created_at', 'type', 'index']
    ordering = ['-created_at']


class SettingViewSet(viewsets.ModelViewSet):
    queryset = Setting.objects.all()
    serializer_class = SettingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['key']
    search_fields = ['key', 'value', 'description']
    ordering_fields = ['key']
    ordering = ['key']
    lookup_field = 'key'  # Setting usa 'key' como PK, no 'id'
    
    def list(self, request, *args, **kwargs):
        """Devolver array directo (sin paginación) como FastAPI"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Actualizar configuración individual por key"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'device', 'status']
    search_fields = ['type', 'error']
    ordering_fields = ['created_at', 'started_at', 'finished_at', 'progress']
    ordering = ['-created_at']


class JobLogViewSet(viewsets.ModelViewSet):
    queryset = JobLog.objects.all()
    serializer_class = JobLogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['job', 'level', 'device_id']
    search_fields = ['message']
    ordering_fields = ['timestamp']
    ordering = ['timestamp']


class TimetableViewSet(viewsets.ModelViewSet):
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_flexible', 'rounding_rule']
    search_fields = ['name']
    ordering_fields = ['name', 'on_duty_time', 'off_duty_time']
    ordering = ['name']
    
    def list(self, request, *args, **kwargs):
        """Devolver array directo (sin paginación) como FastAPI"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@method_decorator(csrf_exempt, name='timetables')
class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = []
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    @action(detail=True, methods=['get', 'post'])
    def timetables(self, request, pk=None):
        """
        GET: List shift cycle items
        POST: Configure shift cycle (replace all)
        """
        shift = self.get_object()
        
        if request.method == 'GET':
            items = ShiftTimetable.objects.filter(shift=shift).order_by('day_index')
            serializer = ShiftTimetableSerializer(items, many=True)
            return Response(serializer.data)
            
        elif request.method == 'POST':
            # Expect list of {timetable_id: int, day_index: int}
            data = request.data
            if not isinstance(data, list):
                return Response({"error": "Expected a list of items"}, status=400)
                
            # Clear existing
            ShiftTimetable.objects.filter(shift=shift).delete()
            
            created_items = []
            for item in data:
                tt_id = item.get('timetable_id')
                day_idx = item.get('day_index')
                
                if tt_id is not None and day_idx is not None:
                    st = ShiftTimetable.objects.create(
                        shift=shift,
                        timetable_id=tt_id,
                        day_index=day_idx
                    )
                    created_items.append(st)
            
            serializer = ShiftTimetableSerializer(created_items, many=True)
            return Response(serializer.data)
    
    def list(self, request, *args, **kwargs):
        """Devolver array directo (sin paginación) como FastAPI"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ShiftTimetableViewSet(viewsets.ModelViewSet):
    queryset = ShiftTimetable.objects.all()
    serializer_class = ShiftTimetableSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['shift', 'timetable', 'day_index']
    search_fields = []
    ordering_fields = ['shift', 'day_index']
    ordering = ['shift', 'day_index']


class ScheduleOverrideViewSet(viewsets.ModelViewSet):
    queryset = ScheduleOverride.objects.all()
    serializer_class = ScheduleOverrideSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'employee': ['exact'],
        'timetable': ['exact'],
        'date': ['exact', 'gte', 'lte', 'range']
    }
    search_fields = []
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']

    def list(self, request, *args, **kwargs):
        """Devolver array directo (sin paginación) como FastAPI"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='from-shift')
    def create_from_shift(self, request):
        """
        Create/update a schedule override using a shift and date.

        Body:
        {
          "employee_id": 1,
          "shift_id": 2,
          "date": "2026-02-09",
          "start_date": "2026-02-01"  # Optional, required if shift.cycle_days > 0
        }
        """
        employee_id = request.data.get('employee_id')
        shift_id = request.data.get('shift_id')
        date_str = request.data.get('date')
        start_date_str = request.data.get('start_date')

        if not employee_id or not shift_id or not date_str:
            return Response(
                {"error": "employee_id, shift_id, and date are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from datetime import datetime
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            employee = Employee.objects.get(id=employee_id)
            shift = Shift.objects.get(id=shift_id)
        except (Employee.DoesNotExist, Shift.DoesNotExist):
            return Response(
                {"error": "Employee or shift not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Resolve day_index dynamically
        if shift.cycle_days and shift.cycle_days > 0:
            if not start_date_str:
                return Response(
                    {"error": "start_date is required for shifts with cycle_days"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"error": "Invalid start_date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            day_index = (target_date - start_date).days % shift.cycle_days
        else:
            day_index = target_date.weekday()

        shift_tt = ShiftTimetable.objects.filter(
            shift=shift,
            day_index=day_index
        ).select_related('timetable').first()

        if not shift_tt or not shift_tt.timetable:
            return Response(
                {"error": "No timetable configured for this shift on the selected date"},
                status=status.HTTP_400_BAD_REQUEST
            )

        override, _ = ScheduleOverride.objects.update_or_create(
            employee=employee,
            date=target_date,
            defaults={"timetable": shift_tt.timetable}
        )

        serializer = self.get_serializer(override)
        return Response(serializer.data)


class EmployeeShiftViewSet(viewsets.ModelViewSet):
    queryset = EmployeeShift.objects.all()
    serializer_class = EmployeeShiftSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['scope', 'employee', 'department', 'shift']
    search_fields = []
    ordering_fields = ['start_date', 'end_date']
    ordering = ['-start_date']
    
    def list(self, request, *args, **kwargs):
        """Devolver array directo (sin paginación) como FastAPI"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LeaveViewSet(viewsets.ModelViewSet):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'leave_type', 'status']
    search_fields = ['reason']
    ordering_fields = ['start_time', 'end_time', 'status']
    ordering = ['-start_time']


class HolidayViewSet(viewsets.ModelViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = []
    search_fields = ['name']
    ordering_fields = ['start_date', 'end_date']
    ordering = ['start_date']


class DailyAttendanceViewSet(viewsets.ModelViewSet):
    queryset = DailyAttendance.objects.all()
    serializer_class = DailyAttendanceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'employee': ['exact'],
        'employee__user_id': ['exact', 'icontains'],  # Search by employee user_id
        'employee__name': ['exact', 'icontains'],      # Search by employee name
        'date': ['exact', 'gte', 'lte', 'range'],      # Date range filtering
        'status': ['exact', 'icontains'],
        'schedule_type': ['exact'],
        'is_absent': ['exact'],
        'timetable': ['exact'],
    }
    search_fields = ['exception_reason', 'employee__name', 'employee__user_id']  # Full-text search
    ordering_fields = ['date', 'employee__id', 'status']
    ordering = ['-date', 'employee__id']

    def get_queryset(self):
        """Optimize queries with select_related and handle filters"""
        queryset = DailyAttendance.objects.select_related('employee', 'timetable')
        
        # Support date range via query params
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        
        if from_date:
            queryset = queryset.filter(date__gte=from_date)
        if to_date:
            queryset = queryset.filter(date__lte=to_date)
            
        return queryset
    
    def get_permissions(self):
        """Custom permissions for shadow mode endpoint."""
        if self.action == 'shadow_comparison':
            # Allow any authenticated user to view shadow comparisons (for monitoring)
            return [AllowAny()]
        return [AllowAny()]
    
    @action(detail=False, methods=['get'])
    def shadow_comparison(self, request):
        """
        Get shadow mode comparison for a specific employee and date.
        
        Query params:
            - employee_id: Employee ID
            - date: Date (YYYY-MM-DD)
        
        Returns:
            Shadow mode comparison result (V1 vs V2)
        """
        from rest_framework.response import Response
        from .services.shadow_mode_service import ShadowModeService
        from datetime import datetime
        
        employee_id = request.query_params.get('employee_id')
        date_str = request.query_params.get('date')
        
        if not employee_id or not date_str:
            return Response(
                {'error': 'Missing required parameters: employee_id, date'},
                status=400
            )
        
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': f'Invalid date format: {date_str}. Use YYYY-MM-DD'},
                status=400
            )
        
        # Get V1 results (if exists)
        daily = DailyAttendance.objects.filter(
            employee_id=employee_id,
            date=target_date
        ).first()
        
        # Run shadow mode comparison
        shadow = ShadowModeService()
        comparison = shadow.validate_daily_calculation(
            employee_id=int(employee_id),
            target_date=target_date,
            v1_daily_attendance=daily
        )
        
        if not comparison:
            return Response(
                {'error': 'Shadow mode is disabled or failed to generate comparison'},
                status=503
            )
        
        return Response(
            {
                'employee_id': comparison.employee_id,
                'date': str(comparison.target_date),
                'v1': {
                    'status': comparison.v1_status,
                    'worked_minutes': comparison.v1_worked_minutes,
                    'late_minutes': comparison.v1_late_minutes,
                    'early_minutes': comparison.v1_early_minutes,
                    'error': comparison.v1_error,
                },
                'v2': {
                    'status': comparison.v2_status,
                    'worked_minutes': comparison.v2_worked_minutes,
                    'late_minutes': comparison.v2_late_minutes,
                    'early_minutes': comparison.v2_early_minutes,
                    'error': comparison.v2_error,
                },
                'comparison': {
                    'matches': not comparison.has_differences,
                    'differences': comparison.differences,
                    'timestamp': comparison.comparison_timestamp.isoformat(),
                },
            }
        )