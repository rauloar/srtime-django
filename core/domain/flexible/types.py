"""
Flexible Processor - Common Types and Enums
Pure domain types for the flexible attendance calculation engine.
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class WarningCode(str, Enum):
    """Warning codes for parsing and structural analysis."""
    # Parsing warnings
    ORPHAN_PUNCH = "ORPHAN_PUNCH"
    NEGATIVE_DURATION = "NEGATIVE_DURATION"
    MICRO_BLOCK = "MICRO_BLOCK"
    DUPLICATE_TIMESTAMP = "DUPLICATE_TIMESTAMP"
    UNORDERED_PUNCHES = "UNORDERED_PUNCHES"
    FUTURE_TIMESTAMP = "FUTURE_TIMESTAMP"
    MISSING_DEVICE_ID = "MISSING_DEVICE_ID"
    
    # Structural warnings
    EXCESSIVE_BLOCK = "EXCESSIVE_BLOCK"
    BLOCK_SPLIT = "BLOCK_SPLIT"
    NEGATIVE_GAP = "NEGATIVE_GAP"
    OVERNIGHT_SHIFT = "OVERNIGHT_SHIFT"


@dataclass(frozen=True)
class Punch:
    """
    Immutable representation of a clock punch.
    This is the raw input from biometric devices.
    """
    id: int
    timestamp: datetime
    device_id: str


@dataclass(frozen=True)
class FlexPolicy:
    """
    Policy configuration for flexible schedule processing.
    All time values are in minutes unless otherwise specified.
    """
    # Block validation
    min_block_minutes: int = 1
    max_block_minutes: int = 840  # 14 hours
    
    # Gap thresholds
    max_gap_minutes: int = 240  # 4 hours
    
    # Structural rules
    force_midnight_split: bool = False
    max_continuous_minutes: int = 840  # 14 hours - triggers split
    
    # Break policy
    break_threshold_minutes: int = 360  # 6 hours
    break_duration_minutes: int = 30
    break_threshold_2: int = 540  # 9 hours
    break_duration_2: int = 15
    
    # Legal limits
    daily_regular_minutes: int = 480  # 8 hours
    daily_max_minutes: int = 600  # 10 hours
    
    # Night shift
    night_start_hour: int = 22
    night_end_hour: int = 6
