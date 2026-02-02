"""
Test Suite for Shadow Review Workflow Service
Validates state machine transitions and audit logging.

These tests use mock objects to simulate the workflow
without requiring full Django database access.
"""
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


# =============================================================================
# MOCK SETUP
# =============================================================================

class MockReviewStatus:
    PENDING = 'PENDING'
    IN_PROGRESS = 'IN_PROGRESS'
    ACCEPTED = 'ACCEPTED'
    ADJUSTED = 'ADJUSTED'
    ESCALATED = 'ESCALATED'
    CLOSED = 'CLOSED'


class MockReviewDecision:
    V2_CORRECT = 'V2_CORRECT'
    V1_CORRECT = 'V1_CORRECT'
    POLICY_CHANGE_NEEDED = 'POLICY_CHANGE'
    INCONCLUSIVE = 'INCONCLUSIVE'


class MockConfidenceLevel:
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    LOW = 'LOW'


@dataclass
class MockUser:
    id: int = 1
    username: str = 'reviewer1'
    
    def __str__(self):
        return self.username


@dataclass
class MockAnalysis:
    id: int = 1


@dataclass
class MockReviewDecisionRecord:
    analysis_id: int = 1
    status: str = 'PENDING'
    reviewer: Optional[MockUser] = None
    reviewer_id: Optional[int] = None
    decision: Optional[str] = None
    decision_notes: Optional[str] = None
    started_at: Optional[datetime] = None
    decided_at: Optional[datetime] = None
    closed_by: Optional[MockUser] = None
    closed_at: Optional[datetime] = None
    confidence_override: Optional[str] = None
    
    def save(self):
        pass


# =============================================================================
# VALID TRANSITIONS MAP (copied from service)
# =============================================================================

VALID_TRANSITIONS = {
    'PENDING': ['IN_PROGRESS'],
    'IN_PROGRESS': ['ACCEPTED', 'ADJUSTED', 'ESCALATED'],
    'ACCEPTED': ['CLOSED'],
    'ADJUSTED': ['CLOSED'],
    'ESCALATED': ['CLOSED'],
    'CLOSED': [],
}


# =============================================================================
# TESTABLE STATE MACHINE
# =============================================================================

class InvalidShadowTransition(Exception):
    """Raised when an invalid state transition is attempted."""
    def __init__(self, from_status: str, to_status: str, reason: str = ""):
        self.from_status = from_status
        self.to_status = to_status
        super().__init__(f"Invalid: {from_status} → {to_status}")


class UnauthorizedReviewer(Exception):
    """Raised when wrong reviewer tries to act."""
    pass


class DecisionRequired(Exception):
    """Raised when decision notes are missing."""
    pass


class TestableWorkflowService:
    """
    Standalone version of ShadowReviewWorkflowService for testing.
    Tests the state machine logic without Django dependencies.
    """
    
    def __init__(self):
        self.audit_log = []
    
    def validate_transition(self, from_status: str, to_status: str) -> None:
        """Validate state transition."""
        valid = VALID_TRANSITIONS.get(from_status, [])
        if to_status not in valid:
            raise InvalidShadowTransition(from_status, to_status)
    
    def start_review(self, review: MockReviewDecisionRecord, reviewer: MockUser):
        """PENDING → IN_PROGRESS"""
        self.validate_transition(review.status, MockReviewStatus.IN_PROGRESS)
        
        previous = review.status
        review.status = MockReviewStatus.IN_PROGRESS
        review.reviewer = reviewer
        review.reviewer_id = reviewer.id
        review.started_at = datetime.now()
        
        self.audit_log.append({
            'action': 'SHADOW_REVIEW_STARTED',
            'previous': previous,
            'new': review.status,
            'actor': reviewer.id,
        })
        
        return review
    
    def submit_decision(
        self,
        review: MockReviewDecisionRecord,
        reviewer: MockUser,
        decision: str,
        notes: str,
    ):
        """IN_PROGRESS → ACCEPTED/ADJUSTED/ESCALATED"""
        # Validate reviewer
        if review.reviewer_id != reviewer.id:
            raise UnauthorizedReviewer()
        
        # Validate notes
        if not notes or not notes.strip():
            raise DecisionRequired()
        
        # Determine target status
        if decision in [MockReviewDecision.V2_CORRECT, MockReviewDecision.V1_CORRECT]:
            target = MockReviewStatus.ACCEPTED
        elif decision == MockReviewDecision.POLICY_CHANGE_NEEDED:
            target = MockReviewStatus.ADJUSTED
        else:
            target = MockReviewStatus.ESCALATED
        
        self.validate_transition(review.status, target)
        
        previous = review.status
        review.status = target
        review.decision = decision
        review.decision_notes = notes
        review.decided_at = datetime.now()
        
        self.audit_log.append({
            'action': 'SHADOW_REVIEW_DECIDED',
            'previous': previous,
            'new': review.status,
            'decision': decision,
            'actor': reviewer.id,
        })
        
        return review
    
    def close_case(self, review: MockReviewDecisionRecord, reviewer: MockUser):
        """ACCEPTED/ADJUSTED/ESCALATED → CLOSED"""
        self.validate_transition(review.status, MockReviewStatus.CLOSED)
        
        previous = review.status
        review.status = MockReviewStatus.CLOSED
        review.closed_by = reviewer
        review.closed_at = datetime.now()
        
        self.audit_log.append({
            'action': 'SHADOW_REVIEW_CLOSED',
            'previous': previous,
            'new': review.status,
            'actor': reviewer.id,
        })
        
        return review


# =============================================================================
# TEST CASES
# =============================================================================

class TestPendingToInProgress(unittest.TestCase):
    """Test PENDING → IN_PROGRESS transition."""
    
    def setUp(self):
        self.service = TestableWorkflowService()
        self.reviewer = MockUser(id=1, username='reviewer1')
    
    def test_pending_to_in_progress_ok(self):
        """Valid: PENDING → IN_PROGRESS."""
        review = MockReviewDecisionRecord(status='PENDING')
        
        result = self.service.start_review(review, self.reviewer)
        
        self.assertEqual(result.status, 'IN_PROGRESS')
        self.assertEqual(result.reviewer_id, 1)
        self.assertIsNotNone(result.started_at)
    
    def test_pending_to_accepted_fails(self):
        """Invalid: PENDING → ACCEPTED (skipping IN_PROGRESS)."""
        review = MockReviewDecisionRecord(status='PENDING')
        
        with self.assertRaises(InvalidShadowTransition) as ctx:
            self.service.validate_transition('PENDING', 'ACCEPTED')
        
        self.assertEqual(ctx.exception.from_status, 'PENDING')
        self.assertEqual(ctx.exception.to_status, 'ACCEPTED')


class TestInProgressToDecided(unittest.TestCase):
    """Test IN_PROGRESS → ACCEPTED/ADJUSTED/ESCALATED."""
    
    def setUp(self):
        self.service = TestableWorkflowService()
        self.reviewer = MockUser(id=1)
    
    def test_in_progress_to_accepted_ok(self):
        """Valid: IN_PROGRESS → ACCEPTED with V2_CORRECT."""
        review = MockReviewDecisionRecord(
            status='IN_PROGRESS',
            reviewer_id=1,
        )
        
        result = self.service.submit_decision(
            review, self.reviewer,
            decision=MockReviewDecision.V2_CORRECT,
            notes="V2 correctly applies break policy",
        )
        
        self.assertEqual(result.status, 'ACCEPTED')
        self.assertEqual(result.decision, MockReviewDecision.V2_CORRECT)
        self.assertIsNotNone(result.decided_at)
    
    def test_in_progress_to_adjusted_ok(self):
        """Valid: IN_PROGRESS → ADJUSTED with POLICY_CHANGE_NEEDED."""
        review = MockReviewDecisionRecord(
            status='IN_PROGRESS',
            reviewer_id=1,
        )
        
        result = self.service.submit_decision(
            review, self.reviewer,
            decision=MockReviewDecision.POLICY_CHANGE_NEEDED,
            notes="Need to update break policy configuration",
        )
        
        self.assertEqual(result.status, 'ADJUSTED')
    
    def test_in_progress_to_escalated_ok(self):
        """Valid: IN_PROGRESS → ESCALATED with INCONCLUSIVE."""
        review = MockReviewDecisionRecord(
            status='IN_PROGRESS',
            reviewer_id=1,
        )
        
        result = self.service.submit_decision(
            review, self.reviewer,
            decision=MockReviewDecision.INCONCLUSIVE,
            notes="Requires legal review due to complexity",
        )
        
        self.assertEqual(result.status, 'ESCALATED')


class TestWrongReviewer(unittest.TestCase):
    """Test that wrong reviewer cannot submit decision."""
    
    def setUp(self):
        self.service = TestableWorkflowService()
    
    def test_wrong_reviewer_fails(self):
        """Invalid: Different reviewer tries to decide."""
        original_reviewer = MockUser(id=1)
        wrong_reviewer = MockUser(id=2)
        
        review = MockReviewDecisionRecord(
            status='IN_PROGRESS',
            reviewer_id=1,  # Assigned to reviewer 1
        )
        
        with self.assertRaises(UnauthorizedReviewer):
            self.service.submit_decision(
                review, wrong_reviewer,
                decision=MockReviewDecision.V2_CORRECT,
                notes="Trying to submit",
            )


class TestDecisionNotesRequired(unittest.TestCase):
    """Test that decision notes are required."""
    
    def setUp(self):
        self.service = TestableWorkflowService()
        self.reviewer = MockUser(id=1)
    
    def test_empty_notes_fails(self):
        """Invalid: Empty notes."""
        review = MockReviewDecisionRecord(
            status='IN_PROGRESS',
            reviewer_id=1,
        )
        
        with self.assertRaises(DecisionRequired):
            self.service.submit_decision(
                review, self.reviewer,
                decision=MockReviewDecision.V2_CORRECT,
                notes="",
            )
    
    def test_whitespace_notes_fails(self):
        """Invalid: Whitespace-only notes."""
        review = MockReviewDecisionRecord(
            status='IN_PROGRESS',
            reviewer_id=1,
        )
        
        with self.assertRaises(DecisionRequired):
            self.service.submit_decision(
                review, self.reviewer,
                decision=MockReviewDecision.V2_CORRECT,
                notes="   ",
            )


class TestBackwardTransitions(unittest.TestCase):
    """Test that backward transitions are not allowed."""
    
    def setUp(self):
        self.service = TestableWorkflowService()
    
    def test_accepted_to_in_progress_fails(self):
        """Invalid: ACCEPTED → IN_PROGRESS (backward)."""
        with self.assertRaises(InvalidShadowTransition):
            self.service.validate_transition('ACCEPTED', 'IN_PROGRESS')
    
    def test_closed_to_accepted_fails(self):
        """Invalid: CLOSED → ACCEPTED (terminal state)."""
        with self.assertRaises(InvalidShadowTransition):
            self.service.validate_transition('CLOSED', 'ACCEPTED')
    
    def test_in_progress_to_pending_fails(self):
        """Invalid: IN_PROGRESS → PENDING (backward)."""
        with self.assertRaises(InvalidShadowTransition):
            self.service.validate_transition('IN_PROGRESS', 'PENDING')


class TestCloseCaseTransitions(unittest.TestCase):
    """Test closing cases."""
    
    def setUp(self):
        self.service = TestableWorkflowService()
        self.reviewer = MockUser(id=1)
    
    def test_accepted_to_closed_ok(self):
        """Valid: ACCEPTED → CLOSED."""
        review = MockReviewDecisionRecord(
            status='ACCEPTED',
            decision=MockReviewDecision.V2_CORRECT,
        )
        
        result = self.service.close_case(review, self.reviewer)
        
        self.assertEqual(result.status, 'CLOSED')
        self.assertIsNotNone(result.closed_at)
    
    def test_in_progress_to_closed_fails(self):
        """Invalid: IN_PROGRESS → CLOSED (skipping decision)."""
        review = MockReviewDecisionRecord(status='IN_PROGRESS')
        
        with self.assertRaises(InvalidShadowTransition):
            self.service.close_case(review, self.reviewer)
    
    def test_pending_to_closed_fails(self):
        """Invalid: PENDING → CLOSED (skipping all steps)."""
        review = MockReviewDecisionRecord(status='PENDING')
        
        with self.assertRaises(InvalidShadowTransition):
            self.service.close_case(review, self.reviewer)


class TestTerminalState(unittest.TestCase):
    """Test that CLOSED is terminal."""
    
    def setUp(self):
        self.service = TestableWorkflowService()
    
    def test_closed_to_anything_fails(self):
        """Invalid: CLOSED → any state."""
        for target in ['PENDING', 'IN_PROGRESS', 'ACCEPTED', 'ADJUSTED', 'ESCALATED']:
            with self.assertRaises(InvalidShadowTransition):
                self.service.validate_transition('CLOSED', target)


class TestAuditGeneration(unittest.TestCase):
    """Test that audit logs are generated."""
    
    def setUp(self):
        self.service = TestableWorkflowService()
        self.reviewer = MockUser(id=1)
    
    def test_start_review_creates_audit(self):
        """Audit created for start_review."""
        review = MockReviewDecisionRecord(status='PENDING')
        
        self.service.start_review(review, self.reviewer)
        
        self.assertEqual(len(self.service.audit_log), 1)
        self.assertEqual(self.service.audit_log[0]['action'], 'SHADOW_REVIEW_STARTED')
    
    def test_submit_decision_creates_audit(self):
        """Audit created for submit_decision."""
        review = MockReviewDecisionRecord(
            status='IN_PROGRESS',
            reviewer_id=1,
        )
        
        self.service.submit_decision(
            review, self.reviewer,
            decision=MockReviewDecision.V2_CORRECT,
            notes="Valid decision",
        )
        
        self.assertEqual(len(self.service.audit_log), 1)
        self.assertEqual(self.service.audit_log[0]['action'], 'SHADOW_REVIEW_DECIDED')
    
    def test_close_case_creates_audit(self):
        """Audit created for close_case."""
        review = MockReviewDecisionRecord(
            status='ACCEPTED',
            decision=MockReviewDecision.V2_CORRECT,
        )
        
        self.service.close_case(review, self.reviewer)
        
        self.assertEqual(len(self.service.audit_log), 1)
        self.assertEqual(self.service.audit_log[0]['action'], 'SHADOW_REVIEW_CLOSED')
    
    def test_full_workflow_creates_three_audits(self):
        """Full workflow creates 3 audit entries."""
        review = MockReviewDecisionRecord(status='PENDING')
        
        # Step 1: Start
        self.service.start_review(review, self.reviewer)
        
        # Step 2: Decide
        self.service.submit_decision(
            review, self.reviewer,
            decision=MockReviewDecision.V2_CORRECT,
            notes="Approved",
        )
        
        # Step 3: Close
        self.service.close_case(review, self.reviewer)
        
        self.assertEqual(len(self.service.audit_log), 3)
        self.assertEqual(self.service.audit_log[0]['action'], 'SHADOW_REVIEW_STARTED')
        self.assertEqual(self.service.audit_log[1]['action'], 'SHADOW_REVIEW_DECIDED')
        self.assertEqual(self.service.audit_log[2]['action'], 'SHADOW_REVIEW_CLOSED')


# =============================================================================
# TEST RUNNER
# =============================================================================

def run_tests():
    """Run all tests and print results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_classes = [
        TestPendingToInProgress,
        TestInProgressToDecided,
        TestWrongReviewer,
        TestDecisionNotesRequired,
        TestBackwardTransitions,
        TestCloseCaseTransitions,
        TestTerminalState,
        TestAuditGeneration,
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
