"""
Timeline Normalizer & Validator
Ensures temporal integrity of timeline blocks.

NO business logic changes.
Only structural/mathematical consistency.
"""
from datetime import datetime, time, timedelta
from typing import List, Dict, Any, Tuple
import logging

from core.models_timeline import BlockType


logger = logging.getLogger('timeline.integrity')


class TimelineIntegrityError(Exception):
    """Raised when timeline blocks violate temporal integrity invariants."""
    pass


class TimelineValidator:
    """
    Validates timeline blocks for temporal integrity.
    
    Enforces invariants:
    1. No overlapping blocks
    2. No negative durations
    3. Correct temporal order
    4. Durations match time ranges
    """
    
    def validate(self, blocks: List[Dict[str, Any]]) -> None:
        """
        Validate timeline blocks.
        
        Args:
            blocks: List of block dictionaries
        
        Raises:
            TimelineIntegrityError: If validation fails
        """
        if not blocks:
            return
        
        # Check each block individually
        for i, block in enumerate(blocks):
            self._validate_single_block(block, i)
        
        # Check temporal order
        self._validate_temporal_order(blocks)
        
        # Check for overlaps
        self._validate_no_overlaps(blocks)
        
        # Check duration correctness
        self._validate_durations(blocks)
    
    def _validate_single_block(self, block: Dict[str, Any], index: int) -> None:
        """Validate a single block's basic properties."""
        # Required fields
        required = ['block_type', 'start_time', 'end_time', 'duration_minutes']
        for field in required:
            if field not in block:
                raise TimelineIntegrityError(
                    f"Block {index}: Missing required field '{field}'"
                )
        
        # Time range validity
        start = block['start_time']
        end = block['end_time']
        
        if start >= end:
            raise TimelineIntegrityError(
                f"Block {index}: start_time ({start}) must be before end_time ({end})"
            )
        
        # Duration must be positive
        if block['duration_minutes'] <= 0:
            raise TimelineIntegrityError(
                f"Block {index}: duration_minutes must be positive, got {block['duration_minutes']}"
            )
    
    def _validate_temporal_order(self, blocks: List[Dict[str, Any]]) -> None:
        """Validate blocks are in temporal order."""
        for i in range(len(blocks) - 1):
            current_start = blocks[i]['start_time']
            next_start = blocks[i + 1]['start_time']
            
            if current_start > next_start:
                raise TimelineIntegrityError(
                    f"Blocks not in temporal order: "
                    f"block {i} starts at {current_start}, "
                    f"but block {i+1} starts at {next_start}"
                )
    
    def _validate_no_overlaps(self, blocks: List[Dict[str, Any]]) -> None:
        """Validate no blocks overlap."""
        for i in range(len(blocks) - 1):
            current_end = blocks[i]['end_time']
            next_start = blocks[i + 1]['start_time']
            
            if current_end > next_start:
                raise TimelineIntegrityError(
                    f"Blocks {i} and {i+1} overlap: "
                    f"block {i} ends at {current_end}, "
                    f"but block {i+1} starts at {next_start}"
                )
    
    def _validate_durations(self, blocks: List[Dict[str, Any]]) -> None:
        """Validate duration matches time range."""
        for i, block in enumerate(blocks):
            calculated = self._calculate_duration(
                block['start_time'],
                block['end_time']
            )
            stated = block['duration_minutes']
            
            # Allow 1 minute tolerance for rounding
            if abs(calculated - stated) > 1:
                logger.warning(
                    f"Block {i}: duration mismatch - "
                    f"calculated {calculated} min, stated {stated} min"
                )


class TimelineNormalizer:
    """
    Normalizes timeline blocks to ensure temporal integrity.
    
    Operations:
    1. Sort blocks by start_time
    2. Fix overlapping blocks (trim second block)
    3. Fill gaps with GAP_UNCLASSIFIED
    4. Recalculate durations
    
    Does NOT change business meaning, only structure.
    """
    
    def __init__(self):
        self.validator = TimelineValidator()
    
    def normalize(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize timeline blocks.
        
        Args:
            blocks: List of block dictionaries (may be out of order, overlapping, etc.)
        
        Returns:
            Normalized list of block dictionaries
        """
        if not blocks:
            return []
        
        # Step 1: Sort by start_time
        sorted_blocks = sorted(blocks, key=lambda b: b['start_time'])
        
        # Step 2: Fix overlaps
        non_overlapping = self._fix_overlaps(sorted_blocks)
        
        # Step 3: Fill gaps
        complete_timeline = self._fill_gaps(non_overlapping)
        
        # Step 4: Recalculate durations
        final_timeline = self._recalculate_durations(complete_timeline)
        
        # Step 5: Validate
        try:
            self.validator.validate(final_timeline)
        except TimelineIntegrityError as e:
            logger.error(f"Timeline validation failed after normalization: {e}")
            # Return original blocks if normalization failed
            return blocks
        
        return final_timeline
    
    def _fix_overlaps(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Fix overlapping blocks by trimming the later block.
        
        Strategy: If block B starts before block A ends, trim B's start to A's end.
        """
        if len(blocks) <= 1:
            return blocks
        
        fixed = [blocks[0]]
        
        for i in range(1, len(blocks)):
            current = blocks[i].copy()
            previous = fixed[-1]
            
            # Check for overlap
            if current['start_time'] < previous['end_time']:
                logger.warning(
                    f"Overlap detected: {previous['block_type']} ends at {previous['end_time']}, "
                    f"but {current['block_type']} starts at {current['start_time']}. "
                    f"Trimming {current['block_type']} start to {previous['end_time']}."
                )
                
                # Trim current block's start
                current['start_time'] = previous['end_time']
                
                # If trim makes block invalid (start >= end), skip it
                if current['start_time'] >= current['end_time']:
                    logger.warning(
                        f"Block {current['block_type']} completely overlapped, removing"
                    )
                    continue
            
            fixed.append(current)
        
        return fixed
    
    def _fill_gaps(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Fill gaps between blocks with GAP_UNCLASSIFIED.
        
        Only fills gaps between consecutive blocks, not at start/end of day.
        """
        if len(blocks) <= 1:
            return blocks
        
        complete = [blocks[0]]
        
        for i in range(1, len(blocks)):
            previous = complete[-1]
            current = blocks[i]
            
            # Check for gap
            gap_duration = self._calculate_duration(
                previous['end_time'],
                current['start_time']
            )
            
            # If gap > 1 minute (tolerance for rounding)
            if gap_duration > 1:
                logger.info(
                    f"Gap detected: {gap_duration} min between "
                    f"{previous['end_time']} and {current['start_time']}. "
                    f"Inserting GAP_UNCLASSIFIED."
                )
                
                # Create gap block
                gap_block = {
                    'block_type': BlockType.GAP_UNCLASSIFIED,
                    'start_time': previous['end_time'],
                    'end_time': current['start_time'],
                    'duration_minutes': gap_duration,
                    'related_rule': 'AUTO_FILLED_GAP',
                    'anomaly_code': 'UNCLASSIFIED_GAP',
                }
                complete.append(gap_block)
            
            complete.append(current)
        
        return complete
    
    def _recalculate_durations(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Recalculate duration for all blocks based on time range."""
        recalculated = []
        
        for block in blocks:
            block_copy = block.copy()
            block_copy['duration_minutes'] = self._calculate_duration(
                block['start_time'],
                block['end_time']
            )
            recalculated.append(block_copy)
        
        return recalculated
    
    def _calculate_duration(self, start: time, end: time) -> int:
        """Calculate duration in minutes between two times."""
        today = datetime.today().date()
        start_dt = datetime.combine(today, start)
        end_dt = datetime.combine(today, end)
        
        # Handle crossing midnight
        if end < start:
            end_dt += timedelta(days=1)
        
        delta = end_dt - start_dt
        return int(delta.total_seconds() / 60)
