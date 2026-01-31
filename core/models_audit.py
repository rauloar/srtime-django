"""
Forensic Traceability Models
Implements audit infrastructure for legally defensible attendance calculations.

These models are INFRASTRUCTURE, not features:
- PolicySnapshot: Immutable record of calculation parameters
- CalculationAuditLog: Event log for forensic analysis

CRITICAL RULES:
- PolicySnapshot records are NEVER modified after creation
- CalculationAuditLog records are NEVER deleted
- All changes create new records, not modifications
"""
from django.db import models
from django.contrib.auth import get_user_model
import hashlib
import json


User = get_user_model()


class CalculationState(models.TextChoices):
    """
    State of a daily attendance calculation.
    
    PENDING: Day exists but calculation not yet performed
    CALCULATED: Calculation completed, this is the current version
    SUPERSEDED: This record was replaced by a recalculation
    """
    PENDING = 'PENDING', 'Pendiente'
    CALCULATED = 'CALCULATED', 'Calculado'
    SUPERSEDED = 'SUPERSEDED', 'Reemplazado'


class CalculationMode(models.TextChoices):
    """
    Type of calculation engine used.
    """
    FLEXIBLE = 'FLEXIBLE', 'Jornada Flexible'
    STRUCTURED = 'STRUCTURED', 'Horario Fijo'
    UNKNOWN = 'UNKNOWN', 'Desconocido'


class AuditEventType(models.TextChoices):
    """
    Types of audit events for calculation log.
    """
    CREATED = 'CREATED', 'Creado'
    RECALCULATED = 'RECALCULATED', 'Recalculado'
    MANUALLY_ADJUSTED = 'MANUALLY_ADJUSTED', 'Ajuste Manual'
    POLICY_CHANGED = 'POLICY_CHANGED', 'Política Cambiada'
    PUNCH_CORRECTED = 'PUNCH_CORRECTED', 'Fichada Corregida'
    REVIEWED = 'REVIEWED', 'Revisado'
    APPROVED = 'APPROVED', 'Aprobado'


class PolicySnapshot(models.Model):
    """
    Immutable snapshot of calculation policy used for a specific calculation.
    
    PURPOSE:
    - Preserve exact parameters used at calculation time
    - Enable reproduction of historical calculations
    - Provide evidence for labor audits
    
    RULES:
    - NEVER update a PolicySnapshot after creation
    - Reuse existing snapshots with matching hash
    - Hash is computed from serialized JSON
    """
    # Identity
    policy_hash = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        verbose_name='Hash de Política',
        help_text='SHA256 del contenido JSON'
    )
    
    # Content
    policy_json = models.JSONField(
        verbose_name='Política (JSON)',
        help_text='FlexPolicy o StructuredPolicy serializada'
    )
    
    # Metadata
    policy_type = models.CharField(
        max_length=20,
        choices=[
            ('FLEX', 'Flexible'),
            ('STRUCTURED', 'Estructurada'),
        ],
        default='FLEX',
        verbose_name='Tipo de Política'
    )
    
    source = models.CharField(
        max_length=50,
        choices=[
            ('COMPANY_DEFAULT', 'Por defecto de empresa'),
            ('DEPARTMENT', 'Por departamento'),
            ('EMPLOYEE_OVERRIDE', 'Excepción de empleado'),
            ('TIMETABLE', 'Desde horario'),
            ('ADMIN', 'Configuración administrativa'),
        ],
        default='COMPANY_DEFAULT',
        verbose_name='Origen'
    )
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción',
        help_text='Descripción opcional de la política'
    )
    
    class Meta:
        db_table = 'att_policy_snapshot'
        verbose_name = 'Snapshot de Política'
        verbose_name_plural = 'Snapshots de Política'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Policy {self.policy_hash[:8]}... ({self.policy_type})"
    
    @classmethod
    def compute_hash(cls, policy_dict: dict) -> str:
        """
        Compute deterministic hash from policy dictionary.
        
        The JSON is sorted to ensure identical policies produce identical hashes.
        """
        # Sort keys for deterministic serialization
        json_str = json.dumps(policy_dict, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    @classmethod
    def get_or_create_from_policy(cls, policy_dict: dict, policy_type: str = 'FLEX', source: str = 'COMPANY_DEFAULT'):
        """
        Get existing snapshot or create new one if hash doesn't exist.
        
        This is the ONLY way snapshots should be created.
        """
        policy_hash = cls.compute_hash(policy_dict)
        
        snapshot, created = cls.objects.get_or_create(
            policy_hash=policy_hash,
            defaults={
                'policy_json': policy_dict,
                'policy_type': policy_type,
                'source': source,
            }
        )
        
        return snapshot, created
    
    def save(self, *args, **kwargs):
        """Ensure hash is computed before save."""
        if not self.policy_hash:
            self.policy_hash = self.compute_hash(self.policy_json)
        super().save(*args, **kwargs)


class CalculationAuditLog(models.Model):
    """
    Immutable log of calculation events for forensic analysis.
    
    PURPOSE:
    - Track all calculation-related events
    - Provide audit trail for inspections
    - Support investigation of discrepancies
    
    RULES:
    - NEVER update or delete records
    - Every significant event gets a log entry
    - Include all relevant metadata
    """
    # Reference to the attendance record
    daily_attendance = models.ForeignKey(
        'DailyAttendance',
        on_delete=models.PROTECT,  # Prevent deletion of audited records
        related_name='audit_logs',
        verbose_name='Asistencia Diaria'
    )
    
    # Event details
    event_type = models.CharField(
        max_length=30,
        choices=AuditEventType.choices,
        verbose_name='Tipo de Evento'
    )
    
    # Calculation context at time of event
    engine_version = models.CharField(
        max_length=50,
        verbose_name='Versión del Motor'
    )
    
    calculation_fingerprint = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name='Fingerprint del Cálculo'
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Metadatos',
        help_text='Información adicional del evento (valores anteriores, motivo, etc.)'
    )
    
    # Actor
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calculation_audit_logs',
        verbose_name='Usuario'
    )
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'att_calculation_audit_log'
        verbose_name = 'Log de Auditoría de Cálculo'
        verbose_name_plural = 'Logs de Auditoría de Cálculo'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['daily_attendance', 'event_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['event_type']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.daily_attendance_id} @ {self.created_at}"
