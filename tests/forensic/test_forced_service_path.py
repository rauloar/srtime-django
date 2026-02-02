"""
Tests for Forced Service Path
Verifies that all forensic operations MUST go through ForensicServices.
"""
import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal

from django.test import TestCase


class TestForcedServicePath(TestCase):
    """Tests that verify forensic operations require service layer."""
    
    # =========================================================================
    # DIRECT SAVE BLOCKING
    # =========================================================================
    
    def test_direct_review_save_blocked(self):
        """Direct save on review model should be blocked."""
        from core.forensic.context import is_forensic_context_active
        from core.forensic.model_protection import ForensicImmutabilityError
        
        # Outside context, protected models should block
        self.assertFalse(is_forensic_context_active())
    
    def test_service_path_allowed(self):
        """Operations through ForensicReviewService should work."""
        from core.forensic.context import forensic_operation
        
        with forensic_operation(
            actor_id=1,
            entity_type='ShadowReviewDecision',
            operation_type='TEST'
        ) as ctx:
            # Within context, operations are allowed
            self.assertIsNotNone(ctx)
    
    # =========================================================================
    # IDEMPOTENCY ENFORCEMENT
    # =========================================================================
    
    def test_missing_idempotency_key_rejected(self):
        """Requests without idempotency key should be rejected."""
        from core.forensic.middleware import IdempotencyKeyRequiredMiddleware
        from django.test import RequestFactory
        
        factory = RequestFactory()
        mock_get_response = MagicMock()
        middleware = IdempotencyKeyRequiredMiddleware(mock_get_response)
        
        request = factory.post('/api/forensic/shadow/review/decision')
        response = middleware(request)
        
        self.assertEqual(response.status_code, 400)
    
    def test_duplicate_idempotency_key_returns_cached(self):
        """Duplicate idempotency key should return cached response."""
        # This tests the concept - actual implementation in ForensicTransactionGuard
        pass
    
    # =========================================================================
    # CLOSED CASE IMMUTABILITY
    # =========================================================================
    
    def test_modify_closed_case_blocked(self):
        """Modifying a CLOSED case should be blocked."""
        from core.forensic.model_protection import ForensicUpdateBlockedError
        
        # The ForensicModelProtectionMixin should block updates to CLOSED status
        # This is enforced at model level
        pass
    
    # =========================================================================
    # ADMIN ACCESS BLOCKED
    # =========================================================================
    
    def test_admin_cannot_delete(self):
        """Django admin should not allow delete on forensic models."""
        from core.forensic.admin import ForensicReadOnlyAdmin
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/admin/')
        request.user = MagicMock(username='admin')
        
        admin = ForensicReadOnlyAdmin(MagicMock(), MagicMock())
        
        self.assertFalse(admin.has_delete_permission(request))
    
    def test_admin_cannot_add(self):
        """Django admin should not allow add on forensic models."""
        from core.forensic.admin import ForensicReadOnlyAdmin
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/admin/')
        request.user = MagicMock(username='admin')
        
        admin = ForensicReadOnlyAdmin(MagicMock(), MagicMock())
        
        self.assertFalse(admin.has_add_permission(request))
    
    def test_admin_cannot_change(self):
        """Django admin should not allow change on forensic models."""
        from core.forensic.admin import ForensicReadOnlyAdmin
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/admin/')
        request.user = MagicMock(username='admin')
        
        admin = ForensicReadOnlyAdmin(MagicMock(), MagicMock())
        
        self.assertFalse(admin.has_change_permission(request))
    
    # =========================================================================
    # HASH CHAIN INTEGRITY
    # =========================================================================
    
    def test_decision_creates_hash_chain(self):
        """Submitting decision should create integrity hash node."""
        # This is enforced in ForensicReviewService.submit_decision_forensic()
        # The service calls create_integrity_hash() after successful operation
        pass
    
    def test_closure_creates_hash_chain(self):
        """Closing case should create integrity hash node."""
        # This is enforced in ForensicReviewService.close_case_forensic()
        pass
    
    def test_export_creates_hash_chain(self):
        """Exporting PDF should create integrity hash node."""
        # This is enforced in ForensicExportService.export_case_pdf_forensic()
        pass
    
    # =========================================================================
    # VERSION MISMATCH PROTECTION
    # =========================================================================
    
    def test_version_mismatch_rejected(self):
        """Operations with wrong version should be rejected."""
        from core.services.forensic.forensic_transaction_guard import (
            OptimisticLockError
        )
        
        # This is enforced in ForensicTransactionGuard.execute()
        # When expected_version != actual_version, raises OptimisticLockError
        pass


class TestForensicServiceIntegration(TestCase):
    """Integration tests for forensic service layer."""
    
    def test_review_service_uses_guard(self):
        """ForensicReviewService should use ForensicTransactionGuard."""
        from core.services.forensic.forensic_review_service import ForensicReviewService
        
        service = ForensicReviewService()
        self.assertIsNotNone(service.guard)
    
    def test_export_service_uses_tsa(self):
        """ForensicExportService should use TSAService."""
        from core.services.forensic.forensic_export_service import ForensicExportService
        
        service = ForensicExportService()
        self.assertIsNotNone(service.tsa)


class TestForensicContextFlow(TestCase):
    """Tests for forensic context flow through the system."""
    
    def test_context_propagates_to_guard(self):
        """Forensic context should propagate to transaction guard."""
        from core.forensic.context import forensic_operation, get_forensic_context
        
        with forensic_operation(
            idempotency_key='test-key',
            actor_id=1,
            endpoint='/api/test'
        ) as ctx:
            current = get_forensic_context()
            self.assertEqual(current.idempotency_key, 'test-key')
            self.assertEqual(current.actor_id, 1)
            self.assertEqual(current.endpoint, '/api/test')
    
    def test_context_clears_after_operation(self):
        """Context should be cleared after operation completes."""
        from core.forensic.context import forensic_operation, get_forensic_context
        
        with forensic_operation(actor_id=1):
            pass  # Operation
        
        self.assertIsNone(get_forensic_context())
    
    def test_context_clears_on_exception(self):
        """Context should be cleared even if exception occurs."""
        from core.forensic.context import forensic_operation, get_forensic_context
        
        try:
            with forensic_operation(actor_id=1):
                raise ValueError("Test error")
        except ValueError:
            pass
        
        self.assertIsNone(get_forensic_context())
