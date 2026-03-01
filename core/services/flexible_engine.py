"""
Flexible Attendance Engine - Orchestrator
Coordinates all phases of the flexible calculation pipeline.

This module is the ONLY place with control flow logic.
It calls domain functions in sequence without adding business rules.

Usage:
    result = calculate_flexible_day(
        employee_id=123,
        target_date=date(2025, 1, 15),
        punches=punch_list,
        policy=flex_policy,
        holidays=[date(2025, 1, 1)],
        has_leave=False,
    )
"""
from datetime import date, datetime
from typing import List, Set, Callable, Optional

from core.domain.flexible import (
    # Types
    Punch,
    FlexPolicy,
    WarningCode,
    # Phase 1: Parsing
    validate_punches,
    build_work_blocks,
    # Phase 2: Structure
    analyze_gaps,
    resolve_attribution,
    filter_blocks_by_date,
    apply_structural_splits,
    # Phase 3: Calculation
    compute_worked_minutes,
    compute_breaks,
    compute_net_worked,
    # Phase 4: Classification
    classify_regular_overtime,
    compute_night_minutes,
    check_holiday,
    # Phase 5: Status
    build_status_context,
    determine_status,
    FlexStatus,
    # Phase 6: Forensic
    ForensicContext,
    evaluate_forensic_flags,
    Confidence,
)
from core.domain.flexible.result import DailyCalculationResult


ENGINE_VERSION = "2.0.0"


def calculate_flexible_day(
    employee_id: int,
    target_date: date,
    punches: List[Punch],
    policy: FlexPolicy,
    holidays: List[date],
    has_leave: bool,
    is_rest_day: bool = False,
    now_provider: Optional[Callable[[], datetime]] = None,
) -> DailyCalculationResult:
    """
    Calculate attendance for a flexible work day.
    
    Orchestrates all phases of the calculation pipeline:
    1. Validation
    2. Parsing (punches → blocks)
    3. Structural analysis (gaps, splits)
    4. Base calculation (worked, breaks, net)
    5. Legal classification (overtime, night)
    6. Status determination
    7. Forensic evaluation
    8. Result assembly
    
    Args:
        employee_id: Employee identifier
        target_date: Date to calculate
        punches: List of clock punches (will be filtered to target_date)
        policy: FlexPolicy with calculation rules
        holidays: List of holiday dates (NO database access)
        has_leave: Whether employee has approved leave for this date
        is_rest_day: Whether this is a programmed rest day
        now_provider: Optional callable for current time (for testing)
    
    Returns:
        DailyCalculationResult with all computed fields
    
    Note:
        This function does NOT access the database.
        All data must be provided as parameters.
    """
    # Get current time for audit
    now = now_provider() if now_provider else datetime.now()
    
    # Convert holidays to set for O(1) lookup
    holidays_set: Set[date] = set(holidays)
    
    # =========================================================================
    # PHASE 1: VALIDATION
    # =========================================================================
    validation_warnings = validate_punches(punches, now_provider)
    
    # =========================================================================
    # PHASE 1: PARSING - Punches → WorkBlocks
    # =========================================================================
    blocks, parse_warnings = build_work_blocks(punches)
    
    # Combine warnings
    all_parse_warnings = validation_warnings + parse_warnings
    
    # =========================================================================
    # PHASE 2: STRUCTURE - Gaps, Splits, Attribution
    # =========================================================================
    # Apply structural splits (midnight, excessive duration)
    blocks, split_warnings = apply_structural_splits(blocks, policy)
    all_parse_warnings.extend(split_warnings)
    
    # Analyze gaps between blocks
    gap_result = analyze_gaps(blocks, policy)
    
    # Assign attribution dates
    blocks = resolve_attribution(blocks)
    
    # Filter to only blocks attributed to target date
    day_blocks = filter_blocks_by_date(blocks, target_date)
    
    # =========================================================================
    # PHASE 3: CALCULATION - Worked, Breaks, Net
    # =========================================================================
    worked_result = compute_worked_minutes(day_blocks)
    break_minutes = compute_breaks(worked_result.total_minutes, policy)
    net_worked = compute_net_worked(worked_result.total_minutes, break_minutes)
    
    # =========================================================================
    # PHASE 4: CLASSIFICATION - Legal categories
    # =========================================================================
    legal = classify_regular_overtime(net_worked, policy)
    night_result = compute_night_minutes(day_blocks, policy)
    effective_night_minutes = min(night_result.night_minutes, net_worked)
    is_holiday = check_holiday(target_date, holidays_set)
    
    # =========================================================================
    # PHASE 5: STATUS - Determine day status
    # =========================================================================
    status_context = build_status_context(
        blocks=day_blocks,
        net_worked_minutes=net_worked,
        legal=legal,
        is_holiday=is_holiday,
        has_leave=has_leave,
        is_rest_day=is_rest_day,
    )
    status = determine_status(status_context)
    
    # =========================================================================
    # PHASE 6: FORENSIC - Warnings and review flags
    # =========================================================================
    forensic_context = ForensicContext(
        blocks=day_blocks,
        worked_result=worked_result,
        net_worked_minutes=net_worked,
        legal=legal,
        gap_result=gap_result,
        policy=policy,
        parse_warnings=all_parse_warnings,
    )
    forensic = evaluate_forensic_flags(forensic_context)
    
    # =========================================================================
    # PHASE 7: RESULT ASSEMBLY
    # =========================================================================
    # Determine check_in and check_out from blocks
    check_in = None
    check_out = None
    
    complete_blocks = [b for b in day_blocks if b.is_complete]
    if complete_blocks:
        # First complete block's start
        sorted_blocks = sorted(complete_blocks, key=lambda b: b.start_time)
        check_in = sorted_blocks[0].start_time
        # Last complete block's end
        check_out = sorted_blocks[-1].end_time
    elif day_blocks:
        # Only orphan punches
        check_in = day_blocks[0].start_time
    
    return DailyCalculationResult(
        # Identity
        employee_id=employee_id,
        target_date=target_date,
        calculation_mode="FLEXIBLE",
        
        # Timestamps
        check_in=check_in,
        check_out=check_out,
        
        # Time metrics
        worked_minutes=worked_result.total_minutes,
        break_minutes=break_minutes,
        net_worked_minutes=net_worked,
        
        # Legal classification
        regular_minutes=legal.regular_minutes,
        overtime_minutes=legal.overtime_minutes,
        night_minutes=effective_night_minutes,
        
        # Structured mode fields (NULL in flexible)
        expected_minutes=None,
        late_minutes=None,
        early_out_minutes=None,
        
        # Status
        status=status.value,
        
        # Flags
        is_holiday=is_holiday,
        exceeded_daily_limit=legal.is_excessive,
        has_orphan_punch=worked_result.incomplete_blocks_count > 0,
        requires_review=forensic.requires_review,
        
        # Audit
        calculation_warnings=forensic.warnings,
        calculation_confidence=forensic.calculation_confidence,
        blocks_count=worked_result.complete_blocks_count,
        
        # Traceability
        policy_id=None,  # To be set by caller if needed
        timetable_id=None,  # Not used in flexible mode
        engine_version=ENGINE_VERSION,
        calculated_at=now,
        
        # Forensic
        forensic_flags=forensic.flags,
        source_punches_count=len(punches),
    )
