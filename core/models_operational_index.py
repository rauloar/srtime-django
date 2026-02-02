"""
Operational Index Model
Fast index for operational attendance review and management.

NO calculation logic, NO result modification.
Only indexing for human review and base data correction.
"""
from django.db import models
from django.core.validators import MinValueValidator


class AttendanceDayIndex(models.Model):
    """
    Fast operational index for attendance review.
    
    Purpose: Enable HR to quickly find days requiring attention.
    Generated after calculation completion.
    
    NOT for modifying results - only for finding issues to fix in base data.
    """
    
    # === IDENTITY ===
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='day_index',
        verbose_name='Empleado'
    )
    date = models.DateField(
        db_index=True,
        verbose_name='Fecha'
    )
    
    # === RESULT SUMMARY (for fast filtering) ===
    status = models.CharField(
        max_length=50,
        db_index=True,
        help_text='Calculated attendance status',
        verbose_name='Estado'
    )
    worked_minutes = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='Minutos trabajados'
    )
    expected_minutes = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Minutos esperados'
    )
    
    # === OPERATIONAL FLAGS (for fast queries) ===
    has_anomalies = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Day has detected anomalies',
        verbose_name='Tiene anomalías'
    )
    anomaly_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Number of anomalies detected',
        verbose_name='Cantidad de anomalías'
    )
    has_gaps = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Day has anomalous gaps in timeline',
        verbose_name='Tiene gaps'
    )
    has_unclassified_time = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Day has unclassified time blocks',
        verbose_name='Tiene tiempo no clasificado'
    )
    
    # === ATTENTION FLAG ===
    requires_attention = models.BooleanField(
        default=False,
        db_index=True,
        help_text='HR should review this day',
        verbose_name='Requiere atención'
    )
    
    # === METADATA ===
    indexed_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Indexado en'
    )
    
    class Meta:
        db_table = 'core_attendance_day_index'
        verbose_name = 'Índice Diario'
        verbose_name_plural = 'Índices Diarios'
        unique_together = [('employee', 'date')]
        indexes = [
            models.Index(fields=['date', 'requires_attention']),
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['status']),
            models.Index(fields=['requires_attention', 'date']),
        ]
        ordering = ['-date']
    
    def __str__(self):
        attention = "⚠️ " if self.requires_attention else ""
        return f"{attention}{self.employee.full_name} - {self.date} - {self.status}"
    
    @property
    def minutes_difference(self) -> int:
        """Calculate difference between worked and expected."""
        return self.worked_minutes - self.expected_minutes
    
    @property
    def is_deficit(self) -> bool:
        """Check if day has time deficit."""
        return self.minutes_difference < 0
    
    @property
    def is_overtime(self) -> bool:
        """Check if day has overtime."""
        return self.minutes_difference > 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            'date': str(self.date),
            'employee': {
                'id': self.employee.id,
                'name': self.employee.full_name,
            },
            'status': self.status,
            'worked_minutes': self.worked_minutes,
            'expected_minutes': self.expected_minutes,
            'minutes_difference': self.minutes_difference,
            'flags': {
                'has_anomalies': self.has_anomalies,
                'anomaly_count': self.anomaly_count,
                'has_gaps': self.has_gaps,
                'has_unclassified_time': self.has_unclassified_time,
                'requires_attention': self.requires_attention,
            },
        }
