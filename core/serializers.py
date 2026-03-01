from rest_framework import serializers
from .models import (
    Company, Position, Zone, Department, Employee,
    Device, AttendanceLog, ImportBatch, DeviceUser, BiometricTemplate,
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
    active = serializers.BooleanField(source='is_active', required=False)
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
            'hire_date', 'birthday', 'gender', 'is_active', 'active',
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
        """Get employee name from FK, fallback to lookup by user_id."""
        if getattr(obj, 'employee', None):
            return obj.employee.name

        try:
            from core.models import Employee
            employee = Employee.objects.get(user_id=obj.user_id)
            return employee.name
        except Employee.DoesNotExist:
            return None
    
    def validate(self, data):
        """Resolve employee FK from payload and keep user_id synchronized."""
        from core.models import Employee

        current_employee = getattr(self.instance, 'employee', None) if self.instance else None
        current_user_id = getattr(self.instance, 'user_id', None) if self.instance else None

        employee = data.get('employee', current_employee)
        user_id = data.get('user_id', current_user_id)

        if employee is None and user_id:
            employee = Employee.objects.filter(user_id=user_id).first()
            if employee is None:
                raise serializers.ValidationError({
                    'user_id': (
                        f"Employee with user_id '{user_id}' does not exist in HR system. "
                        f"HR system is the source of truth for employee master data. "
                        f"Please sync device users to HR system first."
                    )
                })

        if employee is None:
            raise serializers.ValidationError({
                'employee': 'Employee is required for attendance logs.'
            })

        data['employee'] = employee
        data['user_id'] = employee.user_id
        return data


class ImportBatchSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = ImportBatch
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = DeviceUser
        exclude = ['id']

    def to_representation(self, instance):
        """Merge HR Employee data into the response"""
        data = super().to_representation(instance)
        
        if instance.user_id:
            from .models import Employee
            # Try to find linked HR employee
            emp = Employee.objects.filter(user_id=instance.user_id).select_related('department', 'position').first()
            if emp:
                # Merge HR fields (frontend expects these at top level)
                data['email'] = emp.email
                data['phone'] = emp.phone
                data['mobile_phone'] = emp.mobile_phone
                data['address'] = emp.address
                data['city'] = emp.city
                data['country'] = emp.country
                data['birthday'] = emp.birthday
                data['gender'] = emp.gender
                data['ssn'] = emp.ssn
                data['photo_path'] = emp.photo_path
                data['hire_date'] = emp.hire_date
                
                # Relations
                data['department_id'] = emp.department_id
                data['department_name'] = emp.department.name if emp.department else None
                data['position'] = emp.position_id
                data['position_name'] = emp.position.name if emp.position else None
                
        return data


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
        allow_null=True,
        required=False,
    )
    off_duty_time = serializers.TimeField(
        format="%H:%M:%S",
        input_formats=["%H:%M:%S", "%H:%M"],
        allow_null=True,
        required=False,
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
    
    def validate(self, data):
        """Validación personalizada para horarios flexibles vs fijos"""
        is_flexible = data.get('is_flexible', False)
        
        # Para horarios fijos, on_duty_time y off_duty_time son requeridos
        if not is_flexible:
            if not data.get('on_duty_time'):
                raise serializers.ValidationError(
                    {"on_duty_time": "Este campo es requerido para horarios fijos."}
                )
            if not data.get('off_duty_time'):
                raise serializers.ValidationError(
                    {"off_duty_time": "Este campo es requerido para horarios fijos."}
                )
        
        return data


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = '__all__'


class ShiftTimetableSerializer(serializers.ModelSerializer):
    shift_name = serializers.CharField(source='shift.name', read_only=True)
    timetable_name = serializers.CharField(source='timetable.name', read_only=True)
    timetable_id = serializers.IntegerField(source='timetable.id', read_only=True)
    
    class Meta:
        model = ShiftTimetable
        fields = ['id', 'shift', 'shift_name', 'timetable', 'timetable_id', 'timetable_name', 'day_index']


class ScheduleOverrideSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    timetable_name = serializers.CharField(source='timetable.name', read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        source='employee',
        queryset=Employee.objects.all(),
        required=False,
        allow_null=True
    )
    user_id = serializers.SlugRelatedField(
        source='employee',
        slug_field='user_id',
        queryset=Employee.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = ScheduleOverride
        exclude = ['employee']


class EmployeeShiftSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    shift_name = serializers.CharField(source='shift.name', read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        source='employee',
        queryset=Employee.objects.all(),
        required=False,
        allow_null=True
    )
    user_id = serializers.SlugRelatedField(
        source='employee',
        slug_field='user_id',
        queryset=Employee.objects.all(),
        allow_null=True,
        required=False
    )
    
    class Meta:
        model = EmployeeShift
        exclude = ['employee']
    
    def validate(self, data):
        """
        Verify that assigned shift has at least one ShiftTimetable configured.
        
        Fail-fast validation to prevent assigning misconfigured shifts.
        Without this check, employees assigned to shifts without timetables
        would be silently treated as IMPLICIT_REST during schedule resolution.
        """
        # Get shift from data (create) or instance (update)
        shift = data.get('shift') or (self.instance.shift if self.instance else None)
        
        if shift:
            has_timetables = ShiftTimetable.objects.filter(shift=shift).exists()
            if not has_timetables:
                raise serializers.ValidationError(
                    f"El turno '{shift.name}' no tiene ciclo configurado. "
                    "Configure al menos un horario antes de asignarlo."
                )
        
        return data


class LeaveSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        source='employee',
        queryset=Employee.objects.all(),
        required=False,
        allow_null=True
    )
    user_id = serializers.SlugRelatedField(
        source='employee',
        slug_field='user_id',
        queryset=Employee.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Leave
        exclude = ['employee']


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'


class DailyAttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    employee_user_id = serializers.CharField(source='employee.user_id', read_only=True)
    user_id = serializers.CharField(source='employee.user_id', read_only=True)
    timetable_name = serializers.CharField(source='timetable.name', read_only=True)
    status_info = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyAttendance
        exclude = ['employee']
    
    def get_status_info(self, obj):
        """
        Returns attendance status information including label and color.
        Provides single source of truth for frontend rendering.
        """
        return get_attendance_status_info(obj.status)


class DailyAttendanceV2Serializer(serializers.ModelSerializer):
    """
    CONTRATO FORMAL v2 - Dominio fuerte
    
    Estructura de respuesta EXACTA y GARANTIZADA:
    {
      "identity": { "id", "user_id", "date" },
      "status": { "code", "label", "color" },
      "metrics": { "worked_minutes", "late_minutes", "early_minutes", "overtime_minutes" },
      "schedule": { "check_in", "check_out" },
      "employee": { "name", "user_id", "department_name" }
    }
    
    REGLAS INVIOLABLES:
    - Campos numéricos NUNCA null (garantizados)
    - status.code siempre presente
    - status.label siempre presente
    - status.color siempre {light, dark} theme-aware
    - employee.name siempre presente
    - employee.user_id siempre presente
    """
    
    identity = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    metrics = serializers.SerializerMethodField()
    schedule = serializers.SerializerMethodField()
    employee = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyAttendance
        fields = ['identity', 'status', 'metrics', 'schedule', 'employee']
    
    def get_identity(self, obj):
        """Identidad del registro"""
        return {
            'id': obj.id,
            'user_id': obj.employee.user_id if obj.employee else None,
            'date': obj.date.isoformat()
        }
    
    def get_status(self, obj):
        """
        Estado normalizado con código canónico.
        Mapeo: "Normal" → "NORMAL", "Late" → "LATE", etc.
        """
        status_info = get_attendance_status_info(obj.status)
        
        # Mapeo de status textual a código canónico en UPPER_CASE con underscore
        status_code_map = {
            'Normal': 'NORMAL',
            'Late': 'LATE',
            'Absent': 'ABSENT',
            'Early': 'EARLY',
            'Partial': 'PARTIAL',
            'Leave': 'LEAVE',
            'Worked': 'WORKED',
            'Incomplete': 'INCOMPLETE',
            'Excessive': 'EXCESSIVE',
            'HolidayWorked': 'HOLIDAY_WORKED',
            'Rest Day': 'REST_DAY',
        }
        
        canonical_code = status_code_map.get(obj.status, obj.status.upper().replace(" ", "_"))
        
        return {
            'code': canonical_code,
            'label': status_info.get('display', obj.status),
            'color': status_info.get('color', '#666666')
        }
    
    def get_metrics(self, obj):
        """Métricas numéricas - GARANTIZADAS no-null"""
        return {
            'worked_minutes': obj.worked_minutes or 0,
            'late_minutes': obj.late_minutes or 0,
            'early_minutes': obj.early_minutes or 0,
            'overtime_minutes': obj.overtime_minutes or 0
        }
    
    def get_schedule(self, obj):
        """Timestamps de entrada/salida"""
        return {
            'check_in': obj.check_in.isoformat() if obj.check_in else None,
            'check_out': obj.check_out.isoformat() if obj.check_out else None
        }
    
    def get_employee(self, obj):
        """Información del empleado - GARANTIZADA completa"""
        return {
                'id': obj.employee.id if obj.employee else None,
            'name': obj.employee.name if obj.employee else '',
            'user_id': obj.employee.user_id if obj.employee else '',
            'department_name': obj.employee.department.name if obj.employee and obj.employee.department else None
        }
