"""
Pytest fixtures for Flexible Processor tests.
Provides reusable test data and configurations.
"""
import pytest
from datetime import datetime, date, timedelta

from core.domain.flexible import Punch, FlexPolicy


# =============================================================================
# DATE FIXTURES
# =============================================================================

@pytest.fixture
def base_date() -> date:
    """Standard test date (non-holiday, non-weekend)."""
    return date(2025, 1, 15)  # Wednesday


@pytest.fixture
def holiday_date() -> date:
    """A holiday date."""
    return date(2025, 1, 1)  # New Year


@pytest.fixture
def holidays() -> list[date]:
    """List of holiday dates for testing."""
    return [
        date(2025, 1, 1),   # New Year
        date(2025, 5, 1),   # Labor Day
        date(2025, 12, 25), # Christmas
    ]


# =============================================================================
# POLICY FIXTURES
# =============================================================================

@pytest.fixture
def default_policy() -> FlexPolicy:
    """Standard flex policy with default values."""
    return FlexPolicy()


@pytest.fixture
def strict_policy() -> FlexPolicy:
    """Strict policy with lower limits."""
    return FlexPolicy(
        daily_regular_minutes=480,
        daily_max_minutes=540,  # 9 hours max
        max_gap_minutes=120,
    )


# =============================================================================
# PUNCH FIXTURES - Normal Day
# =============================================================================

@pytest.fixture
def normal_day_punches(base_date: date) -> list[Punch]:
    """
    Normal 8-hour day with lunch break.
    08:00-12:00, 13:00-17:00
    Expected: worked=480, break=30, net=450
    """
    base = datetime.combine(base_date, datetime.min.time().replace(hour=8))
    return [
        Punch(1, base, "DEV1"),                           # 08:00 IN
        Punch(2, base + timedelta(hours=4), "DEV1"),      # 12:00 OUT
        Punch(3, base + timedelta(hours=5), "DEV1"),      # 13:00 IN
        Punch(4, base + timedelta(hours=9), "DEV1"),      # 17:00 OUT
    ]


@pytest.fixture
def overtime_punches(base_date: date) -> list[Punch]:
    """
    10-hour day (overtime).
    08:00-18:00
    Expected: overtime > 0
    """
    base = datetime.combine(base_date, datetime.min.time().replace(hour=8))
    return [
        Punch(1, base, "DEV1"),                           # 08:00 IN
        Punch(2, base + timedelta(hours=10), "DEV1"),     # 18:00 OUT
    ]


@pytest.fixture
def excessive_punches(base_date: date) -> list[Punch]:
    """
    Excessive 14-hour day.
    06:00-20:00
    Expected: is_excessive=True, requires_review=True
    """
    base = datetime.combine(base_date, datetime.min.time().replace(hour=6))
    return [
        Punch(1, base, "DEV1"),                           # 06:00 IN
        Punch(2, base + timedelta(hours=14), "DEV1"),     # 20:00 OUT
    ]


@pytest.fixture
def night_shift_punches(base_date: date) -> list[Punch]:
    """
    Full night shift.
    22:00-06:00 (next day)
    Expected: night_minutes=480
    """
    base = datetime.combine(base_date, datetime.min.time().replace(hour=22))
    return [
        Punch(1, base, "DEV1"),                           # 22:00 IN
        Punch(2, base + timedelta(hours=8), "DEV1"),      # 06:00 OUT (next day)
    ]


@pytest.fixture
def orphan_punch(base_date: date) -> list[Punch]:
    """
    Single punch without pair.
    08:00 IN (no OUT)
    Expected: status=Incomplete, requires_review=True
    """
    base = datetime.combine(base_date, datetime.min.time().replace(hour=8))
    return [
        Punch(1, base, "DEV1"),  # 08:00 IN only
    ]


@pytest.fixture
def holiday_work_punches(holiday_date: date) -> list[Punch]:
    """
    Work on a holiday.
    08:00-12:00 on Jan 1st
    Expected: status=HolidayWorked
    """
    base = datetime.combine(holiday_date, datetime.min.time().replace(hour=8))
    return [
        Punch(1, base, "DEV1"),                           # 08:00 IN
        Punch(2, base + timedelta(hours=4), "DEV1"),      # 12:00 OUT
    ]


@pytest.fixture
def empty_punches() -> list[Punch]:
    """No punches at all."""
    return []


@pytest.fixture
def future_punch() -> list[Punch]:
    """Punch with future timestamp."""
    future = datetime.now() + timedelta(days=30)
    return [
        Punch(1, future, "DEV1"),
        Punch(2, future + timedelta(hours=4), "DEV1"),
    ]


@pytest.fixture
def long_gap_punches(base_date: date) -> list[Punch]:
    """
    Day with a very long gap between blocks.
    08:00-09:00, 15:00-17:00 (6 hour gap)
    """
    base = datetime.combine(base_date, datetime.min.time().replace(hour=8))
    return [
        Punch(1, base, "DEV1"),                           # 08:00 IN
        Punch(2, base + timedelta(hours=1), "DEV1"),      # 09:00 OUT
        Punch(3, base + timedelta(hours=7), "DEV1"),      # 15:00 IN
        Punch(4, base + timedelta(hours=9), "DEV1"),      # 17:00 OUT
    ]
