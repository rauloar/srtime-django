"""
Flexible Processor - Parsing Module (Phase 1)
Transforms raw punches into WorkBlocks.
All functions are pure with no side effects.
"""
from datetime import datetime
from typing import Callable

from .types import Punch, WarningCode
from .work_block import WorkBlock


def validate_punches(
    punches: list[Punch],
    now_provider: Callable[[], datetime] | None = None
) -> list[str]:
    """
    Validate a list of punches for data integrity.
    
    Args:
        punches: List of Punch objects to validate
        now_provider: Optional callable that returns current time (for testing)
    
    Returns:
        List of warning codes (empty if all valid)
    
    Validations:
        - Chronological order
        - No duplicate timestamps
        - No future timestamps
        - device_id present on each punch
    """
    warnings: list[str] = []
    
    if not punches:
        return warnings
    
    # Get current time for future check
    now = now_provider() if now_provider else datetime.now()
    
    seen_timestamps: set[datetime] = set()
    prev_timestamp: datetime | None = None
    
    for punch in punches:
        # Check device_id
        if not punch.device_id or punch.device_id.strip() == "":
            warnings.append(WarningCode.MISSING_DEVICE_ID.value)
        
        # Check future timestamp
        if punch.timestamp > now:
            warnings.append(WarningCode.FUTURE_TIMESTAMP.value)
        
        # Check duplicate
        if punch.timestamp in seen_timestamps:
            warnings.append(WarningCode.DUPLICATE_TIMESTAMP.value)
        seen_timestamps.add(punch.timestamp)
        
        # Check order
        if prev_timestamp is not None and punch.timestamp < prev_timestamp:
            warnings.append(WarningCode.UNORDERED_PUNCHES.value)
        prev_timestamp = punch.timestamp
    
    return warnings


def build_work_blocks(
    punches: list[Punch]
) -> tuple[list[WorkBlock], list[str]]:
    """
    Transform a list of punches into WorkBlocks.
    
    Args:
        punches: List of Punch objects, assumed to be pre-sorted chronologically
    
    Returns:
        Tuple of (list of WorkBlocks, list of warning codes)
    
    Rules:
        - Pairs punches sequentially (0-1, 2-3, etc.)
        - Odd punch at end creates incomplete block
        - Validates duration is positive
        - Flags micro-blocks (< 1 minute)
    """
    blocks: list[WorkBlock] = []
    warnings: list[str] = []
    
    if not punches:
        return blocks, warnings
    
    # Sort punches by timestamp to ensure correct pairing
    sorted_punches = sorted(punches, key=lambda p: p.timestamp)
    
    i = 0
    while i < len(sorted_punches):
        start_punch = sorted_punches[i]
        
        # Check if we have a pair
        if i + 1 < len(sorted_punches):
            end_punch = sorted_punches[i + 1]
            
            # Create complete block
            block = WorkBlock(
                start_punch=start_punch,
                end_punch=end_punch,
            )
            
            # Validate duration
            if block.duration_minutes is not None:
                if block.duration_minutes < 0:
                    warnings.append(WarningCode.NEGATIVE_DURATION.value)
                elif block.duration_minutes < 1:
                    warnings.append(WarningCode.MICRO_BLOCK.value)
            
            blocks.append(block)
            i += 2
        else:
            # Orphan punch - no pair
            block = WorkBlock(
                start_punch=start_punch,
                end_punch=None,
            )
            blocks.append(block)
            warnings.append(WarningCode.ORPHAN_PUNCH.value)
            i += 1
    
    return blocks, warnings


def sort_punches(punches: list[Punch]) -> list[Punch]:
    """
    Sort punches chronologically.
    
    Args:
        punches: List of Punch objects
    
    Returns:
        New list of punches sorted by timestamp
    """
    return sorted(punches, key=lambda p: p.timestamp)


def filter_valid_blocks(blocks: list[WorkBlock]) -> list[WorkBlock]:
    """
    Filter out invalid blocks (negative or micro duration).
    
    Args:
        blocks: List of WorkBlock objects
    
    Returns:
        List of valid blocks only
    """
    valid: list[WorkBlock] = []
    
    for block in blocks:
        # Keep incomplete blocks (for tracking)
        if not block.is_complete:
            valid.append(block)
            continue
        
        # Filter out invalid durations
        if block.duration_minutes is not None and block.duration_minutes >= 1:
            valid.append(block)
    
    return valid
