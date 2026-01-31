"""
Flexible Processor - Gap Analysis Module
Analyzes gaps between work blocks for fragmentation detection.
"""
from dataclasses import dataclass
from datetime import datetime

from .types import FlexPolicy, WarningCode
from .work_block import WorkBlock


@dataclass(frozen=True)
class Gap:
    """
    Represents a gap between two consecutive work blocks.
    """
    start: datetime
    end: datetime
    duration_minutes: int
    exceeds_threshold: bool


@dataclass
class GapAnalysisResult:
    """
    Result of gap analysis between work blocks.
    """
    gaps: list[Gap]
    total_gap_minutes: int
    longest_gap_minutes: int
    warnings: list[str]
    
    @property
    def has_excessive_gap(self) -> bool:
        """Check if any gap exceeds threshold."""
        return any(g.exceeds_threshold for g in self.gaps)
    
    @property
    def gap_count(self) -> int:
        """Number of gaps detected."""
        return len(self.gaps)


def analyze_gaps(
    blocks: list[WorkBlock],
    policy: FlexPolicy | None = None
) -> GapAnalysisResult:
    """
    Analyze gaps between consecutive work blocks.
    
    Args:
        blocks: List of WorkBlock objects (should be sorted by start time)
        policy: FlexPolicy for threshold checking (optional)
    
    Returns:
        GapAnalysisResult with all gaps and metrics
    
    Rules:
        - Only analyzes gaps between complete blocks
        - Negative gaps are flagged as warnings
        - Gaps are calculated as: next.start - prev.end
    """
    gaps: list[Gap] = []
    warnings: list[str] = []
    total_minutes = 0
    longest_minutes = 0
    
    # Default threshold if no policy
    threshold = policy.max_gap_minutes if policy else 240
    
    # Filter to complete blocks only
    complete_blocks = [b for b in blocks if b.is_complete and b.end_time is not None]
    
    # Sort by start time
    sorted_blocks = sorted(complete_blocks, key=lambda b: b.start_time)
    
    # Analyze gaps between consecutive blocks
    for i in range(len(sorted_blocks) - 1):
        current_block = sorted_blocks[i]
        next_block = sorted_blocks[i + 1]
        
        # Calculate gap
        gap_start = current_block.end_time
        gap_end = next_block.start_time
        
        if gap_start is None:
            continue
        
        delta = gap_end - gap_start
        duration = int(delta.total_seconds() // 60)
        
        # Handle negative gaps
        if duration < 0:
            warnings.append(WarningCode.NEGATIVE_GAP.value)
            continue
        
        # Create gap object
        gap = Gap(
            start=gap_start,
            end=gap_end,
            duration_minutes=duration,
            exceeds_threshold=duration > threshold,
        )
        gaps.append(gap)
        
        # Update metrics
        total_minutes += duration
        if duration > longest_minutes:
            longest_minutes = duration
    
    return GapAnalysisResult(
        gaps=gaps,
        total_gap_minutes=total_minutes,
        longest_gap_minutes=longest_minutes,
        warnings=warnings,
    )


def calculate_fragmentation_level(gap_result: GapAnalysisResult) -> str:
    """
    Calculate fragmentation level based on gap analysis.
    
    Args:
        gap_result: Result from analyze_gaps
    
    Returns:
        Fragmentation level: "LOW", "MEDIUM", or "HIGH"
    """
    gap_count = gap_result.gap_count
    
    if gap_count == 0:
        return "LOW"
    elif gap_count == 1:
        return "LOW"
    elif gap_count <= 3:
        return "MEDIUM"
    else:
        return "HIGH"
