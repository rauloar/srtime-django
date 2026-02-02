"""
Engine Snapshot Model
Technical snapshot of attendance engine inputs for reproducibility.

NO legal evidence, NO forensic features.
Only technical debugging and version comparison.
"""
from django.db import models
from django.core.validators import MinValueValidator


class AttendanceEngineSnapshot(models.Model):
    """
    Technical snapshot of inputs used by the attendance engine.
    
    Purpose: Technical reproducibility and debugging.
    NOT for legal evidence, NOT for forensic audit.
    
    Allows answering: "What exact inputs did the engine use on this date?"
    
    Use cases:
    - Compare before/after when engine rules change
    - Debug calculation differences
    - Reproduce calculations for testing
    - Understand what context was active at calculation time
    """
    
    # === IDENTITY ===
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='engine_snapshots',
        verbose_name='Empleado'
    )
    date = models.DateField(
        db_index=True,
        verbose_name='Fecha'
    )
    
    # === ENGINE VERSION ===
    engine_version = models.CharField(
        max_length=10,
        default='V2',
        verbose_name='Versión del motor'
    )
    
    # === INPUTS (Technical state at calculation time) ===
    punches = models.JSONField(
        help_text='Raw punches used in calculation',
        verbose_name='Fichadas'
    )
    schedule = models.JSONField(
        help_text='Schedule configuration at calculation time',
        verbose_name='Horario'
    )
    tolerances = models.JSONField(
        default=dict,
        help_text='Tolerance settings applied',
        verbose_name='Tolerancias'
    )
    
    # === CONTEXT FLAGS ===
    flexible_mode = models.BooleanField(
        default=False,
        help_text='Was flexible schedule mode active?',
        verbose_name='Modo flexible'
    )
    holiday = models.BooleanField(
        default=False,
        help_text='Was this day a holiday?',
        verbose_name='Feriado'
    )
    absence_type = models.CharField(
        max_length=50,
        blank=True,
        help_text='Absence type if applicable',
        verbose_name='Tipo de ausencia'
    )
    
    # === RESULT SUMMARY (for quick reference) ===
    status = models.CharField(
        max_length=50,
        help_text='Calculated attendance status',
        verbose_name='Estado'
    )
    worked_minutes = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text='Total worked minutes calculated',
        verbose_name='Minutos trabajados'
    )
    expected_minutes = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Expected work minutes',
        verbose_name='Minutos esperados'
    )
    overtime_minutes = models.IntegerField(
        default=0,
        help_text='Overtime minutes (can be negative for deficit)',
        verbose_name='Minutos extra'
    )
    deficit_minutes = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Deficit minutes',
        verbose_name='Minutos déficit'
    )
    
    # === METADATA ===
    calculated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Calculado en'
    )
    
    class Meta:
        db_table = 'core_attendance_engine_snapshot'
        verbose_name = 'Snapshot de Motor'
        verbose_name_plural = 'Snapshots de Motor'
        unique_together = [('employee', 'date', 'engine_version')]
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date', 'engine_version']),
            models.Index(fields=['status']),
        ]
        ordering = ['-date', '-calculated_at']
    
    def __str__(self):
        return (
            f"{self.employee.full_name} - {self.date} - "
            f"{self.engine_version} - {self.status}"
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            'date': str(self.date),
            'engine_version': self.engine_version,
            'inputs': {
                'punches': self.punches,
                'schedule': self.schedule,
                'tolerances': self.tolerances,
            },
            'context': {
                'flexible_mode': self.flexible_mode,
                'holiday': self.holiday,
                'absence_type': self.absence_type,
            },
            'result': {
                'status': self.status,
                'worked_minutes': self.worked_minutes,
                'expected_minutes': self.expected_minutes,
                'overtime_minutes': self.overtime_minutes,
                'deficit_minutes': self.deficit_minutes,
            },
            'calculated_at': self.calculated_at.isoformat(),
        }
    
    @property
    def is_reproducible(self) -> bool:
        """Check if snapshot has all data needed to reproduce calculation."""
        return bool(
            self.punches and
            self.schedule and
            self.status
        )
