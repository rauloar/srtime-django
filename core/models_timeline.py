"""
Timeline Visual Model
Represents a workday as visual time blocks for operational UX.

NO forensic, NO legal, NO monetary.
Pure operational representation.
"""
from django.db import models
from django.core.validators import MinValueValidator


class BlockType(models.TextChoices):
    """
    Types of timeline blocks.
    """
    WORK = 'WORK', 'Trabajo efectivo'
    GAP_PLANNED = 'GAP_PLANNED', 'Gap planificado (ej. almuerzo)'
    GAP_ANOMALY = 'GAP_ANOMALY', 'Gap anómalo (no esperado)'
    GAP_UNCLASSIFIED = 'GAP_UNCLASSIFIED', 'Gap no clasificado (hueco temporal)'
    SCHEDULE = 'SCHEDULE', 'Horario esperado'
    TOLERANCE = 'TOLERANCE', 'Ventana de tolerancia'
    OUTSIDE = 'OUTSIDE', 'Fuera de jornada'
    BREAK = 'BREAK', 'Descanso detectado'



class AttendanceTimelineBlock(models.Model):
    """
    Visual time block representing part of a workday.
    
    Purpose: Operational visualization of time attendance.
    NOT for legal evidence, NOT for payroll calculation.
    
    Each block represents a segment of time during the day:
    - WORK: Time between punches (actual work)
    - GAP_PLANNED: Expected gaps (lunch, breaks)
    - GAP_ANOMALY: Unexpected gaps in punches
    - SCHEDULE: Expected work schedule
    - TOLERANCE: Grace period for entry/exit
    - OUTSIDE: Time outside scheduled hours
    """
    
    # === IDENTITY ===
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='timeline_blocks',
        verbose_name='Empleado'
    )
    date = models.DateField(
        db_index=True,
        verbose_name='Fecha'
    )
    
    # === BLOCK TYPE ===
    block_type = models.CharField(
        max_length=30,
        choices=BlockType.choices,
        db_index=True,
        verbose_name='Tipo de bloque'
    )
    
    # === TIME RANGE ===
    start_time = models.TimeField(
        verbose_name='Hora inicio'
    )
    end_time = models.TimeField(
        verbose_name='Hora fin'
    )
    duration_minutes = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='Duración (minutos)'
    )
    
    # === CONTEXT ===
    related_rule = models.CharField(
        max_length=100,
        blank=True,
        help_text='Rule that generated this block (for explanation)'
    )
    anomaly_code = models.CharField(
        max_length=50,
        blank=True,
        help_text='Anomaly code if block represents an issue'
    )
    
    # === METADATA ===
    engine_version = models.CharField(
        max_length=10,
        default='V2',
        verbose_name='Versión del motor'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Creado'
    )
    
    class Meta:
        db_table = 'core_attendance_timeline_block'
        verbose_name = 'Bloque de Timeline'
        verbose_name_plural = 'Bloques de Timeline'
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date', 'block_type']),
        ]
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return (
            f"{self.employee.full_name} - {self.date} - "
            f"{self.block_type} ({self.start_time}-{self.end_time})"
        )
    
    @property
    def is_anomaly(self) -> bool:
        """Check if this block represents an anomaly."""
        return bool(self.anomaly_code) or self.block_type == BlockType.GAP_ANOMALY
    
    @property
    def is_work(self) -> bool:
        """Check if this block represents actual work time."""
        return self.block_type == BlockType.WORK
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            'type': self.block_type,
            'start': self.start_time.strftime('%H:%M'),
            'end': self.end_time.strftime('%H:%M'),
            'duration_minutes': self.duration_minutes,
            'related_rule': self.related_rule,
            'anomaly_code': self.anomaly_code,
            'is_anomaly': self.is_anomaly,
            'is_work': self.is_work,
        }
