"""
Flexible Processor - Classification Module (Phase 4)
Legal classification of already-calculated work time.

This module classifies time that Phase 3 already computed.
It does NOT calculate worked minutes, breaks, or modify blocks.

Classification includes:
- Regular vs Overtime
- Night work (nocturnidad)
- Holiday work
"""
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import List, Set

from .types import FlexPolicy
from .work_block import WorkBlock


@dataclass(frozen=True)
class LegalClassification:
    """
    Classification of net worked time into legal categories.
    
    Invariant: regular_minutes + overtime_minutes = input net_worked
    """
    regular_minutes: int
    overtime_minutes: int
    is_excessive: bool


@dataclass(frozen=True)
class NightWorkResult:
    """
    Result of night work calculation.
    
    night_minutes is the intersection of worked blocks with the night range.
    """
    night_minutes: int
    night_blocks_count: int  # How many blocks had night work


def classify_regular_overtime(
    net_worked_minutes: int,
    policy: FlexPolicy
) -> LegalClassification:
    """
    Classify net worked time into regular and overtime.
    
    Args:
        net_worked_minutes: Already-calculated net worked time
        policy: FlexPolicy with daily limits
    
    Returns:
        LegalClassification with regular, overtime, and excessive flag
    
    Rules:
        regular = min(net_worked, daily_regular)
        overtime = max(0, net_worked - daily_regular)
        is_excessive = net_worked > daily_max
    """
    if net_worked_minutes <= 0:
        return LegalClassification(
            regular_minutes=0,
            overtime_minutes=0,
            is_excessive=False,
        )
    
    regular = min(net_worked_minutes, policy.daily_regular_minutes)
    overtime = max(0, net_worked_minutes - policy.daily_regular_minutes)
    is_excessive = net_worked_minutes > policy.daily_max_minutes
    
    return LegalClassification(
        regular_minutes=regular,
        overtime_minutes=overtime,
        is_excessive=is_excessive,
    )


def compute_night_minutes(
    blocks: List[WorkBlock],
    policy: FlexPolicy
) -> NightWorkResult:
    """
    Calculate minutes worked within the night range.
    
    Args:
        blocks: List of WorkBlock (already structured, not modified)
        policy: FlexPolicy with night_start_hour and night_end_hour
    
    Returns:
        NightWorkResult with total night minutes
    
    Rules:
        Night range is typically 22:00 - 06:00
        For each block, calculate intersection with night range
        Handle overnight blocks correctly
    """
    total_night = 0
    blocks_with_night = 0
    
    for block in blocks:
        if not block.is_complete or block.end_time is None:
            continue
        
        night = _intersect_with_night_range(
            block.start_time,
            block.end_time,
            policy.night_start_hour,
            policy.night_end_hour,
        )
        
        if night > 0:
            total_night += night
            blocks_with_night += 1
    
    return NightWorkResult(
        night_minutes=total_night,
        night_blocks_count=blocks_with_night,
    )


def _intersect_with_night_range(
    start: datetime,
    end: datetime,
    night_start_hour: int,
    night_end_hour: int,
) -> int:
    """
    Calculate minutes of intersection between a time range and night hours.
    
    Handles:
        - Blocks that start before night
        - Blocks that end after night
        - Blocks fully within night
        - Blocks that cross midnight
        - Night range that crosses midnight (e.g., 22:00-06:00)
    
    Args:
        start: Block start datetime
        end: Block end datetime
        night_start_hour: Hour when night begins (e.g., 22)
        night_end_hour: Hour when night ends (e.g., 6)
    
    Returns:
        Minutes of intersection
    """
    if start >= end:
        return 0
    
    total_night_minutes = 0
    current = start
    
    while current < end:
        current_date = current.date()
        
        # Night period for this date (night_start today to night_end tomorrow)
        night_start_today = datetime.combine(current_date, time(night_start_hour, 0))
        night_end_tomorrow = datetime.combine(
            current_date + timedelta(days=1), 
            time(night_end_hour, 0)
        )
        
        # Also check previous night (night_start yesterday to night_end today)
        night_end_today = datetime.combine(current_date, time(night_end_hour, 0))
        night_start_yesterday = datetime.combine(
            current_date - timedelta(days=1),
            time(night_start_hour, 0)
        )
        
        # Calculate intersection with today's night range
        if night_start_today < end and night_end_tomorrow > start:
            range_start = max(start, night_start_today)
            range_end = min(end, night_end_tomorrow)
            if range_start < range_end:
                delta = (range_end - range_start).total_seconds() / 60
                total_night_minutes += int(delta)
        
        # Calculate intersection with morning part of previous night
        if current.hour < night_end_hour:
            if night_start_yesterday < end and night_end_today > start:
                range_start = max(start, current)
                range_end = min(end, night_end_today)
                if range_start < range_end and range_start.hour < night_end_hour:
                    delta = (range_end - range_start).total_seconds() / 60
                    # Only count if we haven't already counted this in previous iteration
                    if range_start >= start:
                        total_night_minutes += int(delta)
        
        # Move to next day to avoid double counting
        current = datetime.combine(current_date + timedelta(days=1), time(0, 0))
    
    return total_night_minutes


def check_holiday(target_date: date, holidays: Set[date]) -> bool:
    """
    Check if a date is a holiday.
    
    Args:
        target_date: Date to check
        holidays: Set of holiday dates (NO database access)
    
    Returns:
        True if target_date is in holidays set
    """
    return target_date in holidays


def check_holiday_from_list(target_date: date, holidays: List[date]) -> bool:
    """
    Check if a date is a holiday (list version).
    
    Args:
        target_date: Date to check
        holidays: List of holiday dates
    
    Returns:
        True if target_date is in holidays list
    """
    return target_date in holidays
