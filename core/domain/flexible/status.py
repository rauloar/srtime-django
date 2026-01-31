"""
Flexible Processor - Status Module (Phase 5)
Determines the final status of a work day.

This module applies the status decision tree based on:
- Block completeness
- Net worked time
- Legal classification
- Leave/holiday flags

It does NOT modify blocks, calculate times, or access DB.
"""
from dataclasses import dataclass
from enum import Enum
from typing import List

from .types import FlexPolicy
from .work_block import WorkBlock
from .classification import LegalClassification


class FlexStatus(str, Enum):
    """
    Status of a flexible work day.
    
    These are mutually exclusive final states.
    """
    WORKED = "Worked"
    INCOMPLETE = "Incomplete"
    ABSENT = "Absent"
    EXCESSIVE = "Excessive"
    LEAVE = "Leave"
    HOLIDAY_WORKED = "HolidayWorked"
    REST_DAY = "RestDay"


@dataclass(frozen=True)
class StatusContext:
    """
    Context needed for status determination.
    
    All values must be pre-computed before calling determine_status.
    """
    has_complete_blocks: bool
    has_incomplete_blocks: bool
    has_any_blocks: bool
    net_worked_minutes: int
    is_excessive: bool
    is_holiday: bool
    has_leave: bool
    is_rest_day: bool = False


def determine_status(context: StatusContext) -> FlexStatus:
    """
    Determine the final status of a work day.
    
    Args:
        context: StatusContext with all pre-computed flags
    
    Returns:
        FlexStatus enum value
    
    Decision Tree:
        1. If has_leave → Leave
        2. If no blocks → Absent (or RestDay if marked)
        3. If all blocks incomplete → Incomplete
        4. If excessive time → Excessive
        5. If holiday with work → HolidayWorked
        6. Otherwise → Worked
    """
    # Priority 1: Leave takes precedence
    if context.has_leave:
        return FlexStatus.LEAVE
    
    # Priority 2: No work at all
    if not context.has_any_blocks:
        if context.is_rest_day:
            return FlexStatus.REST_DAY
        return FlexStatus.ABSENT
    
    # Priority 3: Only orphan punches
    if not context.has_complete_blocks and context.has_incomplete_blocks:
        return FlexStatus.INCOMPLETE
    
    # Priority 4: Excessive work (legal violation)
    if context.is_excessive:
        return FlexStatus.EXCESSIVE
    
    # Priority 5: Holiday with work
    if context.is_holiday and context.net_worked_minutes > 0:
        return FlexStatus.HOLIDAY_WORKED
    
    # Default: Normal worked day
    return FlexStatus.WORKED


def build_status_context(
    blocks: List[WorkBlock],
    net_worked_minutes: int,
    legal: LegalClassification,
    is_holiday: bool,
    has_leave: bool,
    is_rest_day: bool = False,
) -> StatusContext:
    """
    Build StatusContext from component parts.
    
    This is a convenience function to construct the context
    from the outputs of previous phases.
    
    Args:
        blocks: List of WorkBlocks (not modified)
        net_worked_minutes: From Phase 3
        legal: LegalClassification from Phase 4
        is_holiday: From check_holiday
        has_leave: From external leave check
        is_rest_day: If this is a programmed rest day
    
    Returns:
        StatusContext ready for determine_status
    """
    has_complete = any(b.is_complete for b in blocks)
    has_incomplete = any(not b.is_complete for b in blocks)
    has_any = len(blocks) > 0
    
    return StatusContext(
        has_complete_blocks=has_complete,
        has_incomplete_blocks=has_incomplete,
        has_any_blocks=has_any,
        net_worked_minutes=net_worked_minutes,
        is_excessive=legal.is_excessive,
        is_holiday=is_holiday,
        has_leave=has_leave,
        is_rest_day=is_rest_day,
    )
