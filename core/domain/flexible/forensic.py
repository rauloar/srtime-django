"""
Flexible Processor - Forensic Module (Phase 6)
Evaluates audit flags and generates warnings for review.

This module analyzes the calculation for:
- Data quality issues
- Legal violations
- Anomalies requiring human review

It does NOT modify any data, only evaluates and reports.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict

from .types import FlexPolicy, WarningCode
from .work_block import WorkBlock
from .gaps import GapAnalysisResult
from .calculation import WorkedResult
from .classification import LegalClassification


class Severity(str, Enum):
    """Severity levels for warnings."""
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Confidence(str, Enum):
    """Confidence level in the calculation."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass(frozen=True)
class Warning:
    """
    A single warning about the calculation.
    """
    code: str
    severity: Severity
    message: str
    field_affected: str = ""


@dataclass
class ForensicResult:
    """
    Result of forensic evaluation.
    
    Contains all warnings, flags, and review requirements.
    """
    warnings: List[Warning] = field(default_factory=list)
    requires_review: bool = False
    calculation_confidence: Confidence = Confidence.HIGH
    flags: Dict[str, bool] = field(default_factory=dict)
    
    def add_warning(self, warning: Warning) -> None:
        """Add a warning to the list."""
        self.warnings.append(warning)
    
    @property
    def warning_count(self) -> int:
        """Total number of warnings."""
        return len(self.warnings)
    
    @property
    def has_critical(self) -> bool:
        """Check if any warning is critical."""
        return any(w.severity == Severity.CRITICAL for w in self.warnings)
    
    @property
    def has_high(self) -> bool:
        """Check if any warning is high severity."""
        return any(w.severity == Severity.HIGH for w in self.warnings)


@dataclass(frozen=True)
class ForensicContext:
    """
    Context for forensic evaluation.
    
    All inputs must be pre-computed.
    """
    blocks: List[WorkBlock]
    worked_result: WorkedResult
    net_worked_minutes: int
    legal: LegalClassification
    gap_result: GapAnalysisResult
    policy: FlexPolicy
    parse_warnings: List[str] = field(default_factory=list)


def evaluate_forensic_flags(context: ForensicContext) -> ForensicResult:
    """
    Evaluate all forensic flags and generate warnings.
    
    Args:
        context: ForensicContext with all pre-computed data
    
    Returns:
        ForensicResult with warnings and review requirements
    
    This function only evaluates, it does NOT modify any inputs.
    """
    result = ForensicResult()
    
    # Evaluate each category
    _evaluate_orphan_punches(context, result)
    _evaluate_excessive_work(context, result)
    _evaluate_gaps(context, result)
    _evaluate_fragmentation(context, result)
    _evaluate_overnight(context, result)
    _evaluate_parse_warnings(context, result)
    
    # Set flags
    result.flags = _build_flags(context, result)
    
    # Determine if review is required
    result.requires_review = _requires_review(context, result)
    
    # Calculate confidence
    result.calculation_confidence = _calculate_confidence(result)
    
    return result


def _evaluate_orphan_punches(context: ForensicContext, result: ForensicResult) -> None:
    """Check for orphan punches (incomplete blocks)."""
    incomplete_count = context.worked_result.incomplete_blocks_count
    
    if incomplete_count > 0:
        result.add_warning(Warning(
            code=WarningCode.ORPHAN_PUNCH.value,
            severity=Severity.HIGH,
            message=f"{incomplete_count} fichada(s) sin pareja detectada(s)",
            field_affected="check_out" if incomplete_count == 1 else "blocks",
        ))


def _evaluate_excessive_work(context: ForensicContext, result: ForensicResult) -> None:
    """Check for excessive work hours."""
    if context.legal.is_excessive:
        exceeded_by = context.net_worked_minutes - context.policy.daily_max_minutes
        result.add_warning(Warning(
            code="EXCESSIVE_SHIFT",
            severity=Severity.HIGH,
            message=f"Jornada excede límite legal por {exceeded_by} minutos",
            field_affected="net_worked_minutes",
        ))
    
    # Alert threshold (12+ hours)
    alert_threshold = 720  # 12 hours
    if context.net_worked_minutes > alert_threshold:
        result.add_warning(Warning(
            code="ALERT_THRESHOLD_EXCEEDED",
            severity=Severity.CRITICAL,
            message=f"Jornada peligrosamente larga: {context.net_worked_minutes} minutos",
            field_affected="net_worked_minutes",
        ))


def _evaluate_gaps(context: ForensicContext, result: ForensicResult) -> None:
    """Check for excessive gaps between blocks."""
    if context.gap_result.has_excessive_gap:
        result.add_warning(Warning(
            code="LONG_GAP_DETECTED",
            severity=Severity.MEDIUM,
            message=f"Gap de {context.gap_result.longest_gap_minutes}min detectado",
            field_affected="gaps",
        ))


def _evaluate_fragmentation(context: ForensicContext, result: ForensicResult) -> None:
    """Check for fragmented work day."""
    complete_count = context.worked_result.complete_blocks_count
    
    if complete_count > 2:
        result.add_warning(Warning(
            code="FRAGMENTED_SHIFT",
            severity=Severity.LOW,
            message=f"Jornada fragmentada en {complete_count} bloques",
            field_affected="blocks",
        ))


def _evaluate_overnight(context: ForensicContext, result: ForensicResult) -> None:
    """Check for overnight blocks."""
    overnight_count = sum(1 for b in context.blocks if b.is_overnight)
    
    if overnight_count > 0:
        result.add_warning(Warning(
            code=WarningCode.OVERNIGHT_SHIFT.value,
            severity=Severity.INFO,
            message=f"{overnight_count} bloque(s) cruza(n) medianoche",
            field_affected="blocks",
        ))


def _evaluate_parse_warnings(context: ForensicContext, result: ForensicResult) -> None:
    """Include warnings from parsing phase."""
    for warning_code in context.parse_warnings:
        if warning_code == WarningCode.MICRO_BLOCK.value:
            result.add_warning(Warning(
                code=warning_code,
                severity=Severity.LOW,
                message="Bloque menor a 1 minuto descartado",
                field_affected="blocks",
            ))
        elif warning_code == WarningCode.NEGATIVE_DURATION.value:
            result.add_warning(Warning(
                code=warning_code,
                severity=Severity.HIGH,
                message="Duración negativa detectada (datos corruptos)",
                field_affected="duration",
            ))


def _build_flags(context: ForensicContext, result: ForensicResult) -> Dict[str, bool]:
    """Build the flags dictionary."""
    return {
        "has_orphan_punch": context.worked_result.incomplete_blocks_count > 0,
        "is_excessive": context.legal.is_excessive,
        "is_fragmented": context.worked_result.complete_blocks_count > 2,
        "has_overnight": any(b.is_overnight for b in context.blocks),
        "has_long_gap": context.gap_result.has_excessive_gap,
        "has_critical_warning": result.has_critical,
    }


def _requires_review(context: ForensicContext, result: ForensicResult) -> bool:
    """
    Determine if human review is required.
    
    Review is required when:
    1. Any orphan punch exists
    2. Legal limit exceeded
    3. Alert threshold exceeded
    4. Any critical warning
    """
    if context.worked_result.incomplete_blocks_count > 0:
        return True
    
    if context.legal.is_excessive:
        return True
    
    if context.net_worked_minutes > 720:  # 12 hours
        return True
    
    if result.has_critical:
        return True
    
    return False


def _calculate_confidence(result: ForensicResult) -> Confidence:
    """
    Calculate confidence level based on warnings.
    
    - HIGH: No warnings or only INFO
    - MEDIUM: Only LOW/MEDIUM warnings
    - LOW: Any HIGH or CRITICAL warning
    """
    if result.has_critical or result.has_high:
        return Confidence.LOW
    
    medium_or_low = any(
        w.severity in (Severity.MEDIUM, Severity.LOW) 
        for w in result.warnings
    )
    
    if medium_or_low:
        return Confidence.MEDIUM
    
    return Confidence.HIGH
