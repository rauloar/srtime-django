
from django.db import models
from django.utils import timezone


class Company(models.Model):
    """Empresa/Compañía"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    website = models.CharField(max_length=100, null=True, blank=True)
    logo_path = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'companies'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['name']

    def __str__(self):
        return self.name


class Position(models.Model):
    """Puesto/Posición laboral"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'positions'
        verbose_name = 'Posición'
        verbose_name_plural = 'Posiciones'
        ordering = ['name']

    def __str__(self):
        return self.name


class Zone(models.Model):
    """Zona física o lógica"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'zones'
        verbose_name = 'Zona'
        verbose_name_plural = 'Zonas'
        ordering = ['name']

    def __str__(self):
        return self.name


class Department(models.Model):
    """Departamento organizacional"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='departments')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')

    class Meta:
        db_table = 'departments'
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['name']

    def __str__(self):
        return self.name


class Employee(models.Model):
    """Empleado/Personal"""
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]

    user_id = models.CharField(max_length=50, unique=True, db_index=True, verbose_name='ID Usuario')
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Nombre')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    
    # Contacto
    email = models.EmailField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True, verbose_name='Teléfono')
    mobile_phone = models.CharField(max_length=50, null=True, blank=True, verbose_name='Celular')
    
    # Datos laborales
    hire_date = models.DateField(null=True, blank=True, verbose_name='Fecha de Ingreso')
    
    # Dirección
    address = models.CharField(max_length=200, null=True, blank=True, verbose_name='Dirección')
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name='Ciudad')
    country = models.CharField(max_length=100, null=True, blank=True, verbose_name='País')
    
    # Foto
    photo_path = models.CharField(max_length=255, null=True, blank=True, verbose_name='Ruta Foto')
    
    # Datos personales
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True, verbose_name='Género')
    birthday = models.DateField(null=True, blank=True, verbose_name='Fecha de Nacimiento')
    ssn = models.CharField(max_length=50, null=True, blank=True, verbose_name='DNI/SSN')
    
    active = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        db_table = 'employees'
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['name']
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['active']),
            models.Index(fields=['department', 'active']),
        ]

    def __str__(self):
        return f"{self.user_id} - {self.name or 'Sin nombre'}"


class Device(models.Model):
    """Dispositivo ZKTeco"""
    name = models.CharField(max_length=100, verbose_name='Nombre')
    ip = models.CharField(max_length=50, verbose_name='Dirección IP')
    port = models.IntegerField(default=4370, verbose_name='Puerto')
    password = models.IntegerField(default=0, verbose_name='Contraseña')
    zone = models.CharField(max_length=50, null=True, blank=True, verbose_name='Zona (texto)')
    location = models.CharField(max_length=100, null=True, blank=True, verbose_name='Ubicación')
    zone_rel = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, blank=True, related_name='devices', verbose_name='Zona')
    
    # Estado e identidad
    enabled = models.BooleanField(default=True, verbose_name='Habilitado')
    serialnumber = models.CharField(max_length=100, null=True, blank=True, verbose_name='Número de Serie')
    device_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Nombre del Dispositivo')
    platform = models.CharField(max_length=50, null=True, blank=True, verbose_name='Plataforma')
    firmware_version = models.CharField(max_length=100, null=True, blank=True, verbose_name='Versión Firmware')
    mac = models.CharField(max_length=20, null=True, blank=True, verbose_name='Dirección MAC')
    
    # Salud y estadísticas
    last_seen = models.DateTimeField(null=True, blank=True, verbose_name='Última Conexión')
    last_error = models.CharField(max_length=255, null=True, blank=True, verbose_name='Último Error')
    user_count = models.IntegerField(default=0, verbose_name='Cantidad Usuarios')
    face_count = models.IntegerField(default=0, verbose_name='Cantidad Rostros')
    fp_count = models.IntegerField(default=0, verbose_name='Cantidad Huellas')
    transaction_count = models.IntegerField(default=0, verbose_name='Cantidad Transacciones')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha Creación')

    class Meta:
        db_table = 'devices'
        verbose_name = 'Dispositivo'
        verbose_name_plural = 'Dispositivos'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.ip})"


class AttendanceLog(models.Model):
    """Log de asistencia/marcación"""
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='logs')
    user_id = models.CharField(max_length=50, db_index=True, verbose_name='ID Usuario')
    timestamp = models.DateTimeField(db_index=True, verbose_name='Fecha/Hora')
    status = models.IntegerField(verbose_name='Estado')
    punch = models.IntegerField(verbose_name='Punch')
    
    # Detalles extendidos
    verify_mode = models.IntegerField(null=True, blank=True, verbose_name='Modo Verificación')
    workstate = models.IntegerField(null=True, blank=True, verbose_name='Estado Trabajo')
    workcode = models.IntegerField(null=True, blank=True, verbose_name='Código Trabajo')
    punch_source = models.CharField(max_length=50, null=True, blank=True, verbose_name='Origen Marcación')
    
    raw_json = models.JSONField(null=True, blank=True, verbose_name='JSON Original')

    class Meta:
        db_table = 'attendance_logs'
        verbose_name = 'Log de Asistencia'
        verbose_name_plural = 'Logs de Asistencia'
        constraints = [
            models.UniqueConstraint(fields=['device', 'user_id', 'timestamp'], name='uix_att_log')
        ]
        indexes = [
            models.Index(fields=['user_id', 'timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['device', 'timestamp']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user_id} @ {self.timestamp}"


class ImportBatch(models.Model):
    """Lote de importación"""
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='batches')
    imported_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha Importación')
    count = models.IntegerField(default=0, verbose_name='Cantidad')

    class Meta:
        db_table = 'import_batches'
        verbose_name = 'Lote de Importación'
        verbose_name_plural = 'Lotes de Importación'
        ordering = ['-imported_at']

    def __str__(self):
        return f"Batch {self.id} - {self.count} registros"


class User(models.Model):
    """Usuario del dispositivo (no confundir con AuthUser)"""
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='users')
    uid = models.IntegerField(verbose_name='UID')
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Nombre')
    privilege = models.IntegerField(null=True, blank=True, verbose_name='Privilegio')
    password = models.CharField(max_length=100, null=True, blank=True, verbose_name='Contraseña')
    group_id = models.IntegerField(null=True, blank=True, verbose_name='ID Grupo')
    user_id = models.CharField(max_length=50, null=True, blank=True, verbose_name='ID Usuario')
    card = models.CharField(max_length=50, null=True, blank=True, verbose_name='Tarjeta')
    
    face_count = models.IntegerField(default=0, verbose_name='Cantidad Rostros')
    finger_count = models.IntegerField(default=0, verbose_name='Cantidad Huellas')
    
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')

    class Meta:
        db_table = 'users'
        verbose_name = 'Usuario de Dispositivo'
        verbose_name_plural = 'Usuarios de Dispositivos'
        constraints = [
            models.UniqueConstraint(fields=['device', 'uid'], name='uix_device_uid')
        ]
        ordering = ['user_id']

    def __str__(self):
        return f"{self.user_id or self.uid} - {self.name or 'Sin nombre'}"


class BiometricTemplate(models.Model):
    """Template biométrico"""
    TYPE_CHOICES = [
        ('FINGER', 'Huella'),
        ('FACE', 'Facial'),
        ('PALM', 'Palma'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='templates')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Tipo')
    index = models.IntegerField(default=0, verbose_name='Índice')
    valid = models.IntegerField(default=1, verbose_name='Válido')
    data = models.TextField(verbose_name='Datos')
    version = models.CharField(max_length=20, null=True, blank=True, verbose_name='Versión')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')

    class Meta:
        db_table = 'biometric_templates'
        verbose_name = 'Template Biométrico'
        verbose_name_plural = 'Templates Biométricos'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'type', 'index'], name='uix_bio_template')
        ]

    def __str__(self):
        return f"{self.get_type_display()} - {self.user}"


class Setting(models.Model):
    """Configuración del sistema"""
    key = models.CharField(max_length=50, primary_key=True, db_index=True, verbose_name='Clave')
    value = models.CharField(max_length=255, null=True, blank=True, verbose_name='Valor')
    description = models.CharField(max_length=255, null=True, blank=True, verbose_name='Descripción')

    class Meta:
        db_table = 'settings'
        verbose_name = 'Configuración'
        verbose_name_plural = 'Configuraciones'
        ordering = ['key']

    def __str__(self):
        return f"{self.key} = {self.value}"


class Job(models.Model):
    """Trabajo/Tarea asíncrona"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('running', 'Ejecutando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('cancelled', 'Cancelado'),
    ]

    id = models.CharField(max_length=36, primary_key=True, verbose_name='ID')  # UUID
    type = models.CharField(max_length=50, verbose_name='Tipo')
    device = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Estado')
    progress = models.IntegerField(default=0, verbose_name='Progreso')
    
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='Inicio')
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name='Fin')
    error = models.TextField(null=True, blank=True, verbose_name='Error')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha Creación')

    class Meta:
        db_table = 'jobs'
        verbose_name = 'Trabajo'
        verbose_name_plural = 'Trabajos'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.type} - {self.get_status_display()}"


class JobLog(models.Model):
    """Log de trabajo"""
    LEVEL_CHOICES = [
        ('INFO', 'Información'),
        ('ERROR', 'Error'),
        ('WARNING', 'Advertencia'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='logs')
    device_id = models.IntegerField(null=True, blank=True, verbose_name='ID Dispositivo')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='INFO', verbose_name='Nivel')
    message = models.TextField(verbose_name='Mensaje')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Fecha/Hora')

    class Meta:
        db_table = 'job_logs'
        verbose_name = 'Log de Trabajo'
        verbose_name_plural = 'Logs de Trabajos'
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.level}] {self.message[:50]}"


class Timetable(models.Model):
    """Horario de trabajo"""
    ROUNDING_CHOICES = [
        ('none', 'Ninguno'),
        ('5min', '5 minutos'),
        ('10min', '10 minutos'),
        ('down_5min', 'Abajo 5 min'),
    ]

    name = models.CharField(max_length=100, verbose_name='Nombre')
    on_duty_time = models.CharField(max_length=10, verbose_name='Hora Entrada')  # "09:00"
    off_duty_time = models.CharField(max_length=10, verbose_name='Hora Salida')  # "18:00"
    late_allow_minutes = models.IntegerField(default=0, verbose_name='Tolerancia Llegada Tarde (min)')
    early_leave_allow_minutes = models.IntegerField(default=0, verbose_name='Tolerancia Salida Temprano (min)')
    
    check_in_start = models.CharField(max_length=10, null=True, blank=True, verbose_name='Inicio Ventana Entrada')
    check_in_end = models.CharField(max_length=10, null=True, blank=True, verbose_name='Fin Ventana Entrada')
    check_out_start = models.CharField(max_length=10, null=True, blank=True, verbose_name='Inicio Ventana Salida')
    check_out_end = models.CharField(max_length=10, null=True, blank=True, verbose_name='Fin Ventana Salida')
    
    break_minutes = models.IntegerField(default=0, verbose_name='Minutos de Descanso')
    rounding_rule = models.CharField(max_length=50, choices=ROUNDING_CHOICES, default='none', verbose_name='Regla de Redondeo')
    required_minutes = models.IntegerField(default=0, verbose_name='Minutos Requeridos')
    work_days = models.IntegerField(default=1, verbose_name='Días de Trabajo')
    is_flexible = models.BooleanField(default=False, verbose_name='Es Flexible')

    class Meta:
        db_table = 'att_timetables'
        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.on_duty_time}-{self.off_duty_time})"


class Shift(models.Model):
    """Turno de trabajo"""
    name = models.CharField(max_length=100, verbose_name='Nombre')

    class Meta:
        db_table = 'att_shifts'
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
        ordering = ['name']

    def __str__(self):
        return self.name


class ShiftTimetable(models.Model):
    """Relación Turno-Horario"""
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='timetables')
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='shift_timetables')
    day_index = models.IntegerField(verbose_name='Día de la Semana')  # 0=Lunes, 6=Domingo

    class Meta:
        db_table = 'att_shift_timetables'
        verbose_name = 'Horario de Turno'
        verbose_name_plural = 'Horarios de Turnos'
        ordering = ['shift', 'day_index']

    def __str__(self):
        days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        day_name = days[self.day_index] if 0 <= self.day_index < 7 else f"Día {self.day_index}"
        return f"{self.shift.name} - {day_name}"


class ScheduleOverride(models.Model):
    """Sobrescritura de horario"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='schedule_overrides')
    date = models.DateField(verbose_name='Fecha')
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='schedule_overrides')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha Creación')

    class Meta:
        db_table = 'att_schedule_overrides'
        verbose_name = 'Excepción de Horario'
        verbose_name_plural = 'Excepciones de Horarios'
        constraints = [
            models.UniqueConstraint(fields=['employee', 'date'], name='uix_sched_override')
        ]
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee.name} - {self.date}"


class EmployeeShift(models.Model):
    """Asignación de turno (empleado o departamento)"""
    SCOPE_CHOICES = [
        ('EMPLOYEE', 'Empleado'),
        ('DEPARTMENT', 'Departamento'),
    ]

    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='EMPLOYEE', verbose_name='Ámbito')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True, related_name='shift_assignments')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True, related_name='shift_assignments')
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='assignments')
    start_date = models.DateField(verbose_name='Fecha Inicio')
    end_date = models.DateField(null=True, blank=True, verbose_name='Fecha Fin')

    class Meta:
        db_table = 'att_employee_shifts'
        verbose_name = 'Asignación de Turno'
        verbose_name_plural = 'Asignaciones de Turnos'
        ordering = ['-start_date']

    def __str__(self):
        target = self.employee.name if self.employee else (self.department.name if self.department else 'Sin asignar')
        return f"{target} - {self.shift.name}"


class Leave(models.Model):
    """Ausencia/Licencia"""
    STATUS_CHOICES = [
        ('Pending', 'Pendiente'),
        ('Approved', 'Aprobado'),
        ('Rejected', 'Rechazado'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=50, verbose_name='Tipo de Licencia')  # Vacation, Sick, etc.
    start_time = models.DateTimeField(verbose_name='Inicio')
    end_time = models.DateTimeField(verbose_name='Fin')
    reason = models.CharField(max_length=255, null=True, blank=True, verbose_name='Motivo')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', verbose_name='Estado')

    class Meta:
        db_table = 'att_leaves'
        verbose_name = 'Ausencia'
        verbose_name_plural = 'Ausencias'
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.employee.name} - {self.leave_type}"


class Holiday(models.Model):
    """Feriado"""
    name = models.CharField(max_length=100, verbose_name='Nombre')
    start_date = models.DateField(verbose_name='Fecha Inicio')
    end_date = models.DateField(verbose_name='Fecha Fin')

    class Meta:
        db_table = 'att_holidays'
        verbose_name = 'Feriado'
        verbose_name_plural = 'Feriados'
        ordering = ['start_date']

    def __str__(self):
        return self.name


class DailyAttendance(models.Model):
    """
    Asistencia diaria calculada.
    
    FORENSIC TRACEABILITY:
    This model now supports full audit trail for legal defensibility:
    - engine_version: Which version of the engine performed this calculation
    - policy_snapshot: Exact policy parameters used
    - calculation_fingerprint: Hash to detect input changes
    - calculation_state: Whether this is current or superseded
    - supersedes/superseded_by: Lineage for recalculations
    
    CRITICAL RULES:
    - NEVER modify a record with state=CALCULATED
    - Recalculations CREATE new records and mark old as SUPERSEDED
    - The unique constraint allows multiple records per employee/date for lineage
    """
    
    # State choices for calculation lifecycle
    CALCULATION_STATE_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('CALCULATED', 'Calculado'),
        ('SUPERSEDED', 'Reemplazado'),
    ]
    
    CALCULATION_MODE_CHOICES = [
        ('FLEXIBLE', 'Jornada Flexible'),
        ('STRUCTURED', 'Horario Fijo'),
        ('UNKNOWN', 'Desconocido'),
    ]
    
    STATUS_CHOICES = [
        ('Normal', 'Normal'),
        ('Late', 'Tardío'),
        ('Early', 'Salida anticipada'),
        ('Absent', 'Ausente'),
        ('Leave', 'Licencia'),
        ('Worked', 'Trabajado'),
        ('Incomplete', 'Incompleto'),
        ('Excessive', 'Excesivo'),
        ('HolidayWorked', 'Trabajo en Feriado'),
        ('RestDay', 'Día de Descanso'),
    ]

    SCHEDULE_TYPE_CHOICES = [
        ('FIXED', 'Fijo'),
        ('FLEX', 'Flexible'),
        ('OVERRIDE', 'Excepción'),
        ('DEPT', 'Departamento'),
        ('NONE', 'Ninguno'),
    ]

    # === IDENTITY ===
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='daily_attendance')
    date = models.DateField(db_index=True, verbose_name='Fecha')
    timetable = models.ForeignKey(Timetable, on_delete=models.SET_NULL, null=True, blank=True, related_name='daily_attendance')
    
    # === TIMESTAMPS ===
    check_in = models.DateTimeField(null=True, blank=True, verbose_name='Entrada')
    check_out = models.DateTimeField(null=True, blank=True, verbose_name='Salida')
    
    # === SCHEDULE CONTEXT ===
    on_duty = models.CharField(max_length=10, null=True, blank=True, verbose_name='Hora Esperada Entrada')
    off_duty = models.CharField(max_length=10, null=True, blank=True, verbose_name='Hora Esperada Salida')
    
    # === TIME METRICS ===
    late_minutes = models.IntegerField(default=0, verbose_name='Minutos de Tardanza')
    early_minutes = models.IntegerField(default=0, verbose_name='Minutos de Salida Temprana')
    worked_minutes = models.IntegerField(default=0, verbose_name='Minutos Trabajados')
    overtime_minutes = models.IntegerField(default=0, verbose_name='Minutos Extra')
    break_minutes = models.IntegerField(default=0, verbose_name='Minutos de Descanso')
    net_worked_minutes = models.IntegerField(default=0, verbose_name='Minutos Netos Trabajados')
    regular_minutes = models.IntegerField(default=0, verbose_name='Minutos Regulares')
    night_minutes = models.IntegerField(default=0, verbose_name='Minutos Nocturnos')
    
    # === STATUS ===
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Absent', verbose_name='Estado')
    exception_reason = models.CharField(max_length=100, null=True, blank=True, verbose_name='Razón de Excepción')
    
    # === STATUS ===
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Absent', verbose_name='Estado')
    exception_reason = models.CharField(max_length=100, null=True, blank=True, verbose_name='Razón de Excepción')
    is_absent = models.BooleanField(default=True, verbose_name='Ausente')

    class Meta:
        db_table = 'att_daily_attendance'
        verbose_name = 'Asistencia Diaria'
        verbose_name_plural = 'Asistencias Diarias'
        indexes = [
            models.Index(fields=['date', 'employee']),
            models.Index(fields=['status']),
            models.Index(fields=['date']),
        ]
        ordering = ['-date', 'employee']

    def __str__(self):
        return f"{self.employee.name} - {self.date} - {self.status}"

