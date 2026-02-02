"""
Shadow Calculation Model
For pre-migration validation: compares V1 (production) with V2 (shadow) calculations.

PURPOSE:
This model stores parallel calculations without affecting production data.
It allows analysis of differences between engine versions before migration.

RULES:
- Write-only: Records are NEVER updated after creation
- Read for analysis: Used to generate comparison reports
- No production impact: Failures here do NOT affect official calculations
"""
from django.db import models


class DifferenceType(models.TextChoices):
    """
    Classification of calculation differences between V1 and V2.
    
    Used for prioritizing review and migration readiness analysis.
    """
    NONE = 'NONE', 'Sin diferencia'           # 0 minutes
    MINOR = 'MINOR', 'Diferencia menor'       # 1-10 minutes
    MAJOR = 'MAJOR', 'Diferencia mayor'       # 11-60 minutes
    CRITICAL = 'CRITICAL', 'Diferencia crítica'  # >60 minutes


class ShadowCalculation(models.Model):
    """
    Shadow calculation record for V1 vs V2 comparison.
    
    Each record represents a single day calculated by BOTH engines,
    stored for analysis purposes only.
    
    This is VALIDATION INFRASTRUCTURE, not a production feature.
    """
    
    # === IDENTITY ===
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='shadow_calculations',
        verbose_name='Empleado'
    )
    date = models.DateField(
        db_index=True,
        verbose_name='Fecha'
    )
    
    # === V1 DATA (From Production) ===
    v1_worked_minutes = models.IntegerField(
        verbose_name='V1 Minutos Trabajados'
    )
    v1_overtime_minutes = models.IntegerField(
        default=0,
        verbose_name='V1 Minutos Extra'
    )
    v1_status = models.CharField(
        max_length=50,
        verbose_name='V1 Estado'
    )
    
    # === V2 DATA (Shadow Calculation) ===
    v2_worked_minutes = models.IntegerField(
        verbose_name='V2 Minutos Brutos'
    )
    v2_net_minutes = models.IntegerField(
        verbose_name='V2 Minutos Netos'
    )
    v2_regular_minutes = models.IntegerField(
        verbose_name='V2 Minutos Regulares'
    )
    v2_overtime_minutes = models.IntegerField(
        verbose_name='V2 Minutos Extra'
    )
    v2_night_minutes = models.IntegerField(
        default=0,
        verbose_name='V2 Minutos Nocturnos'
    )
    v2_status = models.CharField(
        max_length=50,
        verbose_name='V2 Estado'
    )
    
    # === COMPARISON METRICS ===
    difference_minutes = models.IntegerField(
        verbose_name='Diferencia (minutos)',
        help_text='V2 net - V1 worked'
    )
    difference_type = models.CharField(
        max_length=20,
        choices=DifferenceType.choices,
        default=DifferenceType.NONE,
        db_index=True,
        verbose_name='Tipo de Diferencia'
    )
    requires_review = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='Requiere Revisión'
    )
    
    # === V2 TRACEABILITY ===
    fingerprint_v2 = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name='Fingerprint V2'
    )
    engine_version = models.CharField(
        max_length=50,
        default='2.0.0',
        verbose_name='Versión Motor V2'
    )
    policy_snapshot = models.ForeignKey(
        'PolicySnapshot',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shadow_calculations',
        verbose_name='Snapshot de Política'
    )
    
    # === METADATA ===
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    v1_daily_attendance_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='ID DailyAttendance V1',
        help_text='Reference to the V1 record being compared'
    )
    
    class Meta:
        db_table = 'att_shadow_calculation'
        verbose_name = 'Cálculo Shadow'
        verbose_name_plural = 'Cálculos Shadow'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['difference_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['requires_review']),
        ]
    
    def __str__(self):
        diff_label = f"+{self.difference_minutes}" if self.difference_minutes > 0 else str(self.difference_minutes)
        return f"Shadow {self.employee_id} @ {self.date}: {diff_label}min ({self.difference_type})"
    
    @classmethod
    def classify_difference(cls, difference_minutes: int) -> DifferenceType:
        """
        Classify the difference between V1 and V2 calculations.
        
        Args:
            difference_minutes: Absolute difference in minutes
        
        Returns:
            DifferenceType enum value
        """
        abs_diff = abs(difference_minutes)
        
        if abs_diff == 0:
            return DifferenceType.NONE
        elif abs_diff <= 10:
            return DifferenceType.MINOR
        elif abs_diff <= 60:
            return DifferenceType.MAJOR
        else:
            return DifferenceType.CRITICAL


# =============================================================================
# DIFFERENCE ANALYSIS ENUMS
# =============================================================================

class DifferenceReason(models.TextChoices):
    """
    Causal classification for why V2 differs from V1.
    
    Used by the Difference Reasoning Engine to explain differences
    in a way that is legally defensible and understandable by RRHH.
    
    ORDER MATTERS: Rules are evaluated in enum order for priority.
    """
    BREAK_POLICY_CHANGE = 'BREAK_POLICY', 'Cambio en política de descansos'
    OVERTIME_POLICY_CHANGE = 'OVERTIME_POLICY', 'Cambio en política de horas extra'
    FLEXIBLE_SPLIT_LOGIC = 'FLEXIBLE_SPLIT', 'Tratamiento de jornada fragmentada'
    NIGHT_CLASSIFICATION_CHANGE = 'NIGHT_CLASS', 'Cambio en clasificación nocturna'
    HOLIDAY_DETECTION_CHANGE = 'HOLIDAY_DETECT', 'Detección de trabajo en feriado'
    ORPHAN_PUNCH_HANDLING = 'ORPHAN_PUNCH', 'Manejo de fichadas huérfanas'
    ROUNDING_RULE_DIFFERENCE = 'ROUNDING', 'Diferencia por regla de redondeo'
    STATUS_RESOLUTION_CHANGE = 'STATUS_CHANGE', 'Cambio en resolución de estado'
    ENGINE_BUG_V1 = 'BUG_V1', 'Posible error en motor V1'
    UNKNOWN = 'UNKNOWN', 'Causa no determinada'


class ConfidenceLevel(models.TextChoices):
    """
    Confidence level of the causal classification.
    
    HIGH: Clear structural rule matched
    MEDIUM: Multiple signals, some ambiguity
    LOW: Fallback or unclear cause
    """
    HIGH = 'HIGH', 'Alta confianza'
    MEDIUM = 'MEDIUM', 'Confianza media'
    LOW = 'LOW', 'Baja confianza'


# =============================================================================
# SHADOW DIFFERENCE ANALYSIS MODEL
# =============================================================================

class ShadowDifferenceAnalysis(models.Model):
    """
    Causal analysis of a shadow calculation difference.
    
    This model stores the EXPLANATION of why V2 differs from V1,
    not just the numeric difference. It is the output of the
    Difference Reasoning Engine.
    
    PURPOSE:
    - Provide legally defensible explanations
    - Enable RRHH to understand engine behavior
    - Support migration decision-making
    
    RULES:
    - One analysis per shadow calculation
    - Write-once (immutable after creation)
    - Read for reporting and review workflow
    """
    
    # === LINK TO RAW COMPARISON ===
    shadow_calculation = models.OneToOneField(
        ShadowCalculation,
        on_delete=models.CASCADE,
        related_name='analysis',
        verbose_name='Cálculo Shadow'
    )
    
    # === CAUSAL CLASSIFICATION ===
    primary_reason = models.CharField(
        max_length=30,
        choices=DifferenceReason.choices,
        verbose_name='Causa Principal',
        help_text='Razón principal de la diferencia'
    )
    secondary_reason = models.CharField(
        max_length=30,
        choices=DifferenceReason.choices,
        blank=True,
        null=True,
        verbose_name='Causa Secundaria',
        help_text='Razón adicional que contribuye a la diferencia'
    )
    confidence_level = models.CharField(
        max_length=10,
        choices=ConfidenceLevel.choices,
        default=ConfidenceLevel.MEDIUM,
        verbose_name='Nivel de Confianza'
    )
    
    # === HUMAN-READABLE EXPLANATION ===
    explanation = models.TextField(
        verbose_name='Explicación',
        help_text='Texto legible por RRHH explicando la diferencia'
    )
    
    # === REVIEW FLAGS ===
    requires_human_review = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='Requiere Revisión Humana'
    )
    
    # === DETAILED BREAKDOWN ===
    affected_fields = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Campos Afectados',
        help_text='Qué campos específicos difieren (break, overtime, etc.)'
    )
    rule_trace = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Traza de Reglas',
        help_text='Reglas evaluadas y sus resultados'
    )
    
    # === METADATA ===
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Análisis'
    )
    engine_version = models.CharField(
        max_length=20,
        default='1.0.0',
        verbose_name='Versión del Analizador'
    )
    
    class Meta:
        db_table = 'att_shadow_difference_analysis'
        verbose_name = 'Análisis de Diferencia Shadow'
        verbose_name_plural = 'Análisis de Diferencias Shadow'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['primary_reason']),
            models.Index(fields=['confidence_level']),
            models.Index(fields=['requires_human_review']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Analysis {self.shadow_calculation_id}: {self.primary_reason} ({self.confidence_level})"
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if this analysis has high confidence."""
        return self.confidence_level == ConfidenceLevel.HIGH
    
    @property
    def needs_attention(self) -> bool:
        """Check if this analysis needs human attention."""
        return (
            self.requires_human_review or 
            self.confidence_level == ConfidenceLevel.LOW or
            self.primary_reason == DifferenceReason.UNKNOWN
        )


# =============================================================================
# REVIEW WORKFLOW ENUMS
# =============================================================================

class ReviewStatus(models.TextChoices):
    """
    Status of the human review workflow.
    
    State machine transitions:
        PENDING → IN_PROGRESS
        IN_PROGRESS → ACCEPTED | ADJUSTED | ESCALATED
        ACCEPTED | ADJUSTED | ESCALATED → CLOSED
        CLOSED → (terminal, no transitions)
    """
    PENDING = 'PENDING', 'Pendiente de revisión'
    IN_PROGRESS = 'IN_PROGRESS', 'En revisión'
    ACCEPTED = 'ACCEPTED', 'Aceptado'
    ADJUSTED = 'ADJUSTED', 'Requiere ajuste de política'
    ESCALATED = 'ESCALATED', 'Escalado a Legal'
    CLOSED = 'CLOSED', 'Cerrado'


class ReviewDecision(models.TextChoices):
    """
    Final decision on a shadow difference.
    
    Indicates whether V2 is correct, V1 is correct, or policy needs change.
    """
    V2_CORRECT = 'V2_CORRECT', 'V2 es correcto'
    V1_CORRECT = 'V1_CORRECT', 'V1 es correcto'
    POLICY_CHANGE_NEEDED = 'POLICY_CHANGE', 'Requiere cambio de política'
    INCONCLUSIVE = 'INCONCLUSIVE', 'Resultado inconcluso'
    NOT_APPLICABLE = 'N/A', 'No aplica'


# =============================================================================
# SHADOW REVIEW DECISION MODEL
# =============================================================================

class ShadowReviewDecision(models.Model):
    """
    Human review decision on a shadow difference analysis.
    
    This model represents the chain of custody for decisions made
    by RRHH/Legal on calculation differences. Each decision is
    legally binding and auditable.
    
    RULES:
    - Immutable after CLOSED status
    - All transitions are audited
    - Only assigned reviewer can submit decision
    - No silent edits allowed
    """
    
    # === LINK TO ANALYSIS ===
    analysis = models.OneToOneField(
        ShadowDifferenceAnalysis,
        on_delete=models.CASCADE,
        related_name='review_decision',
        verbose_name='Análisis'
    )
    
    # === WORKFLOW STATE ===
    status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
        db_index=True,
        verbose_name='Estado'
    )
    
    # === REVIEW ASSIGNMENT ===
    reviewer = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shadow_reviews',
        verbose_name='Revisor Asignado'
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Inicio de Revisión'
    )
    
    # === DECISION DATA ===
    decision = models.CharField(
        max_length=20,
        choices=ReviewDecision.choices,
        blank=True,
        null=True,
        verbose_name='Decisión'
    )
    decision_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas de Decisión',
        help_text='Justificación obligatoria de la decisión'
    )
    decided_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Decisión'
    )
    
    # === OPTIONAL OVERRIDES ===
    confidence_override = models.CharField(
        max_length=10,
        choices=ConfidenceLevel.choices,
        blank=True,
        null=True,
        verbose_name='Override de Confianza',
        help_text='Si el revisor considera que la confianza debe ser diferente'
    )
    
    # === CLOSURE ===
    closed_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shadow_reviews_closed',
        verbose_name='Cerrado por'
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Cierre'
    )
    
    # === METADATA ===
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    class Meta:
        db_table = 'att_shadow_review_decision'
        verbose_name = 'Decisión de Revisión Shadow'
        verbose_name_plural = 'Decisiones de Revisión Shadow'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['reviewer']),
            models.Index(fields=['decided_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Review {self.analysis_id}: {self.status}"
    
    @property
    def is_terminal(self) -> bool:
        """Check if review is in a terminal state."""
        return self.status == ReviewStatus.CLOSED
    
    @property
    def is_decided(self) -> bool:
        """Check if a decision has been made."""
        return self.status in [
            ReviewStatus.ACCEPTED,
            ReviewStatus.ADJUSTED,
            ReviewStatus.ESCALATED,
        ]
    
    @property
    def can_be_closed(self) -> bool:
        """Check if this review can be closed."""
        return self.is_decided and not self.is_terminal
