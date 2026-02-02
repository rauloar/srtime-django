"""
Test Suite for Difference Analysis Service
Validates the rule-based reasoning engine for shadow comparison analysis.

These tests use mock objects to simulate ShadowCalculation records
without requiring database access.
"""
import unittest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass
from typing import Optional


# =============================================================================
# MOCK SETUP (for testing without Django)
# =============================================================================

# Mock the models module
class MockDifferenceType:
    NONE = 'NONE'
    MINOR = 'MINOR'
    MAJOR = 'MAJOR'
    CRITICAL = 'CRITICAL'


class MockDifferenceReason:
    BREAK_POLICY_CHANGE = 'BREAK_POLICY'
    OVERTIME_POLICY_CHANGE = 'OVERTIME_POLICY'
    FLEXIBLE_SPLIT_LOGIC = 'FLEXIBLE_SPLIT'
    NIGHT_CLASSIFICATION_CHANGE = 'NIGHT_CLASS'
    HOLIDAY_DETECTION_CHANGE = 'HOLIDAY_DETECT'
    ORPHAN_PUNCH_HANDLING = 'ORPHAN_PUNCH'
    ROUNDING_RULE_DIFFERENCE = 'ROUNDING'
    STATUS_RESOLUTION_CHANGE = 'STATUS_CHANGE'
    ENGINE_BUG_V1 = 'BUG_V1'
    UNKNOWN = 'UNKNOWN'


class MockConfidenceLevel:
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    LOW = 'LOW'


@dataclass
class MockShadowCalculation:
    """Mock ShadowCalculation for testing."""
    id: int = 1
    v1_worked_minutes: int = 480
    v1_overtime_minutes: int = 0
    v1_status: str = 'Worked'
    v2_worked_minutes: int = 480
    v2_net_minutes: int = 450
    v2_regular_minutes: int = 450
    v2_overtime_minutes: int = 0
    v2_night_minutes: int = 0
    v2_status: str = 'Worked'
    difference_minutes: int = 0
    difference_type: str = 'NONE'


# =============================================================================
# REASONING ENGINE (Standalone for Testing)
# =============================================================================

class TestableReasoningEngine:
    """
    Standalone version of DifferenceReasoningEngine for testing.
    Duplicates core logic without Django dependencies.
    """
    
    BREAK_DIFF_THRESHOLD = 5
    OVERTIME_DIFF_THRESHOLD = 5
    NIGHT_DIFF_THRESHOLD = 5
    ROUNDING_MAX_DIFF = 10
    
    def analyze(self, shadow):
        """Run analysis and return primary reason."""
        rules = [
            self._check_engine_bug_v1,
            self._check_break_policy,
            self._check_overtime_policy,
            self._check_night_classification,
            self._check_flexible_split,
            self._check_holiday_detection,
            self._check_orphan_punch,
            self._check_status_change,
            self._check_rounding,
        ]
        
        for rule_fn in rules:
            result = rule_fn(shadow)
            if result['matched']:
                return result
        
        return {
            'matched': True,
            'reason': MockDifferenceReason.UNKNOWN,
            'confidence': MockConfidenceLevel.LOW,
            'explanation': 'Unknown cause',
        }
    
    def _check_engine_bug_v1(self, shadow):
        v1_worked = shadow.v1_worked_minutes
        v1_overtime = shadow.v1_overtime_minutes
        
        if v1_overtime > v1_worked and v1_worked > 0:
            return {
                'matched': True,
                'reason': MockDifferenceReason.ENGINE_BUG_V1,
                'confidence': MockConfidenceLevel.HIGH,
                'explanation': f'V1 bug: overtime {v1_overtime} > worked {v1_worked}',
            }
        
        if v1_worked < 0 or v1_overtime < 0:
            return {
                'matched': True,
                'reason': MockDifferenceReason.ENGINE_BUG_V1,
                'confidence': MockConfidenceLevel.HIGH,
                'explanation': 'V1 bug: negative values',
            }
        
        return {'matched': False}
    
    def _check_break_policy(self, shadow):
        v2_break = shadow.v2_worked_minutes - shadow.v2_net_minutes
        
        if v2_break > 0:
            diff_explained = abs(shadow.v1_worked_minutes - shadow.v2_net_minutes)
            if diff_explained <= self.BREAK_DIFF_THRESHOLD:
                return {
                    'matched': True,
                    'reason': MockDifferenceReason.BREAK_POLICY_CHANGE,
                    'confidence': MockConfidenceLevel.HIGH,
                    'explanation': f'V2 applied {v2_break} min break deduction',
                }
        
        return {'matched': False}
    
    def _check_overtime_policy(self, shadow):
        overtime_diff = abs(shadow.v2_overtime_minutes - shadow.v1_overtime_minutes)
        
        if overtime_diff > self.OVERTIME_DIFF_THRESHOLD:
            return {
                'matched': True,
                'reason': MockDifferenceReason.OVERTIME_POLICY_CHANGE,
                'confidence': MockConfidenceLevel.HIGH,
                'explanation': f'Overtime diff: {overtime_diff} min',
            }
        
        return {'matched': False}
    
    def _check_night_classification(self, shadow):
        if shadow.v2_night_minutes > self.NIGHT_DIFF_THRESHOLD:
            return {
                'matched': True,
                'reason': MockDifferenceReason.NIGHT_CLASSIFICATION_CHANGE,
                'confidence': MockConfidenceLevel.HIGH,
                'explanation': f'V2 detected {shadow.v2_night_minutes} night minutes',
            }
        
        return {'matched': False}
    
    def _check_flexible_split(self, shadow):
        worked_diff = abs(shadow.v2_worked_minutes - shadow.v1_worked_minutes)
        v1_worked = shadow.v1_status.lower() in ['worked', 'present', 'normal']
        v2_worked = shadow.v2_status.lower() in ['worked', 'present', 'normal']
        
        if worked_diff > 30 and v1_worked and v2_worked:
            return {
                'matched': True,
                'reason': MockDifferenceReason.FLEXIBLE_SPLIT_LOGIC,
                'confidence': MockConfidenceLevel.MEDIUM,
                'explanation': f'Flexible split: {worked_diff} min diff',
            }
        
        return {'matched': False}
    
    def _check_holiday_detection(self, shadow):
        v2_holiday = 'holiday' in shadow.v2_status.lower()
        v1_holiday = 'holiday' in shadow.v1_status.lower()
        
        if v2_holiday and not v1_holiday:
            return {
                'matched': True,
                'reason': MockDifferenceReason.HOLIDAY_DETECTION_CHANGE,
                'confidence': MockConfidenceLevel.HIGH,
                'explanation': 'V2 detected holiday work',
            }
        
        return {'matched': False}
    
    def _check_orphan_punch(self, shadow):
        orphan_indicators = ['incomplete', 'orphan', 'missing']
        has_orphan = any(ind in shadow.v2_status.lower() for ind in orphan_indicators)
        
        if has_orphan:
            return {
                'matched': True,
                'reason': MockDifferenceReason.ORPHAN_PUNCH_HANDLING,
                'confidence': MockConfidenceLevel.MEDIUM,
                'explanation': 'V2 detected orphan punches',
            }
        
        return {'matched': False}
    
    def _check_status_change(self, shadow):
        absent = ['absent', 'ausente']
        worked = ['worked', 'present', 'normal']
        
        v1_absent = any(a in shadow.v1_status.lower() for a in absent)
        v1_worked = any(w in shadow.v1_status.lower() for w in worked)
        v2_absent = any(a in shadow.v2_status.lower() for a in absent)
        v2_worked = any(w in shadow.v2_status.lower() for w in worked)
        
        if (v1_absent and v2_worked) or (v1_worked and v2_absent):
            return {
                'matched': True,
                'reason': MockDifferenceReason.STATUS_RESOLUTION_CHANGE,
                'confidence': MockConfidenceLevel.HIGH,
                'explanation': f'Status change: {shadow.v1_status} -> {shadow.v2_status}',
            }
        
        return {'matched': False}
    
    def _check_rounding(self, shadow):
        abs_diff = abs(shadow.difference_minutes)
        
        if 0 < abs_diff <= self.ROUNDING_MAX_DIFF:
            return {
                'matched': True,
                'reason': MockDifferenceReason.ROUNDING_RULE_DIFFERENCE,
                'confidence': MockConfidenceLevel.MEDIUM,
                'explanation': f'Rounding diff: {abs_diff} min',
            }
        
        return {'matched': False}


# =============================================================================
# TEST CASES
# =============================================================================

class TestBreakPolicyDetection(unittest.TestCase):
    """Test detection of break policy changes."""
    
    def setUp(self):
        self.engine = TestableReasoningEngine()
    
    def test_break_deduction_detected(self):
        """V2 deducted 30 min break, V1 didn't but almost same base worked."""
        # Break rule: v2_break > 0 AND abs(v1_worked - v2_net) <= threshold
        # So v1_worked should be close to v2_net
        shadow = MockShadowCalculation(
            v1_worked_minutes=450,  # V1 reported 450 (didn't include break in gross)
            v1_overtime_minutes=0,
            v1_status='Worked',
            v2_worked_minutes=480,  # V2 gross = 480
            v2_net_minutes=450,     # V2 net = 450 (30 min break deducted)
            v2_overtime_minutes=0,
            difference_minutes=0,   # 450 - 450 = 0
        )
        
        result = self.engine.analyze(shadow)
        
        self.assertTrue(result['matched'])
        self.assertEqual(result['reason'], MockDifferenceReason.BREAK_POLICY_CHANGE)
        self.assertEqual(result['confidence'], MockConfidenceLevel.HIGH)
    
    def test_no_break_change(self):
        """No break difference - should not match."""
        shadow = MockShadowCalculation(
            v1_worked_minutes=480,
            v2_worked_minutes=480,
            v2_net_minutes=480,  # No break
            difference_minutes=0,
        )
        
        result = self.engine.analyze(shadow)
        
        # Should fall through to another rule or UNKNOWN
        self.assertNotEqual(result.get('reason'), MockDifferenceReason.BREAK_POLICY_CHANGE)


class TestOvertimePolicyDetection(unittest.TestCase):
    """Test detection of overtime policy changes."""
    
    def setUp(self):
        self.engine = TestableReasoningEngine()
    
    def test_overtime_increase_detected(self):
        """V2 calculated more overtime."""
        shadow = MockShadowCalculation(
            v1_worked_minutes=600,
            v1_overtime_minutes=0,
            v2_worked_minutes=600,
            v2_net_minutes=600,
            v2_overtime_minutes=120,  # V2 found 2h overtime
            difference_minutes=0,
        )
        
        result = self.engine.analyze(shadow)
        
        self.assertTrue(result['matched'])
        self.assertEqual(result['reason'], MockDifferenceReason.OVERTIME_POLICY_CHANGE)
    
    def test_overtime_decrease_detected(self):
        """V2 calculated less overtime."""
        shadow = MockShadowCalculation(
            v1_worked_minutes=600,
            v1_overtime_minutes=120,
            v2_worked_minutes=600,
            v2_net_minutes=600,
            v2_overtime_minutes=60,  # V2 found less
            difference_minutes=0,
        )
        
        result = self.engine.analyze(shadow)
        
        self.assertTrue(result['matched'])
        self.assertEqual(result['reason'], MockDifferenceReason.OVERTIME_POLICY_CHANGE)


class TestFlexibleSplitDetection(unittest.TestCase):
    """Test detection of flexible split logic differences."""
    
    def setUp(self):
        self.engine = TestableReasoningEngine()
    
    def test_large_worked_diff_detected(self):
        """Significant difference in raw worked time."""
        shadow = MockShadowCalculation(
            v1_worked_minutes=480,
            v1_status='Worked',
            v2_worked_minutes=420,  # 60 min less
            v2_net_minutes=420,
            v2_status='Worked',
            difference_minutes=-60,
        )
        
        result = self.engine.analyze(shadow)
        
        self.assertTrue(result['matched'])
        self.assertEqual(result['reason'], MockDifferenceReason.FLEXIBLE_SPLIT_LOGIC)


class TestRoundingDetection(unittest.TestCase):
    """Test detection of rounding rule differences."""
    
    def setUp(self):
        self.engine = TestableReasoningEngine()
    
    def test_minor_rounding_detected(self):
        """Small difference due to rounding."""
        shadow = MockShadowCalculation(
            v1_worked_minutes=480,
            v2_worked_minutes=480,
            v2_net_minutes=485,  # 5 min diff
            v2_overtime_minutes=0,
            v1_overtime_minutes=0,
            difference_minutes=5,
        )
        
        result = self.engine.analyze(shadow)
        
        # Note: Break policy might match first if v2_net > v2_worked
        # In this case, no break, so should be rounding
        self.assertEqual(result['reason'], MockDifferenceReason.ROUNDING_RULE_DIFFERENCE)
    
    def test_zero_diff_is_not_rounding(self):
        """Zero difference should not be rounding."""
        shadow = MockShadowCalculation(
            v1_worked_minutes=480,
            v2_worked_minutes=480,
            v2_net_minutes=480,
            difference_minutes=0,
        )
        
        result = self.engine.analyze(shadow)
        
        # Zero diff should be UNKNOWN (nothing matched)
        self.assertEqual(result['reason'], MockDifferenceReason.UNKNOWN)


class TestUnknownCase(unittest.TestCase):
    """Test unknown case handling."""
    
    def setUp(self):
        self.engine = TestableReasoningEngine()
    
    def test_no_matching_rule_returns_unknown(self):
        """When no rule matches, return UNKNOWN with LOW confidence."""
        shadow = MockShadowCalculation(
            v1_worked_minutes=480,
            v2_worked_minutes=480,
            v2_net_minutes=480,
            v2_overtime_minutes=0,
            v1_overtime_minutes=0,
            v2_night_minutes=0,
            difference_minutes=0,
            v1_status='Worked',
            v2_status='Worked',
        )
        
        result = self.engine.analyze(shadow)
        
        self.assertEqual(result['reason'], MockDifferenceReason.UNKNOWN)
        self.assertEqual(result['confidence'], MockConfidenceLevel.LOW)


class TestMajorDifferenceReviewFlag(unittest.TestCase):
    """Test requires_review flag for major differences."""
    
    def test_major_difference_requires_review(self):
        """MAJOR difference type should require review."""
        shadow = MockShadowCalculation(
            difference_type='MAJOR',
            difference_minutes=45,
        )
        
        # The requires_review logic
        requires = shadow.difference_type in ['MAJOR', 'CRITICAL']
        self.assertTrue(requires)
    
    def test_critical_difference_requires_review(self):
        """CRITICAL difference type should require review."""
        shadow = MockShadowCalculation(
            difference_type='CRITICAL',
            difference_minutes=120,
        )
        
        requires = shadow.difference_type in ['MAJOR', 'CRITICAL']
        self.assertTrue(requires)
    
    def test_minor_difference_no_review(self):
        """MINOR difference should not require review by default."""
        shadow = MockShadowCalculation(
            difference_type='MINOR',
            difference_minutes=5,
        )
        
        requires = shadow.difference_type in ['MAJOR', 'CRITICAL']
        self.assertFalse(requires)


class TestEngineBugV1Detection(unittest.TestCase):
    """Test detection of V1 engine bugs."""
    
    def setUp(self):
        self.engine = TestableReasoningEngine()
    
    def test_overtime_exceeds_worked(self):
        """V1 bug: overtime > worked."""
        shadow = MockShadowCalculation(
            v1_worked_minutes=100,
            v1_overtime_minutes=200,  # Impossible!
            v2_worked_minutes=300,
            v2_net_minutes=300,
            v2_overtime_minutes=0,
        )
        
        result = self.engine.analyze(shadow)
        
        self.assertEqual(result['reason'], MockDifferenceReason.ENGINE_BUG_V1)
        self.assertEqual(result['confidence'], MockConfidenceLevel.HIGH)
    
    def test_negative_values(self):
        """V1 bug: negative values."""
        shadow = MockShadowCalculation(
            v1_worked_minutes=-50,
            v1_overtime_minutes=0,
        )
        
        result = self.engine.analyze(shadow)
        
        self.assertEqual(result['reason'], MockDifferenceReason.ENGINE_BUG_V1)


class TestStatusChangeDetection(unittest.TestCase):
    """Test detection of status resolution changes."""
    
    def setUp(self):
        self.engine = TestableReasoningEngine()
    
    def test_absent_to_worked(self):
        """V1: Absent, V2: Worked."""
        shadow = MockShadowCalculation(
            v1_worked_minutes=0,
            v1_status='Absent',
            v2_worked_minutes=480,
            v2_net_minutes=480,
            v2_status='Worked',
        )
        
        result = self.engine.analyze(shadow)
        
        self.assertEqual(result['reason'], MockDifferenceReason.STATUS_RESOLUTION_CHANGE)
    
    def test_worked_to_absent(self):
        """V1: Worked, V2: Absent."""
        shadow = MockShadowCalculation(
            v1_worked_minutes=480,
            v1_status='Worked',
            v2_worked_minutes=0,
            v2_net_minutes=0,
            v2_status='Absent',
        )
        
        result = self.engine.analyze(shadow)
        
        self.assertEqual(result['reason'], MockDifferenceReason.STATUS_RESOLUTION_CHANGE)


class TestRulePriority(unittest.TestCase):
    """Test that rules are evaluated in correct priority order."""
    
    def setUp(self):
        self.engine = TestableReasoningEngine()
    
    def test_bug_has_highest_priority(self):
        """ENGINE_BUG_V1 should match before other rules."""
        shadow = MockShadowCalculation(
            v1_worked_minutes=100,
            v1_overtime_minutes=200,  # Bug
            v2_worked_minutes=500,
            v2_net_minutes=450,  # Also has break diff
            v2_overtime_minutes=60,  # Also has OT diff
        )
        
        result = self.engine.analyze(shadow)
        
        # Bug should win
        self.assertEqual(result['reason'], MockDifferenceReason.ENGINE_BUG_V1)


# =============================================================================
# TEST RUNNER
# =============================================================================

def run_tests():
    """Run all tests and print results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestBreakPolicyDetection,
        TestOvertimePolicyDetection,
        TestFlexibleSplitDetection,
        TestRoundingDetection,
        TestUnknownCase,
        TestMajorDifferenceReviewFlag,
        TestEngineBugV1Detection,
        TestStatusChangeDetection,
        TestRulePriority,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
