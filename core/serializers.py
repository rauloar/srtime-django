from rest_framework import serializers
from .models import (
    Company, Position, Zone, Department, Employee,
    Device, AttendanceLog, ImportBatch, User, BiometricTemplate,
    Setting, Job, JobLog, Timetable, Shift, ShiftTimetable,
    ScheduleOverride, EmployeeShift, Leave, Holiday, DailyAttendance
)
from .enums import (
    get_punch_status_label, get_verify_mode_label, get_attendance_status_info
)


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = Department
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    current_shift = serializers.SerializerMethodField(read_only=True)
    current_timetable = serializers.SerializerMethodField(read_only=True)
    schedule_source = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'user_id', 'name', 'email', 'phone', 'mobile_phone', 'ssn',
            'department', 'department_name', 'position', 'position_name',
            'hire_date', 'birthday', 'gender', 'active',
            'address', 'city', 'country', 'photo_path',
            'current_shift', 'current_timetable', 'schedule_source'
        ]
    
    def get_current_shift(self, obj):
        """Get current shift assignment for employee"""
        from datetime import date
        from django.db.models import Q
        
        target_date = self.context.get('target_date', date.today())
        
        # Check EmployeeShift EMPLOYEE scope (priority)
        emp_shift = EmployeeShift.objects.filter(
            scope='EMPLOYEE',
            employee_id=obj.id,
            start_date__lte=target_date,
        ).filter(
            Q(end_date__gte=target_date) | Q(end_date__isnull=True)
        ).select_related('shift').first()
        
        if emp_shift and emp_shift.shift:
            return {
                'id': emp_shift.shift.id,
                'name': emp_shift.shift.name,
                'scope': 'EMPLOYEE',
                'start_date': emp_shift.start_date.isoformat(),
                'end_date': emp_shift.end_date.isoformat() if emp_shift.end_date else None
            }
        
        # Check EmployeeShift DEPARTMENT scope (fallback)
        if obj.department:
            dept_shift = EmployeeShift.objects.filter(
                scope='DEPARTMENT',
                department_id=obj.department.id,
                start_date__lte=target_date,
            ).filter(
                Q(end_date__gte=target_date) | Q(end_date__isnull=True)
            ).select_related('shift').first()
            
            if dept_shift and dept_shift.shift:
                return {
                    'id': dept_shift.shift.id,
                    'name': dept_shift.shift.name,
                    'scope': 'DEPARTMENT',
                    'start_date': dept_shift.start_date.isoformat(),
                    'end_date': dept_shift.end_date.isoformat() if dept_shift.end_date else None
                }
        
        return None
    
    def get_current_timetable(self, obj):
        """Get current timetable that will be applied for attendance calculation"""
        from datetime import date
        from core.services.schedule_resolver import resolve_schedule_unified
        
        target_date = self.context.get('target_date', date.today())
        
        try:
            resolved = resolve_schedule_unified(obj.id, target_date)
            
            if resolved.is_valid and resolved.timetable:
                tt = resolved.timetable
                return {
                    'id': tt.id,
                    'name': tt.name,
                    'on_duty_time': str(tt.on_duty_time) if tt.on_duty_time else None,
                    'off_duty_time': str(tt.off_duty_time) if tt.off_duty_time else None,
                    'is_flexible': tt.is_flexible,
                    'break_minutes': tt.break_minutes,
                    'late_allow_minutes': tt.late_allow_minutes,
                    'early_leave_allow_minutes': tt.early_leave_allow_minutes,
                    'overtime_threshold_minutes': tt.overtime_threshold_minutes,
                }
            
            return None
        except Exception:
            return None
    
    def get_schedule_source(self, obj):
        """Get schedule resolution source for this employee on target date"""
        from datetime import date
        from core.services.schedule_resolver import resolve_schedule_unified
        
        target_date = self.context.get('target_date', date.today())
        
        try:
            resolved = resolve_schedule_unified(obj.id, target_date)
            
            return {
                'is_valid': resolved.is_valid,
                'source': resolved.source.value if resolved.source else None,
                'error': resolved.error.value if resolved.error else None,
                'description': _get_source_description(resolved.source.value if resolved.source else None)
            }
        except Exception:
            return None


def _get_source_description(source: str) -> str:
    """Friendly description of schedule source"""
    descriptions = {
        'OVERRIDE': 'Manual exception for this date',
        'EMPLOYEE_SHIFT': 'Individual shift assignment',
        'DEPARTMENT_SHIFT': 'Departmental shift assignment',
        'IMPLICIT_REST': 'No schedule configured (rest day)',
        'UNRESOLVED': 'Schedule resolution error'
    }
    return descriptions.get(source, 'Unknown')


class DeviceSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source='zone_rel.name', read_only=True)
    
    class Meta:
        model = Device
        fields = '__all__'


class AttendanceLogSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    status_label = serializers.SerializerMethodField()
    verify_mode_label = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AttendanceLog
        fields = '__all__'
    
    def get_status_label(self, obj):
        """Return punch status label from enums"""
        return get_punch_status_label(obj.status)
    
    def get_verify_mode_label(self, obj):
        """Return verify mode label from enums"""
        if obj.verify_mode is None:
            return None
        return get_verify_mode_label(obj.verify_mode)
    
    def get_user_name(self, obj):
        """Get user name from Employee model by user_id"""
        try:
            from core.models import Employee
            employee = Employee.objects.get(user_id=obj.user_id)
            return employee.name
        except Employee.DoesNotExist:
            return None


class ImportBatchSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = ImportBatch
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = User
        fields = '__all__'


class BiometricTemplateSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = BiometricTemplate
        fields = '__all__'


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = '__all__'


class JobSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = Job
        fields = '__all__'


class JobLogSerializer(serializers.ModelSerializer):
    job_type = serializers.CharField(source='job.type', read_only=True)
    
    class Meta:
        model = JobLog
        fields = '__all__'


class TimetableSerializer(serializers.ModelSerializer):
    on_duty_time = serializers.TimeField(
        format="%H:%M:%S",
        input_formats=["%H:%M:%S", "%H:%M"],
    )
    off_duty_time = serializers.TimeField(
        format="%H:%M:%S",
        input_formats=["%H:%M:%S", "%H:%M"],
    )
    check_in_start = serializers.TimeField(
        format="%H:%M:%S",
        input_formats=["%H:%M:%S", "%H:%M"],
        allow_null=True,
        required=False,
    )
    check_in_end = serializers.TimeField(
        format="%H:%M:%S",
        input_formats=["%H:%M:%S", "%H:%M"],
        allow_null=True,
        required=False,
    )
    check_out_start = serializers.TimeField(
        format="%H:%M:%S",
        input_formats=["%H:%M:%S", "%H:%M"],
        allow_null=True,
        required=False,
    )
    check_out_end = serializers.TimeField(
        format="%H:%M:%S",
        input_formats=["%H:%M:%S", "%H:%M"],
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Timetable
        fields = '__all__'


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = '__all__'


class ShiftTimetableSerializer(serializers.ModelSerializer):
    shift_name = serializers.CharField(source='shift.name', read_only=True)
    timetable_name = serializers.CharField(source='timetable.name', read_only=True)
    
    class Meta:
        model = ShiftTimetable
        fields = '__all__'


class ScheduleOverrideSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    timetable_name = serializers.CharField(source='timetable.name', read_only=True)
    
    class Meta:
        model = ScheduleOverride
        fields = '__all__'


class EmployeeShiftSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    shift_name = serializers.CharField(source='shift.name', read_only=True)
    
    class Meta:
        model = EmployeeShift
        fields = '__all__'


class LeaveSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    
    class Meta:
        model = Leave
        fields = '__all__'


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'


class DailyAttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    employee_user_id = serializers.CharField(source='employee.user_id', read_only=True)
    timetable_name = serializers.CharField(source='timetable.name', read_only=True)
    status_info = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyAttendance
        fields = '__all__'
    
    def get_status_info(self, obj):
        """
        Returns attendance status information including label and color.
        Provides single source of truth for frontend rendering.
        """
        return get_attendance_status_info(obj.status)



