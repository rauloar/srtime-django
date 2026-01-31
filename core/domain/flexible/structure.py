"""
Flexible Processor - Structural Analysis Module (Phase 2)
Handles block splitting and date attribution.
"""
from datetime import date, datetime, timedelta

from .types import FlexPolicy, WarningCode
from .work_block import WorkBlock, create_split_block


def apply_structural_splits(
    blocks: list[WorkBlock],
    policy: FlexPolicy
) -> tuple[list[WorkBlock], list[str]]:
    """
    Apply structural splits to blocks based on policy rules.
    
    Args:
        blocks: List of WorkBlock objects
        policy: FlexPolicy with split rules
    
    Returns:
        Tuple of (new list of blocks with splits applied, warnings)
    
    Split Rules:
        1. If duration > max_continuous_minutes (14h): split at midnight
        2. If force_midnight_split and block is overnight: split at midnight
    """
    result: list[WorkBlock] = []
    warnings: list[str] = []
    
    for block in blocks:
        # Skip incomplete blocks
        if not block.is_complete or block.end_time is None:
            result.append(block)
            continue
        
        duration = block.duration_minutes or 0
        
        # Check if split is needed
        needs_split = False
        
        # Rule 1: Excessive duration
        if duration > policy.max_continuous_minutes:
            needs_split = True
            warnings.append(WarningCode.EXCESSIVE_BLOCK.value)
        
        # Rule 2: Force midnight split
        if policy.force_midnight_split and block.is_overnight:
            needs_split = True
            warnings.append(WarningCode.OVERNIGHT_SHIFT.value)
        
        if needs_split and block.is_overnight:
            # Split at midnight
            split_blocks = split_block_at_midnight(block)
            result.extend(split_blocks)
            warnings.append(WarningCode.BLOCK_SPLIT.value)
        else:
            result.append(block)
    
    return result, warnings


def split_block_at_midnight(block: WorkBlock) -> list[WorkBlock]:
    """
    Split a block at midnight into two blocks.
    
    Args:
        block: WorkBlock that crosses midnight
    
    Returns:
        List of two WorkBlocks (before and after midnight)
    """
    if not block.is_complete or block.end_time is None:
        return [block]
    
    if not block.is_overnight:
        return [block]
    
    start = block.start_time
    end = block.end_time
    
    # Calculate midnight between start and end
    midnight = datetime.combine(
        start.date() + timedelta(days=1),
        datetime.min.time()
    )
    
    # Origin ID for traceability
    origin_id = block.start_punch.id
    
    # First block: start to midnight
    block1 = create_split_block(
        original=block,
        new_start=start,
        new_end=midnight,
        origin_id=origin_id,
    )
    
    # Second block: midnight to end
    block2 = create_split_block(
        original=block,
        new_start=midnight,
        new_end=end,
        origin_id=origin_id,
    )
    
    return [block1, block2]


def resolve_attribution(blocks: list[WorkBlock]) -> list[WorkBlock]:
    """
    Assign attribution date to each block.
    
    Args:
        blocks: List of WorkBlock objects
    
    Returns:
        New list of blocks with attribution_date set
    
    Rule:
        attribution_date = start_punch.timestamp.date()
    """
    result: list[WorkBlock] = []
    
    for block in blocks:
        attr_date = block.start_punch.timestamp.date()
        result.append(block.with_attribution(attr_date))
    
    return result


def filter_blocks_by_date(
    blocks: list[WorkBlock],
    target_date: date
) -> list[WorkBlock]:
    """
    Filter blocks to only those attributed to a specific date.
    
    Args:
        blocks: List of WorkBlock objects with attribution_date set
        target_date: Date to filter by
    
    Returns:
        Blocks where attribution_date matches target_date
    """
    return [b for b in blocks if b.attribution_date == target_date]


def get_complete_blocks(blocks: list[WorkBlock]) -> list[WorkBlock]:
    """
    Filter to only complete blocks.
    
    Args:
        blocks: List of WorkBlock objects
    
    Returns:
        Only blocks where is_complete is True
    """
    return [b for b in blocks if b.is_complete]


def get_incomplete_blocks(blocks: list[WorkBlock]) -> list[WorkBlock]:
    """
    Filter to only incomplete blocks.
    
    Args:
        blocks: List of WorkBlock objects
    
    Returns:
        Only blocks where is_complete is False
    """
    return [b for b in blocks if not b.is_complete]


def sort_blocks_by_time(blocks: list[WorkBlock]) -> list[WorkBlock]:
    """
    Sort blocks by start time.
    
    Args:
        blocks: List of WorkBlock objects
    
    Returns:
        Blocks sorted by start_time ascending
    """
    return sorted(blocks, key=lambda b: b.start_time)
