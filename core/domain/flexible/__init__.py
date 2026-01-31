"""
Flexible Processor Domain Module
Pure domain logic for flexible schedule attendance calculation.

This module contains no Django dependencies and is fully testable in isolation.
"""
from .types import FlexPolicy, Punch, WarningCode
from .work_block import WorkBlock, create_split_block
from .parsing import (
    build_work_blocks,
    filter_valid_blocks,
    sort_punches,
    validate_punches,
)
from .gaps import (
    Gap,
    GapAnalysisResult,
    analyze_gaps,
    calculate_fragmentation_level,
)
from .structure import (
    apply_structural_splits,
    filter_blocks_by_date,
    get_complete_blocks,
    get_incomplete_blocks,
    resolve_attribution,
    sort_blocks_by_time,
    split_block_at_midnight,
)
from .calculation import (
    WorkedResult,
    compute_breaks,
    compute_net_worked,
    compute_total_from_blocks,
    compute_worked_minutes,
)
from .classification import (
    LegalClassification,
    NightWorkResult,
    check_holiday,
    check_holiday_from_list,
    classify_regular_overtime,
    compute_night_minutes,
)
from .status import (
    FlexStatus,
    StatusContext,
    build_status_context,
    determine_status,
)
from .forensic import (
    Confidence,
    ForensicContext,
    ForensicResult,
    Severity,
    Warning,
    evaluate_forensic_flags,
)
from .result import DailyCalculationResult

__all__ = [
    # Types
    "FlexPolicy",
    "Punch",
    "WarningCode",
    # WorkBlock
    "WorkBlock",
    "create_split_block",
    # Parsing
    "build_work_blocks",
    "filter_valid_blocks",
    "sort_punches",
    "validate_punches",
    # Gaps
    "Gap",
    "GapAnalysisResult",
    "analyze_gaps",
    "calculate_fragmentation_level",
    # Structure
    "apply_structural_splits",
    "filter_blocks_by_date",
    "get_complete_blocks",
    "get_incomplete_blocks",
    "resolve_attribution",
    "sort_blocks_by_time",
    "split_block_at_midnight",
    # Calculation
    "WorkedResult",
    "compute_breaks",
    "compute_net_worked",
    "compute_total_from_blocks",
    "compute_worked_minutes",
    # Classification
    "LegalClassification",
    "NightWorkResult",
    "check_holiday",
    "check_holiday_from_list",
    "classify_regular_overtime",
    "compute_night_minutes",
    # Status
    "FlexStatus",
    "StatusContext",
    "build_status_context",
    "determine_status",
    # Forensic
    "Confidence",
    "ForensicContext",
    "ForensicResult",
    "Severity",
    "Warning",
    "evaluate_forensic_flags",
    # Result
    "DailyCalculationResult",
]
