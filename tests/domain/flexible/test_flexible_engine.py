"""
Tests for the Flexible Engine Orchestrator.
Tests the full calculate_flexible_day() pipeline.
"""
import pytest
from datetime import date, datetime

from core.domain.flexible import FlexStatus, Confidence


# Import engine directly to avoid services __init__ issues
import importlib.util
spec = importlib.util.spec_from_file_location(
    'flexible_engine', 
    'core/services/flexible_engine.py'
)
engine_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine_module)
calculate_flexible_day = engine_module.calculate_flexible_day


class TestNormalDay:
    """Tests for normal 8-hour work day."""
    
    def test_worked_minutes(self, normal_day_punches, base_date, default_policy, holidays):
        """Verify gross worked minutes calculation."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=normal_day_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.worked_minutes == 480
    
    def test_break_deduction(self, normal_day_punches, base_date, default_policy, holidays):
        """Verify break minutes are deducted."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=normal_day_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.break_minutes == 30
    
    def test_net_worked(self, normal_day_punches, base_date, default_policy, holidays):
        """Verify net worked = worked - breaks."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=normal_day_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.net_worked_minutes == 450
        assert result.net_worked_minutes == result.worked_minutes - result.break_minutes
    
    def test_status_worked(self, normal_day_punches, base_date, default_policy, holidays):
        """Verify status is 'Worked' for normal day."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=normal_day_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.status == FlexStatus.WORKED.value
    
    def test_no_overtime(self, normal_day_punches, base_date, default_policy, holidays):
        """Verify no overtime for normal 8-hour day."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=normal_day_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.overtime_minutes == 0
    
    def test_high_confidence(self, normal_day_punches, base_date, default_policy, holidays):
        """Verify high confidence for clean data."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=normal_day_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.calculation_confidence == Confidence.HIGH
    
    def test_no_review_required(self, normal_day_punches, base_date, default_policy, holidays):
        """Verify no review required for normal day."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=normal_day_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.requires_review is False


class TestOvertime:
    """Tests for overtime calculation."""
    
    def test_overtime_detected(self, overtime_punches, base_date, default_policy, holidays):
        """Verify overtime is calculated for 10-hour day."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=overtime_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.overtime_minutes > 0
    
    def test_overtime_amount(self, overtime_punches, base_date, default_policy, holidays):
        """Verify correct overtime amount."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=overtime_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        # 10 hours = 600 min, minus breaks
        # net = 600 - 45 = 555 (two break thresholds)
        # overtime = 555 - 480 = 75
        assert result.overtime_minutes == result.net_worked_minutes - default_policy.daily_regular_minutes


class TestExcessiveShift:
    """Tests for excessive work hours (legal violation)."""
    
    def test_excessive_flag(self, excessive_punches, base_date, default_policy, holidays):
        """Verify is_excessive flag for 14-hour day."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=excessive_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.exceeded_daily_limit is True
    
    def test_requires_review(self, excessive_punches, base_date, default_policy, holidays):
        """Verify review is required for excessive shift."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=excessive_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.requires_review is True
    
    def test_status_excessive(self, excessive_punches, base_date, default_policy, holidays):
        """Verify status is 'Excessive' for excessive day."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=excessive_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.status == FlexStatus.EXCESSIVE.value


class TestNightShift:
    """Tests for night work calculation."""
    
    def test_night_minutes_calculated(self, night_shift_punches, base_date, default_policy, holidays):
        """Verify night minutes are calculated for overnight shift."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=night_shift_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        # 22:00-06:00 = 8 hours within night range (22:00-06:00)
        assert result.night_minutes >= 240  # At least 4 hours of night work


class TestOrphanPunch:
    """Tests for incomplete block (orphan punch)."""
    
    def test_status_incomplete(self, orphan_punch, base_date, default_policy, holidays):
        """Verify status is 'Incomplete' for orphan punch."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=orphan_punch,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.status == FlexStatus.INCOMPLETE.value
    
    def test_requires_review(self, orphan_punch, base_date, default_policy, holidays):
        """Verify review is required for orphan punch."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=orphan_punch,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.requires_review is True
    
    def test_has_orphan_flag(self, orphan_punch, base_date, default_policy, holidays):
        """Verify has_orphan_punch flag is set."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=orphan_punch,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.has_orphan_punch is True
    
    def test_zero_worked(self, orphan_punch, base_date, default_policy, holidays):
        """Verify zero worked time for incomplete blocks."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=orphan_punch,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.worked_minutes == 0


class TestHolidayWork:
    """Tests for work on holiday."""
    
    def test_status_holiday_worked(self, holiday_work_punches, holiday_date, default_policy, holidays):
        """Verify status is 'HolidayWorked' for work on holiday."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=holiday_date,
            punches=holiday_work_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.status == FlexStatus.HOLIDAY_WORKED.value
    
    def test_is_holiday_flag(self, holiday_work_punches, holiday_date, default_policy, holidays):
        """Verify is_holiday flag is set."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=holiday_date,
            punches=holiday_work_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.is_holiday is True


class TestMathematicalInvariants:
    """Tests for mathematical invariants that must always hold."""
    
    def test_regular_plus_overtime_equals_net(self, normal_day_punches, base_date, default_policy, holidays):
        """Verify: regular + overtime == net_worked."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=normal_day_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.regular_minutes + result.overtime_minutes == result.net_worked_minutes
    
    def test_regular_overtime_invariant_overtime_day(self, overtime_punches, base_date, default_policy, holidays):
        """Verify invariant holds for overtime day."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=overtime_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.regular_minutes + result.overtime_minutes == result.net_worked_minutes
    
    def test_net_worked_less_equal_worked(self, normal_day_punches, base_date, default_policy, holidays):
        """Verify: net_worked <= worked."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=normal_day_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.net_worked_minutes <= result.worked_minutes
    
    def test_night_minutes_less_equal_net(self, night_shift_punches, base_date, default_policy, holidays):
        """Verify: night_minutes <= net_worked."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=night_shift_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.night_minutes <= result.net_worked_minutes
    
    def test_regular_never_exceeds_policy_limit(self, excessive_punches, base_date, default_policy, holidays):
        """Verify: regular_minutes <= policy.daily_regular_minutes."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=excessive_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.regular_minutes <= default_policy.daily_regular_minutes


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_empty_punches(self, empty_punches, base_date, default_policy, holidays):
        """Verify handling of no punches."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=empty_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.status == FlexStatus.ABSENT.value
        assert result.worked_minutes == 0
        assert result.net_worked_minutes == 0
    
    def test_long_gap_detected(self, long_gap_punches, base_date, default_policy, holidays):
        """Verify handling of long gaps between blocks."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=long_gap_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        # Should still calculate worked time
        assert result.worked_minutes > 0
        assert result.blocks_count == 2
    
    def test_leave_takes_precedence(self, normal_day_punches, base_date, default_policy, holidays):
        """Verify leave status takes precedence over work."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=normal_day_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=True,  # Has leave
        )
        assert result.status == FlexStatus.LEAVE.value
    
    def test_rest_day_with_no_punches(self, empty_punches, base_date, default_policy, holidays):
        """Verify rest day status when no punches and marked as rest day."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=empty_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
            is_rest_day=True,
        )
        assert result.status == FlexStatus.REST_DAY.value
    
    def test_calculation_mode_is_flexible(self, normal_day_punches, base_date, default_policy, holidays):
        """Verify calculation_mode is always 'FLEXIBLE'."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=normal_day_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.calculation_mode == "FLEXIBLE"
    
    def test_engine_version_present(self, normal_day_punches, base_date, default_policy, holidays):
        """Verify engine version is recorded."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=normal_day_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.engine_version is not None
        assert result.engine_version.startswith("2.")
    
    def test_calculated_at_timestamp(self, normal_day_punches, base_date, default_policy, holidays):
        """Verify calculated_at timestamp is set."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=normal_day_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        assert result.calculated_at is not None
        assert isinstance(result.calculated_at, datetime)


class TestResultSerialization:
    """Tests for result serialization."""
    
    def test_to_dict(self, normal_day_punches, base_date, default_policy, holidays):
        """Verify to_dict() returns valid dictionary."""
        result = calculate_flexible_day(
            employee_id=1,
            target_date=base_date,
            punches=normal_day_punches,
            policy=default_policy,
            holidays=holidays,
            has_leave=False,
        )
        data = result.to_dict()
        assert isinstance(data, dict)
        assert data["employee_id"] == 1
        assert data["calculation_mode"] == "FLEXIBLE"
        assert data["status"] == "Worked"
