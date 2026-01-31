"""
Flexible Processor - WorkBlock Model
Core data structure representing a paired punch interval.
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

from .types import Punch


@dataclass
class WorkBlock:
    """
    Represents a work interval formed by a pair of punches.
    
    A complete block has both start and end punches.
    An incomplete block only has a start punch (orphan).
    """
    start_punch: Punch
    end_punch: Optional[Punch] = None
    duration_minutes: Optional[int] = None
    is_complete: bool = False
    is_overnight: bool = False
    attribution_date: Optional[date] = None
    split_origin_id: Optional[int] = None  # ID of original block if this was split
    
    def __post_init__(self) -> None:
        """Compute derived fields after initialization."""
        self.is_complete = self.end_punch is not None
        
        if self.is_complete and self.end_punch is not None:
            # Calculate duration
            delta = self.end_punch.timestamp - self.start_punch.timestamp
            self.duration_minutes = int(delta.total_seconds() // 60)
            
            # Check if overnight
            self.is_overnight = (
                self.start_punch.timestamp.date() != self.end_punch.timestamp.date()
            )
    
    @property
    def start_time(self) -> datetime:
        """Convenience accessor for start timestamp."""
        return self.start_punch.timestamp
    
    @property
    def end_time(self) -> Optional[datetime]:
        """Convenience accessor for end timestamp."""
        return self.end_punch.timestamp if self.end_punch else None
    
    def with_attribution(self, attr_date: date) -> "WorkBlock":
        """Return a new WorkBlock with attribution date set."""
        return WorkBlock(
            start_punch=self.start_punch,
            end_punch=self.end_punch,
            duration_minutes=self.duration_minutes,
            is_complete=self.is_complete,
            is_overnight=self.is_overnight,
            attribution_date=attr_date,
            split_origin_id=self.split_origin_id,
        )


def create_split_block(
    original: WorkBlock,
    new_start: datetime,
    new_end: datetime,
    origin_id: int
) -> WorkBlock:
    """
    Create a new WorkBlock as a split from an original block.
    
    Used when dividing blocks at midnight or due to excessive duration.
    The new block maintains traceability via split_origin_id.
    """
    # Create synthetic punches for the split
    start_punch = Punch(
        id=original.start_punch.id,
        timestamp=new_start,
        device_id=original.start_punch.device_id,
    )
    end_punch = Punch(
        id=original.end_punch.id if original.end_punch else original.start_punch.id,
        timestamp=new_end,
        device_id=original.start_punch.device_id,
    )
    
    return WorkBlock(
        start_punch=start_punch,
        end_punch=end_punch,
        split_origin_id=origin_id,
    )
