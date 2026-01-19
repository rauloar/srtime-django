from rest_framework import serializers
from .models import (
    AuthUser, Company, Position, Zone, Department, Employee,
    Device, AttendanceLog, ImportBatch, User, BiometricTemplate,
    Setting, Job, JobLog, Timetable, Shift, ShiftTimetable,
    ScheduleOverride, EmployeeShift, Leave, Holiday, DailyAttendance
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
    
    class Meta:
        model = Employee
        fields = '__all__'


class DeviceSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source='zone_rel.name', read_only=True)
    
    class Meta:
        model = Device
        fields = '__all__'


class AttendanceLogSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = AttendanceLog
        fields = '__all__'


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
    
    class Meta:
        model = DailyAttendance
        fields = '__all__'


class AuthUserSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    
    class Meta:
        model = AuthUser
        fields = ['id', 'username', 'role', 'employee', 'employee_name', 'active', 'created_at']
        read_only_fields = ['id', 'created_at']
