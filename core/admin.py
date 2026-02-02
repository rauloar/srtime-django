from django.contrib import admin
from .models import (
    Company, Position, Zone, Department, Employee,
    Device, AttendanceLog, ImportBatch, User, BiometricTemplate,
    Setting, Job, JobLog, Timetable, Shift, ShiftTimetable,
    ScheduleOverride, EmployeeShift, Leave, Holiday, DailyAttendance
)




@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'address', 'website']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'description']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'description']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'company', 'parent']
    list_filter = ['company', 'parent']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'name', 'department', 'position', 'active', 'hire_date']
    list_filter = ['active', 'department', 'position', 'gender']
    search_fields = ['user_id', 'name', 'email', 'phone', 'ssn']
    ordering = ['name']
    date_hierarchy = 'hire_date'


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'ip', 'port', 'enabled', 'zone_rel', 'last_seen', 'user_count', 'transaction_count']
    list_filter = ['enabled', 'zone_rel']
    search_fields = ['name', 'ip', 'serialnumber', 'device_name']
    ordering = ['name']
    readonly_fields = ['last_seen', 'user_count', 'face_count', 'fp_count', 'transaction_count', 'created_at']


@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'device', 'timestamp', 'status', 'punch']
    list_filter = ['device', 'status', 'punch']
    search_fields = ['user_id']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    readonly_fields = ['raw_json']


@admin.register(ImportBatch)
class ImportBatchAdmin(admin.ModelAdmin):
    list_display = ['id', 'device', 'imported_at', 'count']
    list_filter = ['device']
    ordering = ['-imported_at']
    date_hierarchy = 'imported_at'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'name', 'device', 'privilege', 'face_count', 'finger_count']
    list_filter = ['device', 'privilege']
    search_fields = ['user_id', 'name', 'card']
    ordering = ['user_id']


@admin.register(BiometricTemplate)
class BiometricTemplateAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'index', 'valid', 'version', 'created_at']
    list_filter = ['type', 'valid']
    search_fields = ['version']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'description']
    search_fields = ['key', 'value', 'description']
    ordering = ['key']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'device', 'status', 'progress', 'started_at', 'finished_at']
    list_filter = ['type', 'status', 'device']
    search_fields = ['id', 'type', 'error']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'started_at', 'finished_at', 'error']


@admin.register(JobLog)
class JobLogAdmin(admin.ModelAdmin):
    list_display = ['job', 'level', 'device_id', 'message', 'timestamp']
    list_filter = ['level', 'job']
    search_fields = ['message']
    ordering = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['name', 'on_duty_time', 'off_duty_time', 'late_allow_minutes', 'is_flexible', 'required_minutes']
    list_filter = ['is_flexible', 'rounding_rule']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    ordering = ['name']


@admin.register(ShiftTimetable)
class ShiftTimetableAdmin(admin.ModelAdmin):
    list_display = ['shift', 'timetable', 'day_index']
    list_filter = ['shift', 'day_index']
    ordering = ['shift', 'day_index']


@admin.register(ScheduleOverride)
class ScheduleOverrideAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'timetable', 'created_at']
    list_filter = ['timetable']
    search_fields = ['employee__name', 'employee__user_id']
    ordering = ['-date']
    date_hierarchy = 'date'


@admin.register(EmployeeShift)
class EmployeeShiftAdmin(admin.ModelAdmin):
    list_display = ['scope', 'employee', 'department', 'shift', 'start_date', 'end_date']
    list_filter = ['scope', 'shift']
    search_fields = ['employee__name', 'department__name']
    ordering = ['-start_date']
    date_hierarchy = 'start_date'


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_time', 'end_time', 'status']
    list_filter = ['leave_type', 'status']
    search_fields = ['employee__name', 'reason']
    ordering = ['-start_time']
    date_hierarchy = 'start_time'


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date']
    search_fields = ['name']
    ordering = ['start_date']
    date_hierarchy = 'start_date'


@admin.register(DailyAttendance)
class DailyAttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'status', 'check_in', 'check_out', 'late_minutes', 'worked_minutes', 'is_absent']
    list_filter = ['status', 'is_absent', 'date']
    search_fields = ['employee__name', 'employee__user_id', 'exception_reason']
    ordering = ['-date', 'employee']
    date_hierarchy = 'date'

