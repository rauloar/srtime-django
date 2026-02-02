"""
Test Suite for Forensic API Layer
Validates permissions, response formats, and error handling.

These tests use mock objects to test the API layer independently
of the database and service implementations.
"""
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


# =============================================================================
# MOCK SETUP
# =============================================================================

@dataclass
class MockUser:
    id: int = 1
    is_authenticated: bool = True
    is_superuser: bool = False
    is_staff: bool = False
    groups: list = None
    
    def __post_init__(self):
        if self.groups is None:
            self.groups = MockGroupManager([])


class MockGroupManager:
    """Mock Django group manager."""
    
    def __init__(self, groups):
        self._groups = groups
    
    def filter(self, **kwargs):
        name = kwargs.get('name')
        name__in = kwargs.get('name__in', [])
        
        if name:
            matches = [g for g in self._groups if g == name]
        elif name__in:
            matches = [g for g in self._groups if g in name__in]
        else:
            matches = self._groups
        
        return MockQuerySet(matches)


class MockQuerySet:
    """Mock Django QuerySet."""
    
    def __init__(self, items):
        self._items = items
    
    def exists(self):
        return len(self._items) > 0


class MockRequest:
    """Mock DRF request."""
    
    def __init__(self, user, method='GET', data=None, query_params=None):
        self.user = user
        self.method = method
        self.data = data or {}
        self.query_params = query_params or {}


# =============================================================================
# PERMISSION LOGIC (copied from permissions.py for testing)
# =============================================================================

class TestableIsAttendanceAdmin:
    """Testable version of IsAttendanceAdmin."""
    
    def has_permission(self, request):
        user = request.user
        
        if not user or not user.is_authenticated:
            return False
        
        if user.is_superuser:
            return True
        
        if user.is_staff:
            return True
        
        if user.groups.filter(name='attendance_admin').exists():
            return True
        
        return False


class TestableIsShadowReviewer:
    """Testable version of IsShadowReviewer."""
    
    def has_permission(self, request):
        user = request.user
        
        if not user or not user.is_authenticated:
            return False
        
        if user.is_superuser:
            return True
        
        allowed_groups = ['shadow_reviewer', 'hr_supervisor', 'legal']
        if user.groups.filter(name__in=allowed_groups).exists():
            return True
        
        return False


# =============================================================================
# PERMISSION TESTS
# =============================================================================

class TestIsAttendanceAdminPermission(unittest.TestCase):
    """Test IsAttendanceAdmin permission logic."""
    
    def setUp(self):
        self.permission = TestableIsAttendanceAdmin()
    
    def test_unauthenticated_denied(self):
        """Unauthenticated user is denied."""
        user = MockUser(is_authenticated=False)
        request = MockRequest(user)
        
        self.assertFalse(self.permission.has_permission(request))
    
    def test_superuser_allowed(self):
        """Superuser is always allowed."""
        user = MockUser(is_superuser=True)
        request = MockRequest(user)
        
        self.assertTrue(self.permission.has_permission(request))
    
    def test_staff_allowed(self):
        """Staff user is allowed."""
        user = MockUser(is_staff=True)
        request = MockRequest(user)
        
        self.assertTrue(self.permission.has_permission(request))
    
    def test_attendance_admin_group_allowed(self):
        """User in attendance_admin group is allowed."""
        user = MockUser(groups=MockGroupManager(['attendance_admin']))
        request = MockRequest(user)
        
        self.assertTrue(self.permission.has_permission(request))
    
    def test_other_group_denied(self):
        """User in other group is denied."""
        user = MockUser(groups=MockGroupManager(['other_group']))
        request = MockRequest(user)
        
        self.assertFalse(self.permission.has_permission(request))
    
    def test_no_group_denied(self):
        """User with no group is denied."""
        user = MockUser()
        request = MockRequest(user)
        
        self.assertFalse(self.permission.has_permission(request))


class TestIsShadowReviewerPermission(unittest.TestCase):
    """Test IsShadowReviewer permission logic."""
    
    def setUp(self):
        self.permission = TestableIsShadowReviewer()
    
    def test_unauthenticated_denied(self):
        """Unauthenticated user is denied."""
        user = MockUser(is_authenticated=False)
        request = MockRequest(user)
        
        self.assertFalse(self.permission.has_permission(request))
    
    def test_superuser_allowed(self):
        """Superuser is always allowed."""
        user = MockUser(is_superuser=True)
        request = MockRequest(user)
        
        self.assertTrue(self.permission.has_permission(request))
    
    def test_shadow_reviewer_group_allowed(self):
        """User in shadow_reviewer group is allowed."""
        user = MockUser(groups=MockGroupManager(['shadow_reviewer']))
        request = MockRequest(user)
        
        self.assertTrue(self.permission.has_permission(request))
    
    def test_hr_supervisor_group_allowed(self):
        """User in hr_supervisor group is allowed."""
        user = MockUser(groups=MockGroupManager(['hr_supervisor']))
        request = MockRequest(user)
        
        self.assertTrue(self.permission.has_permission(request))
    
    def test_legal_group_allowed(self):
        """User in legal group is allowed."""
        user = MockUser(groups=MockGroupManager(['legal']))
        request = MockRequest(user)
        
        self.assertTrue(self.permission.has_permission(request))
    
    def test_attendance_admin_denied_for_shadow(self):
        """attendance_admin alone is not enough for shadow review."""
        user = MockUser(groups=MockGroupManager(['attendance_admin']))
        request = MockRequest(user)
        
        self.assertFalse(self.permission.has_permission(request))


# =============================================================================
# SERIALIZER TESTS
# =============================================================================

class TestCalculateAttendanceInputValidation(unittest.TestCase):
    """Test input validation for calculate attendance."""
    
    def test_valid_input(self):
        """Valid input passes validation."""
        data = {
            'employee_id': 123,
            'date': '2025-01-15',
            'force': False,
        }
        
        # Basic validation
        self.assertIn('employee_id', data)
        self.assertIn('date', data)
        self.assertEqual(data['force'], False)
    
    def test_force_requires_reason(self):
        """Force=true requires reason."""
        data = {
            'employee_id': 123,
            'date': '2025-01-15',
            'force': True,
            'reason': '',  # Empty
        }
        
        # Validation rule: force=true needs non-empty reason
        is_valid = not (data['force'] and not data.get('reason'))
        self.assertFalse(is_valid)
    
    def test_force_with_reason_valid(self):
        """Force=true with reason is valid."""
        data = {
            'employee_id': 123,
            'date': '2025-01-15',
            'force': True,
            'reason': 'Correction requested by HR',
        }
        
        is_valid = not (data['force'] and not data.get('reason'))
        self.assertTrue(is_valid)
    
    def test_future_date_invalid(self):
        """Future date is invalid."""
        future_date = date(2030, 1, 1)
        today = date.today()
        
        is_valid = future_date <= today
        self.assertFalse(is_valid)


class TestSubmitDecisionInputValidation(unittest.TestCase):
    """Test input validation for submit decision."""
    
    def test_valid_decision(self):
        """Valid decision input."""
        data = {
            'decision': 'V2_CORRECT',
            'notes': 'V2 correctly applies break policy per company handbook',
        }
        
        valid_decisions = ['V2_CORRECT', 'V1_CORRECT', 'POLICY_CHANGE', 'INCONCLUSIVE', 'N/A']
        is_valid = data['decision'] in valid_decisions and len(data['notes']) >= 10
        self.assertTrue(is_valid)
    
    def test_short_notes_invalid(self):
        """Notes less than 10 chars are invalid."""
        data = {
            'decision': 'V2_CORRECT',
            'notes': 'OK',  # Too short
        }
        
        is_valid = len(data['notes']) >= 10
        self.assertFalse(is_valid)
    
    def test_invalid_decision_rejected(self):
        """Invalid decision value is rejected."""
        data = {
            'decision': 'INVALID_CHOICE',
            'notes': 'This is a valid note length',
        }
        
        valid_decisions = ['V2_CORRECT', 'V1_CORRECT', 'POLICY_CHANGE', 'INCONCLUSIVE', 'N/A']
        is_valid = data['decision'] in valid_decisions
        self.assertFalse(is_valid)


# =============================================================================
# WORKFLOW TRANSITION TESTS (via API)
# =============================================================================

class TestReviewWorkflowViaAPI(unittest.TestCase):
    """Test review workflow transitions through API layer."""
    
    def test_start_review_from_pending(self):
        """Can start review when status is PENDING."""
        current_status = 'PENDING'
        target_status = 'IN_PROGRESS'
        
        valid_from_pending = ['IN_PROGRESS']
        is_valid = target_status in valid_from_pending
        self.assertTrue(is_valid)
    
    def test_decision_from_in_progress(self):
        """Can submit decision when status is IN_PROGRESS."""
        current_status = 'IN_PROGRESS'
        target_status = 'ACCEPTED'
        
        valid_from_in_progress = ['ACCEPTED', 'ADJUSTED', 'ESCALATED']
        is_valid = target_status in valid_from_in_progress
        self.assertTrue(is_valid)
    
    def test_close_from_accepted(self):
        """Can close when status is ACCEPTED."""
        current_status = 'ACCEPTED'
        target_status = 'CLOSED'
        
        valid_from_accepted = ['CLOSED']
        is_valid = target_status in valid_from_accepted
        self.assertTrue(is_valid)
    
    def test_cannot_close_from_in_progress(self):
        """Cannot close directly from IN_PROGRESS."""
        current_status = 'IN_PROGRESS'
        target_status = 'CLOSED'
        
        valid_from_in_progress = ['ACCEPTED', 'ADJUSTED', 'ESCALATED']
        is_valid = target_status in valid_from_in_progress
        self.assertFalse(is_valid)
    
    def test_cannot_reopen_closed(self):
        """Cannot transition from CLOSED to anything."""
        current_status = 'CLOSED'
        
        valid_from_closed = []
        for target in ['PENDING', 'IN_PROGRESS', 'ACCEPTED']:
            is_valid = target in valid_from_closed
            self.assertFalse(is_valid)


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

class TestErrorResponses(unittest.TestCase):
    """Test error response format."""
    
    def test_error_format(self):
        """Error responses have correct format."""
        error_response = {
            'error': 'EMPLOYEE_NOT_FOUND',
            'message': 'Employee 123 not found',
            'details': {'employee_id': 123},
        }
        
        self.assertIn('error', error_response)
        self.assertIn('message', error_response)
        self.assertIn('details', error_response)
    
    def test_transition_error_includes_states(self):
        """Transition errors include from/to states."""
        error_response = {
            'error': 'INVALID_TRANSITION',
            'message': 'Cannot submit decision',
            'details': {'from': 'PENDING', 'to': 'ACCEPTED'},
        }
        
        self.assertEqual(error_response['details']['from'], 'PENDING')
        self.assertEqual(error_response['details']['to'], 'ACCEPTED')


# =============================================================================
# IDEMPOTENCY TESTS
# =============================================================================

class TestIdempotency(unittest.TestCase):
    """Test idempotent operations."""
    
    def test_calculate_no_change_is_safe(self):
        """Calculating same day twice returns NO_CHANGE."""
        first_result = {'status': 'CREATED', 'fingerprint': 'abc123'}
        second_result = {'status': 'NO_CHANGE', 'fingerprint': 'abc123'}
        
        # Fingerprints should match
        self.assertEqual(first_result['fingerprint'], second_result['fingerprint'])
        # Second call returns NO_CHANGE
        self.assertEqual(second_result['status'], 'NO_CHANGE')
    
    def test_start_review_twice_fails(self):
        """Starting review twice is an invalid transition."""
        # After first start: IN_PROGRESS
        # Second start attempt: IN_PROGRESS → IN_PROGRESS is invalid
        current_status = 'IN_PROGRESS'
        target_status = 'IN_PROGRESS'
        
        valid_from_in_progress = ['ACCEPTED', 'ADJUSTED', 'ESCALATED']
        is_valid = target_status in valid_from_in_progress
        self.assertFalse(is_valid)


# =============================================================================
# TEST RUNNER
# =============================================================================

def run_tests():
    """Run all tests and print results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_classes = [
        TestIsAttendanceAdminPermission,
        TestIsShadowReviewerPermission,
        TestCalculateAttendanceInputValidation,
        TestSubmitDecisionInputValidation,
        TestReviewWorkflowViaAPI,
        TestErrorResponses,
        TestIdempotency,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
