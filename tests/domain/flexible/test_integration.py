"""
Integration tests for Attendance Engine V2.
Tests the Strategy pattern and processor integration.
"""
import sys
sys.path.insert(0, 'c:/Proyectos/srtime-django')

from datetime import datetime, date, timedelta
from dataclasses import dataclass
from typing import Optional

# Mock Django models for testing without DB
@dataclass
class MockLog:
    id: int
    timestamp: datetime
    punch: int
    device_id: str
    user_id: str = "TEST"


@dataclass
class MockTimetable:
    id: int = 1
    is_flexible: bool = False
    on_duty_time: Optional[datetime] = None
    off_duty_time: Optional[datetime] = None
    break_minutes: int = 30
    required_minutes: int = 480
    rounding_rule: Optional[str] = None
    late_allow_minutes: int = 0
    early_leave_allow_minutes: int = 0


# Import domain
from core.domain.flexible import FlexPolicy, Punch

# Import processors directly to avoid Django imports
import importlib.util

# Load flexible processor
spec = importlib.util.spec_from_file_location(
    'flexible_engine', 
    'core/services/flexible_engine.py'
)
flex_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(flex_module)
calculate_flexible_day = flex_module.calculate_flexible_day


class TestResults:
    passed = 0
    failed = 0
    errors = []


def test(name: str, condition: bool, actual=None, expected=None):
    """Run a single test assertion."""
    if condition:
        TestResults.passed += 1
        print(f"  ✓ {name}")
    else:
        TestResults.failed += 1
        msg = f"{actual} != {expected}" if actual is not None else "FAILED"
        TestResults.errors.append((name, msg))
        print(f"  ✗ {name}: {msg}")


def test_strategy_selection():
    """Test processor selection based on schedule type."""
    print("\n[1] STRATEGY SELECTION")
    
    # We can't import the full engine due to Django deps,
    # but we can verify the domain functions work correctly
    
    # Flexible scenario
    base = datetime(2025, 1, 15, 8, 0, 0)
    punches = [
        Punch(1, base, "DEV1"),
        Punch(2, base + timedelta(hours=4), "DEV1"),
        Punch(3, base + timedelta(hours=5), "DEV1"),
        Punch(4, base + timedelta(hours=9), "DEV1"),
    ]
    
    result = calculate_flexible_day(
        employee_id=1,
        target_date=date(2025, 1, 15),
        punches=punches,
        policy=FlexPolicy(),
        holidays=[],
        has_leave=False,
    )
    
    test("flexible mode detected", result.calculation_mode == "FLEXIBLE")
    test("worked minutes calculated", result.worked_minutes == 480)
    test("status is Worked", result.status == "Worked")


def test_processor_context_mapping():
    """Test that processor context correctly maps to domain."""
    print("\n[2] CONTEXT MAPPING")
    
    # Simulate logs to punches conversion
    logs = [
        MockLog(1, datetime(2025, 1, 15, 8, 0), punch=0, device_id="DEV1"),
        MockLog(2, datetime(2025, 1, 15, 12, 0), punch=1, device_id="DEV1"),
        MockLog(3, datetime(2025, 1, 15, 13, 0), punch=0, device_id="DEV1"),
        MockLog(4, datetime(2025, 1, 15, 17, 0), punch=1, device_id="DEV1"),
    ]
    
    # Convert manually (same logic as FlexibleProcessor)
    punches = []
    for log in logs:
        state = int(log.punch) if log.punch is not None else 0
        is_valid_punch = state in [0, 1, 4, 5, 8, 9]
        if is_valid_punch and log.timestamp:
            punch = Punch(
                id=log.id,
                timestamp=log.timestamp,
                device_id=str(log.device_id) if log.device_id else "UNKNOWN",
            )
            punches.append(punch)
    
    test("logs converted to punches", len(punches) == 4)
    test("punch ids preserved", all(p.id == l.id for p, l in zip(punches, logs)))
    test("timestamps preserved", all(p.timestamp == l.timestamp for p, l in zip(punches, logs)))


def test_result_contract():
    """Test that result contract is complete."""
    print("\n[3] RESULT CONTRACT")
    
    base = datetime(2025, 1, 15, 8, 0, 0)
    punches = [
        Punch(1, base, "DEV1"),
        Punch(2, base + timedelta(hours=9), "DEV1"),
    ]
    
    result = calculate_flexible_day(
        employee_id=123,
        target_date=date(2025, 1, 15),
        punches=punches,
        policy=FlexPolicy(),
        holidays=[],
        has_leave=False,
    )
    
    # Check all required fields exist
    test("has employee_id", hasattr(result, "employee_id") and result.employee_id == 123)
    test("has target_date", hasattr(result, "target_date"))
    test("has calculation_mode", hasattr(result, "calculation_mode"))
    test("has check_in", hasattr(result, "check_in"))
    test("has check_out", hasattr(result, "check_out"))
    test("has worked_minutes", hasattr(result, "worked_minutes"))
    test("has break_minutes", hasattr(result, "break_minutes"))
    test("has net_worked_minutes", hasattr(result, "net_worked_minutes"))
    test("has regular_minutes", hasattr(result, "regular_minutes"))
    test("has overtime_minutes", hasattr(result, "overtime_minutes"))
    test("has night_minutes", hasattr(result, "night_minutes"))
    test("has status", hasattr(result, "status"))
    test("has engine_version", hasattr(result, "engine_version"))
    test("has calculated_at", hasattr(result, "calculated_at"))
    test("has timetable_id", hasattr(result, "timetable_id"))
    test("has source_punches_count", hasattr(result, "source_punches_count"))


def test_backward_compatibility():
    """Test that V2 engine produces compatible results."""
    print("\n[4] BACKWARD COMPATIBILITY")
    
    # Normal day should produce standard status
    base = datetime(2025, 1, 15, 8, 0, 0)
    punches = [
        Punch(1, base, "DEV1"),
        Punch(2, base + timedelta(hours=4), "DEV1"),
        Punch(3, base + timedelta(hours=5), "DEV1"),
        Punch(4, base + timedelta(hours=9), "DEV1"),
    ]
    
    result = calculate_flexible_day(
        employee_id=1,
        target_date=date(2025, 1, 15),
        punches=punches,
        policy=FlexPolicy(),
        holidays=[],
        has_leave=False,
    )
    
    # Status should be in expected format
    test("status is string", isinstance(result.status, str))
    test("worked_minutes is int", isinstance(result.worked_minutes, int))
    test("overtime_minutes is int", isinstance(result.overtime_minutes, int))
    
    # Values should be reasonable
    test("worked > 0 for normal day", result.worked_minutes > 0)
    test("net_worked > 0 for normal day", result.net_worked_minutes > 0)


def run_integration_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("ATTENDANCE ENGINE V2 - INTEGRATION TESTS")
    print("=" * 60)
    
    test_strategy_selection()
    test_processor_context_mapping()
    test_result_contract()
    test_backward_compatibility()
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {TestResults.passed} passed, {TestResults.failed} failed")
    print("=" * 60)
    
    if TestResults.errors:
        print("\nFAILURES:")
        for name, error in TestResults.errors:
            print(f"  - {name}: {error}")
    
    return TestResults.failed == 0


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
