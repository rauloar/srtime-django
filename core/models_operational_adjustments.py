"""
Operational Adjustments Models
Allows human flexibility in attendance management.

NO manual result modification, only base data corrections.
All adjustments trigger automatic recalculation.
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class AttendanceAdjustment(models.Model):
    """
    Operational correction to attendance data.
    
    Purpose: Allow HR to correct input data with traceability.
    NOT legal audit, NOT forensic evidence - operational management only.
    
    All adjustments:
    - Modify base data (punches, schedules)
    - Trigger automatic recalculation
    - Maintain operational audit trail
    - Require justification
    """
    
    ADJUSTMENT_TYPES = [
        ('ADD_PUNCH', 'Agregar fichada'),
        ('REMOVE_PUNCH', 'Eliminar fichada errónea'),
        ('EDIT_PUNCH', 'Editar horario de fichada'),
        ('JUSTIFIED_ABSENCE', 'Ausencia justificada'),
        ('FLEX_OVERRIDE', 'Flexibilidad horaria'),
    ]
    
    # === IDENTITY ===
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='attendance_adjustments',
        verbose_name='Empleado'
    )
    date = models.DateField(
        db_index=True,
        verbose_name='Fecha'
    )
    
    # === ADJUSTMENT TYPE ===
    adjustment_type = models.CharField(
        max_length=20,
        choices=ADJUSTMENT_TYPES,
        verbose_name='Tipo de ajuste'
    )
    
    # === AFFECTED DATA ===
    original_time = models.TimeField(
        null=True,
        blank=True,
        help_text='Original time (for EDIT_PUNCH)',
        verbose_name='Hora original'
    )
    new_time = models.TimeField(
        null=True,
        blank=True,
        help_text='New time (for ADD_PUNCH, EDIT_PUNCH)',
        verbose_name='Hora nueva'
    )
    punch_type = models.CharField(
        max_length=10,
        blank=True,
        help_text='IN or OUT',
        verbose_name='Tipo de fichada'
    )
    
    # === JUSTIFICATION (Human, not legal) ===
    reason = models.TextField(
        help_text='Human-readable reason for adjustment',
        verbose_name='Motivo'
    )
    
    # === OPERATIONAL APPROVAL (not legal/forensic) ===
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='adjustments_requested',
        verbose_name='Solicitado por'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='adjustments_approved',
        verbose_name='Aprobado por'
    )
    
    # === STATUS ===
    approved = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='Aprobado'
    )
    applied = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Has this adjustment been applied to base data?',
        verbose_name='Aplicado'
    )
    
    # === METADATA ===
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Creado en'
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Aprobado en'
    )
    applied_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Aplicado en'
    )
    
    class Meta:
        db_table = 'core_attendance_adjustment'
        verbose_name = 'Ajuste de Asistencia'
        verbose_name_plural = 'Ajustes de Asistencia'
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['approved', 'applied']),
            models.Index(fields=['date']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        status = "✓" if self.applied else ("⏳" if self.approved else "📝")
        return (
            f"{status} {self.get_adjustment_type_display()} - "
            f"{self.employee.full_name} - {self.date}"
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'employee': {
                'id': self.employee.id,
                'name': self.employee.full_name,
            },
            'date': str(self.date),
            'adjustment_type': self.adjustment_type,
            'adjustment_type_display': self.get_adjustment_type_display(),
            'original_time': str(self.original_time) if self.original_time else None,
            'new_time': str(self.new_time) if self.new_time else None,
            'punch_type': self.punch_type,
            'reason': self.reason,
            'requested_by': self.requested_by.username if self.requested_by else None,
            'approved_by': self.approved_by.username if self.approved_by else None,
            'approved': self.approved,
            'applied': self.applied,
            'created_at': self.created_at.isoformat(),
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
        }


class FlexibleWorkRule(models.Model):
    """
    Defines flexible work expectations for an employee.
    
    Purpose: Define how much work is expected without rigid punch times.
    Engine calculates actual worked time, this defines expectations.
    """
    
    # === IDENTITY ===
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='flexible_rules',
        verbose_name='Empleado'
    )
    
    # === EXPECTATIONS ===
    weekly_expected_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(168)],
        help_text='Expected hours per week (e.g., 40.00)',
        verbose_name='Horas esperadas por semana'
    )
    daily_min_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(24)],
        help_text='Minimum hours per day (e.g., 4.00)',
        verbose_name='Horas mínimas por día'
    )
    daily_max_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=12.00,
        validators=[MinValueValidator(0), MaxValueValidator(24)],
        help_text='Maximum hours per day (e.g., 12.00)',
        verbose_name='Horas máximas por día'
    )
    
    # === WINDOW (Optional) ===
    core_start_time = models.TimeField(
        null=True,
        blank=True,
        help_text='Core hours start (optional)',
        verbose_name='Inicio horario núcleo'
    )
    core_end_time = models.TimeField(
        null=True,
        blank=True,
        help_text='Core hours end (optional)',
        verbose_name='Fin horario núcleo'
    )
    
    # === STATUS ===
    active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name='Activo'
    )
    
    # === METADATA ===
    effective_from = models.DateField(
        verbose_name='Efectivo desde'
    )
    effective_to = models.DateField(
        null=True,
        blank=True,
        verbose_name='Efectivo hasta'
    )
    
    class Meta:
        db_table = 'core_flexible_work_rule'
        verbose_name = 'Regla de Trabajo Flexible'
        verbose_name_plural = 'Reglas de Trabajo Flexible'
        indexes = [
            models.Index(fields=['employee', 'active']),
            models.Index(fields=['effective_from', 'effective_to']),
        ]
        ordering = ['-effective_from']
    
    def __str__(self):
        return (
            f"{self.employee.full_name} - {self.weekly_expected_hours}h/semana "
            f"({self.daily_min_hours}-{self.daily_max_hours}h/día)"
        )
    
    @property
    def daily_expected_hours(self) -> float:
        """Calculate daily expected hours (weekly / 5)."""
        return float(self.weekly_expected_hours) / 5
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'employee_id': self.employee.id,
            'weekly_expected_hours': float(self.weekly_expected_hours),
            'daily_min_hours': float(self.daily_min_hours),
            'daily_max_hours': float(self.daily_max_hours),
            'core_start_time': str(self.core_start_time) if self.core_start_time else None,
            'core_end_time': str(self.core_end_time) if self.core_end_time else None,
            'active': self.active,
            'effective_from': str(self.effective_from),
            'effective_to': str(self.effective_to) if self.effective_to else None,
        }
