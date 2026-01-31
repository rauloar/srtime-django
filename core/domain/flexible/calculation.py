"""
Flexible Processor - Calculation Module (Phase 3)
Pure mathematical functions for work time calculation.

This module transforms structural WorkBlocks into numeric metrics.
NO legal rules (overtime, holidays, status) are applied here.
"""
from dataclasses import dataclass
from typing import List

from .types import FlexPolicy
from .work_block import WorkBlock


@dataclass(frozen=True)
class WorkedResult:
    """
    Result of work time calculation from blocks.
    
    All values are in minutes.
    This is a pure structural metric, not a legal classification.
    """
    total_minutes: int
    complete_blocks_count: int
    incomplete_blocks_count: int
    longest_block_minutes: int


def compute_worked_minutes(blocks: List[WorkBlock]) -> WorkedResult:
    """
    Calculate gross work metrics from a list of WorkBlocks.
    
    Args:
        blocks: List of WorkBlock objects
    
    Returns:
        WorkedResult with aggregated metrics
    
    Rules:
        - Only complete blocks (is_complete=True) contribute to total
        - Blocks with None duration are ignored
        - Incomplete blocks are counted but not summed
    """
    total_minutes = 0
    complete_count = 0
    incomplete_count = 0
    longest = 0
    
    for block in blocks:
        if not block.is_complete:
            incomplete_count += 1
            continue
        
        # Skip if duration is None or invalid
        duration = block.duration_minutes
        if duration is None or duration < 0:
            continue
        
        complete_count += 1
        total_minutes += duration
        
        if duration > longest:
            longest = duration
    
    return WorkedResult(
        total_minutes=total_minutes,
        complete_blocks_count=complete_count,
        incomplete_blocks_count=incomplete_count,
        longest_block_minutes=longest,
    )


def compute_breaks(worked_minutes: int, policy: FlexPolicy) -> int:
    """
    Calculate automatic break deductions based on policy.
    
    Args:
        worked_minutes: Gross worked time in minutes
        policy: FlexPolicy with break thresholds
    
    Returns:
        Total break minutes to deduct
    
    Rules:
        - Break is applied if worked > threshold
        - Multiple thresholds can stack
        - This is a policy deduction, NOT verification of actual break
    
    Note:
        This function does NOT verify if the worker actually took the break.
        It applies a policy-based deduction for calculation purposes.
    """
    if worked_minutes <= 0:
        return 0
    
    break_minutes = 0
    
    # First threshold
    if worked_minutes > policy.break_threshold_minutes:
        break_minutes += policy.break_duration_minutes
    
    # Second threshold (additional break for longer shifts)
    if worked_minutes > policy.break_threshold_2:
        break_minutes += policy.break_duration_2
    
    return break_minutes


def compute_net_worked(worked_minutes: int, break_minutes: int) -> int:
    """
    Calculate net worked time after break deduction.
    
    Args:
        worked_minutes: Gross worked time in minutes
        break_minutes: Break deduction in minutes
    
    Returns:
        Net worked time (minimum 0)
    
    Invariant:
        net_worked >= 0
    """
    net = worked_minutes - break_minutes
    
    if net < 0:
        return 0
    
    return net


def compute_total_from_blocks(blocks: List[WorkBlock], policy: FlexPolicy) -> tuple[int, int, int]:
    """
    Convenience function to compute all base metrics in one call.
    
    Args:
        blocks: List of WorkBlock objects
        policy: FlexPolicy with break rules
    
    Returns:
        Tuple of (worked_minutes, break_minutes, net_worked_minutes)
    
    This is a composition of the three core functions.
    """
    result = compute_worked_minutes(blocks)
    breaks = compute_breaks(result.total_minutes, policy)
    net = compute_net_worked(result.total_minutes, breaks)
    
    return result.total_minutes, breaks, net
