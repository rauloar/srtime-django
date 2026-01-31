"""
Standalone test runner for Flexible Engine tests.
Run this script directly without pytest dependency.
"""
import sys
sys.path.insert(0, 'c:/Proyectos/srtime-django')

from datetime import datetime, date, timedelta

from core.domain.flexible import Punch, FlexPolicy, FlexStatus, Confidence

# Import engine directly
import importlib.util
spec = importlib.util.spec_from_file_location(
    'flexible_engine', 
    'core/services/flexible_engine.py'
)
engine_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine_module)
calculate_flexible_day = engine_module.calculate_flexible_day


# Test fixtures
BASE_DATE = date(2025, 1, 15)
HOLIDAY_DATE = date(2025, 1, 1)
HOLIDAYS = [date(2025, 1, 1), date(2025, 5, 1), date(2025, 12, 25)]
POLICY = FlexPolicy()


def make_punches(base_date: date, *hours: int) -> list:
    """Create punches from hour values."""
    base = datetime.combine(base_date, datetime.min.time())
    punches = []
    for i, h in enumerate(hours, 1):
        punches.append(Punch(i, base + timedelta(hours=h), "DEV1"))
    return punches


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


def test_suite():
    """Run all tests."""
    print("=" * 60)
    print("FLEXIBLE ENGINE TEST SUITE")
    print("=" * 60)

    # Test data
    NORMAL_DAY = make_punches(BASE_DATE, 8, 12, 13, 17)
    OVERTIME_DAY = make_punches(BASE_DATE, 8, 18)
    EXCESSIVE_DAY = make_punches(BASE_DATE, 6, 20)
    NIGHT_SHIFT = make_punches(BASE_DATE, 22, 30)
    ORPHAN_PUNCH = make_punches(BASE_DATE, 8)
    HOLIDAY_WORK = make_punches(HOLIDAY_DATE, 8, 12)

    # =========================================================================
    print("\n[1] NORMAL DAY TESTS")
    # =========================================================================
    
    result = calculate_flexible_day(1, BASE_DATE, NORMAL_DAY, POLICY, HOLIDAYS, False)
    
    test("worked_minutes == 480", result.worked_minutes == 480, result.worked_minutes, 480)
    test("break_minutes == 30", result.break_minutes == 30, result.break_minutes, 30)
    test("net_worked == 450", result.net_worked_minutes == 450, result.net_worked_minutes, 450)
    test("status == Worked", result.status == FlexStatus.WORKED.value, result.status, "Worked")
    test("overtime == 0", result.overtime_minutes == 0, result.overtime_minutes, 0)
    test("confidence == HIGH", result.calculation_confidence == Confidence.HIGH)
    test("requires_review == False", result.requires_review is False)

    # =========================================================================
    print("\n[2] OVERTIME TESTS")
    # =========================================================================
    
    result = calculate_flexible_day(1, BASE_DATE, OVERTIME_DAY, POLICY, HOLIDAYS, False)
    
    test("overtime > 0", result.overtime_minutes > 0, result.overtime_minutes, "> 0")
    test("regular + overtime == net", 
         result.regular_minutes + result.overtime_minutes == result.net_worked_minutes,
         f"{result.regular_minutes} + {result.overtime_minutes}",
         result.net_worked_minutes)

    # =========================================================================
    print("\n[3] EXCESSIVE SHIFT TESTS")
    # =========================================================================
    
    result = calculate_flexible_day(1, BASE_DATE, EXCESSIVE_DAY, POLICY, HOLIDAYS, False)
    
    test("exceeded_daily_limit == True", result.exceeded_daily_limit is True)
    test("requires_review == True", result.requires_review is True)
    test("status == Excessive", result.status == FlexStatus.EXCESSIVE.value, result.status, "Excessive")

    # =========================================================================
    print("\n[4] NIGHT SHIFT TESTS")
    # =========================================================================
    
    result = calculate_flexible_day(1, BASE_DATE, NIGHT_SHIFT, POLICY, HOLIDAYS, False)
    
    test("night_minutes > 0", result.night_minutes > 0, result.night_minutes, "> 0")
    test("night_minutes >= 240", result.night_minutes >= 240, result.night_minutes, ">= 240")

    # =========================================================================
    print("\n[5] ORPHAN PUNCH TESTS")
    # =========================================================================
    
    result = calculate_flexible_day(1, BASE_DATE, ORPHAN_PUNCH, POLICY, HOLIDAYS, False)
    
    test("status == Incomplete", result.status == FlexStatus.INCOMPLETE.value, result.status, "Incomplete")
    test("requires_review == True", result.requires_review is True)
    test("has_orphan_punch == True", result.has_orphan_punch is True)
    test("worked_minutes == 0", result.worked_minutes == 0, result.worked_minutes, 0)

    # =========================================================================
    print("\n[6] HOLIDAY WORK TESTS")
    # =========================================================================
    
    result = calculate_flexible_day(1, HOLIDAY_DATE, HOLIDAY_WORK, POLICY, HOLIDAYS, False)
    
    test("status == HolidayWorked", result.status == FlexStatus.HOLIDAY_WORKED.value, result.status, "HolidayWorked")
    test("is_holiday == True", result.is_holiday is True)

    # =========================================================================
    print("\n[7] MATHEMATICAL INVARIANTS")
    # =========================================================================
    
    for name, punches in [("normal", NORMAL_DAY), ("overtime", OVERTIME_DAY), ("excessive", EXCESSIVE_DAY)]:
        result = calculate_flexible_day(1, BASE_DATE, punches, POLICY, HOLIDAYS, False)
        
        test(f"[{name}] regular + overtime == net",
             result.regular_minutes + result.overtime_minutes == result.net_worked_minutes)
        
        test(f"[{name}] net <= worked",
             result.net_worked_minutes <= result.worked_minutes)
        
        test(f"[{name}] regular <= policy limit",
             result.regular_minutes <= POLICY.daily_regular_minutes)

    # =========================================================================
    print("\n[8] EDGE CASES")
    # =========================================================================
    
    # Empty punches
    result = calculate_flexible_day(1, BASE_DATE, [], POLICY, HOLIDAYS, False)
    test("empty → status == Absent", result.status == FlexStatus.ABSENT.value, result.status, "Absent")
    test("empty → worked == 0", result.worked_minutes == 0)
    
    # Leave takes precedence
    result = calculate_flexible_day(1, BASE_DATE, NORMAL_DAY, POLICY, HOLIDAYS, has_leave=True)
    test("leave → status == Leave", result.status == FlexStatus.LEAVE.value, result.status, "Leave")
    
    # Rest day
    result = calculate_flexible_day(1, BASE_DATE, [], POLICY, HOLIDAYS, False, is_rest_day=True)
    test("rest day → status == RestDay", result.status == FlexStatus.REST_DAY.value, result.status, "RestDay")
    
    # Mode and version
    result = calculate_flexible_day(1, BASE_DATE, NORMAL_DAY, POLICY, HOLIDAYS, False)
    test("mode == FLEXIBLE", result.calculation_mode == "FLEXIBLE")
    test("version starts with 2.", result.engine_version.startswith("2."))
    test("calculated_at is datetime", isinstance(result.calculated_at, datetime))
    test("to_dict() returns dict", isinstance(result.to_dict(), dict))

    # =========================================================================
    print("\n" + "=" * 60)
    print(f"RESULTS: {TestResults.passed} passed, {TestResults.failed} failed")
    print("=" * 60)
    
    if TestResults.errors:
        print("\nFAILURES:")
        for name, error in TestResults.errors:
            print(f"  - {name}: {error}")
    
    return TestResults.failed == 0


if __name__ == "__main__":
    success = test_suite()
    sys.exit(0 if success else 1)
