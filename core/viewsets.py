from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
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
    filterset_fields = ['device', 'user_id', 'status', 'punch', 'is_manual']
    search_fields = ['user_id', 'edited_reason', 'edited_by']
    ordering_fields = ['timestamp', 'user_id']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Optimize queries with select_related to avoid N+1"""
        return AttendanceLog.objects.select_related('device')

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
    permission_classes = [IsAuthenticated]

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
    filterset_fields = ['employee', 'timetable', 'date']
    search_fields = []
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']


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
    filterset_fields = ['employee', 'date', 'status', 'schedule_type', 'is_absent', 'timetable']
    search_fields = ['exception_reason']
    ordering_fields = ['date', 'employee', 'status']
    ordering = ['-date', 'employee']
