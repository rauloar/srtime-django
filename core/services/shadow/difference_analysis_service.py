"""
Difference Analysis Service
Central service for the Shadow Monitoring System.

PURPOSE:
This service analyzes shadow calculation differences and produces
causal explanations that are legally defensible and understandable by RRHH.

ARCHITECTURE:
    ShadowCalculation (raw V1 vs V2)
           │
           ▼
    DifferenceAnalysisService.analyze()
           │
           ▼
    ShadowDifferenceAnalysis (causal explanation)

DESIGN PRINCIPLES:
1. DETERMINISTIC: Same input → same output, always
2. RULE-BASED: Clear, ordered rules with priority
3. TRACEABLE: Every decision is logged in rule_trace
4. PURE ANALYSIS: No side effects on production data
5. LEGALLY DEFENSIBLE: Explanations suitable for audit

RULE EVALUATION ORDER:
Rules are evaluated in strict order. First matching rule wins.
This eliminates ambiguity and ensures reproducible results.
"""
import logging
from dataclasses import dataclass
from typing import Optional, List, Tuple

from core.models_shadow import (
    ShadowCalculation,
    ShadowDifferenceAnalysis,
    DifferenceReason,
    ConfidenceLevel,
    DifferenceType,
)


logger = logging.getLogger(__name__)


# =============================================================================
# ANALYSIS RESULT (Internal)
# =============================================================================

@dataclass
class RuleResult:
    """Result of evaluating a single rule."""
    rule_name: str
    matched: bool
    reason: Optional[DifferenceReason] = None
    confidence: Optional[ConfidenceLevel] = None
    explanation: Optional[str] = None
    affected_fields: Optional[List[str]] = None


@dataclass
class AnalysisResult:
    """Result of the complete analysis."""
    primary_reason: DifferenceReason
    secondary_reason: Optional[DifferenceReason]
    confidence_level: ConfidenceLevel
    explanation: str
    requires_human_review: bool
    affected_fields: dict
    rule_trace: List[dict]


# =============================================================================
# DIFFERENCE REASONING ENGINE
# =============================================================================

class DifferenceReasoningEngine:
    """
    Rule-based engine for classifying differences between V1 and V2.
    
    RULE ORDER (strict priority):
    1. ENGINE_BUG_V1 - V1 produced impossible results
    2. BREAK_POLICY_CHANGE - Break deduction changed
    3. OVERTIME_POLICY_CHANGE - Overtime calculation changed
    4. NIGHT_CLASSIFICATION_CHANGE - Night minutes changed
    5. FLEXIBLE_SPLIT_LOGIC - Fragmented shift handling
    6. HOLIDAY_DETECTION_CHANGE - Holiday work detection
    7. ORPHAN_PUNCH_HANDLING - Orphan punch treatment
    8. STATUS_RESOLUTION_CHANGE - Status changed (Absent↔Worked)
    9. ROUNDING_RULE_DIFFERENCE - Small rounding differences
    10. UNKNOWN - Fallback
    """
    
    # Thresholds
    BREAK_DIFF_THRESHOLD = 5  # minutes
    OVERTIME_DIFF_THRESHOLD = 5  # minutes
    NIGHT_DIFF_THRESHOLD = 5  # minutes
    ROUNDING_MAX_DIFF = 10  # minutes
    
    def analyze(self, shadow: ShadowCalculation) -> AnalysisResult:
        """
        Analyze a shadow calculation and produce a causal classification.
        
        Args:
            shadow: The ShadowCalculation to analyze
        
        Returns:
            AnalysisResult with classification and explanation
        """
        rule_trace = []
        matched_reasons = []
        
        # Evaluate rules in strict order
        rules = [
            self._check_engine_bug_v1,
            self._check_break_policy,
            self._check_overtime_policy,
            self._check_night_classification,
            self._check_flexible_split,
            self._check_holiday_detection,
            self._check_orphan_punch,
            self._check_status_change,
            self._check_rounding,
        ]
        
        for rule_fn in rules:
            result = rule_fn(shadow)
            rule_trace.append({
                'rule': result.rule_name,
                'matched': result.matched,
                'reason': result.reason.value if result.reason else None,
            })
            
            if result.matched:
                matched_reasons.append(result)
        
        # Determine primary and secondary reasons
        if matched_reasons:
            primary = matched_reasons[0]
            secondary = matched_reasons[1] if len(matched_reasons) > 1 else None
        else:
            # Fallback to UNKNOWN
            primary = RuleResult(
                rule_name='UNKNOWN_FALLBACK',
                matched=True,
                reason=DifferenceReason.UNKNOWN,
                confidence=ConfidenceLevel.LOW,
                explanation=self._generate_unknown_explanation(shadow),
                affected_fields=['unknown'],
            )
            secondary = None
        
        # Build affected fields dict
        affected_fields = {}
        for r in matched_reasons:
            if r.affected_fields:
                for field in r.affected_fields:
                    affected_fields[field] = True
        
        # Determine if human review is needed
        requires_review = self._requires_human_review(
            shadow, primary.reason, primary.confidence
        )
        
        return AnalysisResult(
            primary_reason=primary.reason,
            secondary_reason=secondary.reason if secondary else None,
            confidence_level=primary.confidence,
            explanation=primary.explanation,
            requires_human_review=requires_review,
            affected_fields=affected_fields,
            rule_trace=rule_trace,
        )
    
    # =========================================================================
    # INDIVIDUAL RULES
    # =========================================================================
    
    def _check_engine_bug_v1(self, shadow: ShadowCalculation) -> RuleResult:
        """
        Rule 1: Check if V1 produced impossible results.
        
        Triggers:
        - Overtime > worked minutes
        - Negative values
        - Inconsistent state
        """
        v1_worked = shadow.v1_worked_minutes
        v1_overtime = shadow.v1_overtime_minutes
        
        is_bug = False
        bug_reason = ""
        
        # Check impossible overtime
        if v1_overtime > v1_worked and v1_worked > 0:
            is_bug = True
            bug_reason = f"V1 reportó {v1_overtime} min extra sobre {v1_worked} min trabajados"
        
        # Check negative values
        if v1_worked < 0 or v1_overtime < 0:
            is_bug = True
            bug_reason = "V1 reportó valores negativos"
        
        if is_bug:
            return RuleResult(
                rule_name='ENGINE_BUG_V1',
                matched=True,
                reason=DifferenceReason.ENGINE_BUG_V1,
                confidence=ConfidenceLevel.HIGH,
                explanation=f"El motor V1 produjo un resultado inválido: {bug_reason}. "
                           f"V2 corrige este comportamiento.",
                affected_fields=['worked_minutes', 'overtime_minutes'],
            )
        
        return RuleResult(rule_name='ENGINE_BUG_V1', matched=False)
    
    def _check_break_policy(self, shadow: ShadowCalculation) -> RuleResult:
        """
        Rule 2: Check if break deduction changed.
        
        Triggers:
        - V2 net < V2 worked (break was deducted)
        - V1 worked ≈ V2 worked but V1 > V2 net
        """
        v1_worked = shadow.v1_worked_minutes
        v2_worked = shadow.v2_worked_minutes
        v2_net = shadow.v2_net_minutes
        
        # V2 deducted breaks
        v2_break = v2_worked - v2_net
        
        # Check if break is the primary difference
        if v2_break > 0:
            # V1 didn't deduct breaks (or deducted less)
            diff_explained_by_break = abs(v1_worked - v2_net)
            if diff_explained_by_break <= self.BREAK_DIFF_THRESHOLD:
                return RuleResult(
                    rule_name='BREAK_POLICY_CHANGE',
                    matched=True,
                    reason=DifferenceReason.BREAK_POLICY_CHANGE,
                    confidence=ConfidenceLevel.HIGH,
                    explanation=f"V2 aplicó política de descansos automáticos ({v2_break} min), "
                               f"mientras que V1 no realizaba esta deducción. "
                               f"Esto resulta en {v2_break} minutos menos de tiempo computable.",
                    affected_fields=['break_minutes', 'net_worked_minutes'],
                )
        
        return RuleResult(rule_name='BREAK_POLICY_CHANGE', matched=False)
    
    def _check_overtime_policy(self, shadow: ShadowCalculation) -> RuleResult:
        """
        Rule 3: Check if overtime calculation changed.
        
        Triggers:
        - Overtime difference > threshold
        - Net worked similar
        """
        v1_overtime = shadow.v1_overtime_minutes
        v2_overtime = shadow.v2_overtime_minutes
        overtime_diff = abs(v2_overtime - v1_overtime)
        
        if overtime_diff > self.OVERTIME_DIFF_THRESHOLD:
            direction = "más" if v2_overtime > v1_overtime else "menos"
            return RuleResult(
                rule_name='OVERTIME_POLICY_CHANGE',
                matched=True,
                reason=DifferenceReason.OVERTIME_POLICY_CHANGE,
                confidence=ConfidenceLevel.HIGH,
                explanation=f"V2 calculó {overtime_diff} minutos {direction} de horas extra "
                           f"que V1. V1: {v1_overtime} min, V2: {v2_overtime} min. "
                           f"Esto se debe a diferencias en el umbral de jornada regular.",
                affected_fields=['overtime_minutes'],
            )
        
        return RuleResult(rule_name='OVERTIME_POLICY_CHANGE', matched=False)
    
    def _check_night_classification(self, shadow: ShadowCalculation) -> RuleResult:
        """
        Rule 4: Check if night classification changed.
        
        Triggers:
        - V2 has night minutes
        """
        v2_night = shadow.v2_night_minutes
        
        if v2_night > self.NIGHT_DIFF_THRESHOLD:
            return RuleResult(
                rule_name='NIGHT_CLASSIFICATION_CHANGE',
                matched=True,
                reason=DifferenceReason.NIGHT_CLASSIFICATION_CHANGE,
                confidence=ConfidenceLevel.HIGH,
                explanation=f"V2 detectó {v2_night} minutos de trabajo nocturno "
                           f"(entre 22:00 y 06:00). V1 no diferenciaba horario diurno/nocturno.",
                affected_fields=['night_minutes'],
            )
        
        return RuleResult(rule_name='NIGHT_CLASSIFICATION_CHANGE', matched=False)
    
    def _check_flexible_split(self, shadow: ShadowCalculation) -> RuleResult:
        """
        Rule 5: Check if flexible split logic caused difference.
        
        Triggers:
        - Significant worked time difference
        - Status is worked in both
        """
        v1_worked = shadow.v1_worked_minutes
        v2_worked = shadow.v2_worked_minutes
        worked_diff = abs(v2_worked - v1_worked)
        
        # If there's a significant difference in raw worked time
        # and both show work, it's likely split logic
        v1_worked_status = shadow.v1_status.lower() in ['worked', 'present', 'normal']
        v2_worked_status = shadow.v2_status.lower() in ['worked', 'present', 'normal']
        
        if worked_diff > 30 and v1_worked_status and v2_worked_status:
            return RuleResult(
                rule_name='FLEXIBLE_SPLIT_LOGIC',
                matched=True,
                reason=DifferenceReason.FLEXIBLE_SPLIT_LOGIC,
                confidence=ConfidenceLevel.MEDIUM,
                explanation=f"V2 detectó una diferencia de {worked_diff} minutos en el tiempo bruto. "
                           f"Esto puede deberse a cómo se tratan múltiples bloques de trabajo "
                           f"(jornada fragmentada). V1: {v1_worked} min, V2: {v2_worked} min.",
                affected_fields=['worked_minutes', 'work_blocks'],
            )
        
        return RuleResult(rule_name='FLEXIBLE_SPLIT_LOGIC', matched=False)
    
    def _check_holiday_detection(self, shadow: ShadowCalculation) -> RuleResult:
        """
        Rule 6: Check if holiday detection changed.
        
        Triggers:
        - V2 status contains 'holiday'
        - V1 status doesn't
        """
        v1_status = shadow.v1_status.lower()
        v2_status = shadow.v2_status.lower()
        
        v2_holiday = 'holiday' in v2_status or 'feriado' in v2_status
        v1_holiday = 'holiday' in v1_status or 'feriado' in v1_status
        
        if v2_holiday and not v1_holiday:
            return RuleResult(
                rule_name='HOLIDAY_DETECTION_CHANGE',
                matched=True,
                reason=DifferenceReason.HOLIDAY_DETECTION_CHANGE,
                confidence=ConfidenceLevel.HIGH,
                explanation=f"V2 detectó que este día es feriado y el empleado trabajó. "
                           f"V1 no clasificaba este día como feriado. "
                           f"Esto puede afectar el cálculo de recargos.",
                affected_fields=['status', 'holiday_flag'],
            )
        
        return RuleResult(rule_name='HOLIDAY_DETECTION_CHANGE', matched=False)
    
    def _check_orphan_punch(self, shadow: ShadowCalculation) -> RuleResult:
        """
        Rule 7: Check if orphan punch handling differs.
        
        Triggers:
        - V2 status indicates incomplete/orphan
        - V1 status doesn't
        """
        v2_status = shadow.v2_status.lower()
        
        orphan_indicators = ['incomplete', 'orphan', 'missing', 'incompleto']
        has_orphan = any(ind in v2_status for ind in orphan_indicators)
        
        if has_orphan:
            return RuleResult(
                rule_name='ORPHAN_PUNCH_HANDLING',
                matched=True,
                reason=DifferenceReason.ORPHAN_PUNCH_HANDLING,
                confidence=ConfidenceLevel.MEDIUM,
                explanation=f"V2 detectó fichadas sin par (entrada sin salida o viceversa). "
                           f"El tratamiento de estas fichadas huérfanas difiere entre motores.",
                affected_fields=['status', 'orphan_punches'],
            )
        
        return RuleResult(rule_name='ORPHAN_PUNCH_HANDLING', matched=False)
    
    def _check_status_change(self, shadow: ShadowCalculation) -> RuleResult:
        """
        Rule 8: Check if status resolution changed fundamentally.
        
        Triggers:
        - V1 Absent ↔ V2 Worked
        - V1 Leave ↔ V2 Worked
        """
        v1_status = shadow.v1_status.lower()
        v2_status = shadow.v2_status.lower()
        
        # Define status categories
        absent_indicators = ['absent', 'ausente', 'no show']
        worked_indicators = ['worked', 'present', 'normal', 'presente']
        leave_indicators = ['leave', 'licencia', 'permiso', 'vacation']
        
        v1_absent = any(ind in v1_status for ind in absent_indicators)
        v1_worked = any(ind in v1_status for ind in worked_indicators)
        v1_leave = any(ind in v1_status for ind in leave_indicators)
        
        v2_absent = any(ind in v2_status for ind in absent_indicators)
        v2_worked = any(ind in v2_status for ind in worked_indicators)
        v2_leave = any(ind in v2_status for ind in leave_indicators)
        
        # Absent ↔ Worked transition
        if (v1_absent and v2_worked) or (v1_worked and v2_absent):
            change_desc = "Ausente→Trabajado" if v1_absent else "Trabajado→Ausente"
            return RuleResult(
                rule_name='STATUS_RESOLUTION_CHANGE',
                matched=True,
                reason=DifferenceReason.STATUS_RESOLUTION_CHANGE,
                confidence=ConfidenceLevel.HIGH,
                explanation=f"El estado del día cambió de forma fundamental: {change_desc}. "
                           f"V1: {shadow.v1_status}, V2: {shadow.v2_status}. "
                           f"Esto requiere revisión para determinar el estado correcto.",
                affected_fields=['status'],
            )
        
        # Leave ↔ Worked transition
        if (v1_leave and v2_worked) or (v1_worked and v2_leave):
            change_desc = "Licencia→Trabajado" if v1_leave else "Trabajado→Licencia"
            return RuleResult(
                rule_name='STATUS_RESOLUTION_CHANGE',
                matched=True,
                reason=DifferenceReason.STATUS_RESOLUTION_CHANGE,
                confidence=ConfidenceLevel.HIGH,
                explanation=f"El estado del día cambió de forma fundamental: {change_desc}. "
                           f"V1: {shadow.v1_status}, V2: {shadow.v2_status}.",
                affected_fields=['status'],
            )
        
        return RuleResult(rule_name='STATUS_RESOLUTION_CHANGE', matched=False)
    
    def _check_rounding(self, shadow: ShadowCalculation) -> RuleResult:
        """
        Rule 9: Check if difference is due to rounding.
        
        Triggers:
        - Small difference (≤10 min)
        - No structural change detected
        """
        abs_diff = abs(shadow.difference_minutes)
        
        if 0 < abs_diff <= self.ROUNDING_MAX_DIFF:
            return RuleResult(
                rule_name='ROUNDING_RULE_DIFFERENCE',
                matched=True,
                reason=DifferenceReason.ROUNDING_RULE_DIFFERENCE,
                confidence=ConfidenceLevel.MEDIUM,
                explanation=f"La diferencia de {abs_diff} minutos probablemente se debe a "
                           f"reglas de redondeo diferentes entre V1 y V2. "
                           f"Esta diferencia es menor y no afecta significativamente el cálculo.",
                affected_fields=['rounding'],
            )
        
        return RuleResult(rule_name='ROUNDING_RULE_DIFFERENCE', matched=False)
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _generate_unknown_explanation(self, shadow: ShadowCalculation) -> str:
        """Generate explanation for unknown cases."""
        return (
            f"No se pudo determinar la causa exacta de la diferencia de "
            f"{shadow.difference_minutes} minutos. "
            f"V1: {shadow.v1_worked_minutes} min trabajados, estado '{shadow.v1_status}'. "
            f"V2: {shadow.v2_net_minutes} min netos, estado '{shadow.v2_status}'. "
            f"Se requiere revisión manual para este caso."
        )
    
    def _requires_human_review(
        self,
        shadow: ShadowCalculation,
        reason: DifferenceReason,
        confidence: ConfidenceLevel,
    ) -> bool:
        """Determine if human review is required."""
        # Always review MAJOR and CRITICAL differences
        if shadow.difference_type in [DifferenceType.MAJOR, DifferenceType.CRITICAL]:
            return True
        
        # Always review UNKNOWN cases
        if reason == DifferenceReason.UNKNOWN:
            return True
        
        # Always review LOW confidence
        if confidence == ConfidenceLevel.LOW:
            return True
        
        # Review status changes
        if reason == DifferenceReason.STATUS_RESOLUTION_CHANGE:
            return True
        
        return False


# =============================================================================
# MAIN SERVICE
# =============================================================================

class DifferenceAnalysisService:
    """
    Main service for analyzing shadow calculation differences.
    
    USAGE:
        service = DifferenceAnalysisService()
        analysis = service.analyze(shadow_calculation)
    
    GUARANTEES:
    - Deterministic: Same input → same output
    - Pure analysis: No side effects on production
    - Traceable: Every decision is logged
    """
    
    ANALYZER_VERSION = "1.0.0"
    
    def __init__(self):
        """Initialize with the reasoning engine."""
        self._engine = DifferenceReasoningEngine()
    
    def analyze(self, shadow: ShadowCalculation) -> ShadowDifferenceAnalysis:
        """
        Analyze a shadow calculation and create a ShadowDifferenceAnalysis record.
        
        Args:
            shadow: The ShadowCalculation to analyze
        
        Returns:
            The created ShadowDifferenceAnalysis record
        """
        # Check if analysis already exists
        existing = ShadowDifferenceAnalysis.objects.filter(
            shadow_calculation=shadow
        ).first()
        
        if existing:
            logger.info(f"Analysis already exists for shadow {shadow.id}")
            return existing
        
        # Run the reasoning engine
        result = self._engine.analyze(shadow)
        
        # Create the analysis record
        analysis = ShadowDifferenceAnalysis.objects.create(
            shadow_calculation=shadow,
            primary_reason=result.primary_reason,
            secondary_reason=result.secondary_reason,
            confidence_level=result.confidence_level,
            explanation=result.explanation,
            requires_human_review=result.requires_human_review,
            affected_fields=result.affected_fields,
            rule_trace=result.rule_trace,
            engine_version=self.ANALYZER_VERSION,
        )
        
        logger.info(
            f"Analyzed shadow {shadow.id}: "
            f"{result.primary_reason} ({result.confidence_level})"
        )
        
        return analysis
    
    def analyze_batch(
        self, 
        shadows: List[ShadowCalculation],
        skip_existing: bool = True,
    ) -> List[ShadowDifferenceAnalysis]:
        """
        Analyze multiple shadow calculations.
        
        Args:
            shadows: List of ShadowCalculation to analyze
            skip_existing: If True, skip already analyzed records
        
        Returns:
            List of created ShadowDifferenceAnalysis records
        """
        results = []
        
        for shadow in shadows:
            try:
                # Skip if already analyzed
                if skip_existing:
                    existing = ShadowDifferenceAnalysis.objects.filter(
                        shadow_calculation=shadow
                    ).exists()
                    if existing:
                        continue
                
                analysis = self.analyze(shadow)
                results.append(analysis)
                
            except Exception as e:
                logger.error(f"Failed to analyze shadow {shadow.id}: {e}")
                continue
        
        return results
    
    def analyze_pending(self, limit: int = 100) -> List[ShadowDifferenceAnalysis]:
        """
        Analyze shadow calculations that don't have analysis yet.
        
        Args:
            limit: Maximum number to analyze
        
        Returns:
            List of created ShadowDifferenceAnalysis records
        """
        # Find shadows without analysis
        pending = ShadowCalculation.objects.exclude(
            analysis__isnull=False
        ).order_by('-created_at')[:limit]
        
        return self.analyze_batch(list(pending), skip_existing=False)


# =============================================================================
# SINGLETON ACCESS
# =============================================================================

_analysis_service: Optional[DifferenceAnalysisService] = None


def get_analysis_service() -> DifferenceAnalysisService:
    """Get singleton analysis service instance."""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = DifferenceAnalysisService()
    return _analysis_service
