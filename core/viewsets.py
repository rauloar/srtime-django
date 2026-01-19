from rest_framework import viewsets, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    AuthUser, Company, Position, Zone, Department, Employee,
    Device, AttendanceLog, ImportBatch, User, BiometricTemplate,
    Setting, Job, JobLog, Timetable, Shift, ShiftTimetable,
    ScheduleOverride, EmployeeShift, Leave, Holiday, DailyAttendance
)
from .serializers import (
    AuthUserSerializer, CompanySerializer, PositionSerializer,
    ZoneSerializer, DepartmentSerializer, EmployeeSerializer,
    DeviceSerializer, AttendanceLogSerializer, ImportBatchSerializer,
    UserSerializer, BiometricTemplateSerializer, SettingSerializer,
    JobSerializer, JobLogSerializer, TimetableSerializer,
    ShiftSerializer, ShiftTimetableSerializer, ScheduleOverrideSerializer,
    EmployeeShiftSerializer, LeaveSerializer, HolidaySerializer,
    DailyAttendanceSerializer
)


class AuthUserViewSet(viewsets.ModelViewSet):
    queryset = AuthUser.objects.all()
    serializer_class = AuthUserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'active', 'employee']
    search_fields = ['username']
    ordering_fields = ['username', 'created_at']
    ordering = ['-created_at']


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code']
    ordering = ['name']


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code']
    ordering = ['name']


class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code']
    ordering = ['name']


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


class AttendanceLogViewSet(viewsets.ModelViewSet):
    queryset = AttendanceLog.objects.all()
    serializer_class = AttendanceLogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['device', 'user_id', 'status', 'punch']
    search_fields = ['user_id']
    ordering_fields = ['timestamp', 'user_id']
    ordering = ['-timestamp']
    
    def list(self, request, *args, **kwargs):
        """Devolver array directo como FastAPI"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


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


class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = []
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']


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
