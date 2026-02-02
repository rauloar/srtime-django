"""
Tests for Forensic Model Protection
Verifies that protected models cannot be modified outside forensic context.
"""
import pytest
from unittest.mock import patch, MagicMock

from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model

from core.forensic.context import (
    forensic_operation,
    get_forensic_context,
    is_forensic_context_active,
)
from core.forensic.model_protection import (
    ForensicModelProtectionMixin,
    ForensicImmutabilityError,
    ForensicDeleteBlockedError,
    ForensicUpdateBlockedError,
    log_immutability_violation,
)


User = get_user_model()


# =============================================================================
# TEST MODEL (Simulated Protected Model)
# =============================================================================

class MockProtectedModel:
    """Mock model for testing protection mixin."""
    
    FORENSIC_PROTECTED = True
    FORENSIC_IMMUTABLE_STATUSES = {'CLOSED'}
    FORENSIC_STATUS_FIELD = 'status'
    FORENSIC_ALLOW_INITIAL_CREATE = True
    
    def __init__(self, pk=None, status='PENDING'):
        self.pk = pk
        self.status = status
        self._saved = False
        self._deleted = False
    
    class _meta:
        db_table = 'mock_protected_table'
        model_name = 'mockprotectedmodel'
        fields = []
    
    class DoesNotExist(Exception):
        pass
    
    class objects:
        @staticmethod
        def get(pk):
            raise MockProtectedModel.DoesNotExist()
        
        @staticmethod
        def create(**kwargs):
            return MagicMock()


class TestableProtectedModel(ForensicModelProtectionMixin, MockProtectedModel):
    """Testable protected model combining mixin with mock."""
    
    def save(self, *args, **kwargs):
        # Call the mixin's save which will check protection
        # Then mark as saved if allowed
        super().save(*args, **kwargs)
        self._saved = True
    
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self._deleted = True


# =============================================================================
# CONTEXT TESTS
# =============================================================================

class TestForensicContext(TestCase):
    """Tests for forensic context management."""
    
    def test_no_context_by_default(self):
        """Context should be None when not in forensic operation."""
        self.assertIsNone(get_forensic_context())
        self.assertFalse(is_forensic_context_active())
    
    def test_context_active_within_operation(self):
        """Context should be active within forensic_operation block."""
        with forensic_operation(
            actor_id=1,
            operation_type='TEST'
        ) as ctx:
            self.assertTrue(is_forensic_context_active())
            self.assertIsNotNone(get_forensic_context())
            self.assertEqual(ctx.actor_id, 1)
            self.assertEqual(ctx.operation_type, 'TEST')
    
    def test_context_inactive_after_operation(self):
        """Context should be None after exiting forensic_operation block."""
        with forensic_operation(actor_id=1):
            pass  # Do something
        
        self.assertIsNone(get_forensic_context())
        self.assertFalse(is_forensic_context_active())
    
    def test_context_has_operation_id(self):
        """Context should auto-generate operation_id if not provided."""
        with forensic_operation() as ctx:
            self.assertIsNotNone(ctx.operation_id)
            self.assertTrue(len(ctx.operation_id) > 0)
    
    def test_context_uses_provided_operation_id(self):
        """Context should use provided operation_id."""
        with forensic_operation(operation_id='custom-123') as ctx:
            self.assertEqual(ctx.operation_id, 'custom-123')
    
    def test_nested_contexts_allowed(self):
        """Nested forensic operations should return outer context."""
        with forensic_operation(operation_id='outer') as outer_ctx:
            with forensic_operation(operation_id='inner') as inner_ctx:
                # Inner should get the outer context (no nesting)
                self.assertEqual(inner_ctx.operation_id, 'outer')
            
            # Still in outer context
            self.assertTrue(is_forensic_context_active())
    
    def test_context_records_saves(self):
        """Context should track model saves."""
        with forensic_operation() as ctx:
            ctx.record_save('TestModel', 123)
            ctx.record_save('TestModel', 456)
            
            self.assertEqual(ctx._save_count, 2)
            self.assertEqual(len(ctx._models_modified), 2)


# =============================================================================
# MODEL PROTECTION TESTS
# =============================================================================

class TestModelProtection(TestCase):
    """Tests for model save/delete protection."""
    
    def test_save_blocked_without_context(self):
        """Saving protected model without context should raise error."""
        model = TestableProtectedModel(pk=1)
        
        with patch.object(TestableProtectedModel, '__class__') as mock_class:
            mock_class.__name__ = 'TestableProtectedModel'
            mock_class._meta = MockProtectedModel._meta
            
            with self.assertRaises(ForensicImmutabilityError) as context:
                model.save()
            
            self.assertIn('FORENSIC SECURITY VIOLATION', str(context.exception))
            self.assertIn('outside forensic context', str(context.exception))
    
    def test_save_allowed_with_context(self):
        """Saving protected model with context should succeed."""
        model = TestableProtectedModel(pk=None)  # New record
        
        with forensic_operation(actor_id=1):
            # Should not raise
            model.save()
            self.assertTrue(model._saved)
    
    def test_new_record_allowed_without_context(self):
        """Creating new record should be allowed (FORENSIC_ALLOW_INITIAL_CREATE=True)."""
        model = TestableProtectedModel(pk=None)
        
        # Should not raise for new records
        model.save()
        self.assertTrue(model._saved)
    
    def test_delete_always_blocked(self):
        """Deleting protected model should always raise error."""
        model = TestableProtectedModel(pk=1)
        
        # Even with context, delete should be blocked
        with forensic_operation(actor_id=1):
            with self.assertRaises(ForensicDeleteBlockedError) as context:
                model.delete()
            
            self.assertIn('DELETE operations are NEVER allowed', str(context.exception))
    
    def test_unprotected_model_allowed(self):
        """Model with FORENSIC_PROTECTED=False should allow all operations."""
        model = TestableProtectedModel(pk=1)
        model.FORENSIC_PROTECTED = False
        
        # Should not raise
        model.save()
        self.assertTrue(model._saved)


# =============================================================================
# IMMUTABLE STATUS TESTS
# =============================================================================

class TestImmutableStatus(TestCase):
    """Tests for status-based immutability."""
    
    def test_closed_record_blocked(self):
        """Updating record with CLOSED status should be blocked."""
        model = TestableProtectedModel(pk=1, status='CLOSED')
        
        # Mock the database lookup
        with patch.object(
            TestableProtectedModel.objects,
            'get',
            return_value=TestableProtectedModel(pk=1, status='CLOSED')
        ):
            with forensic_operation(actor_id=1):
                with self.assertRaises(ForensicUpdateBlockedError) as context:
                    model._check_immutable_status()
                
                self.assertIn('CLOSED', str(context.exception))
    
    def test_pending_record_allowed(self):
        """Updating record with PENDING status should be allowed."""
        model = TestableProtectedModel(pk=1, status='PENDING')
        
        with patch.object(
            TestableProtectedModel.objects,
            'get',
            return_value=TestableProtectedModel(pk=1, status='PENDING')
        ):
            with forensic_operation(actor_id=1):
                # Should not raise
                model._check_immutable_status()


# =============================================================================
# VIOLATION LOGGING TESTS
# =============================================================================

class TestViolationLogging(TestCase):
    """Tests for violation logging."""
    
    @patch('core.forensic.model_protection.ForensicImmutabilityViolation')
    def test_violation_logged(self, mock_violation_model):
        """Violations should be logged to database."""
        mock_violation_model.objects.create.return_value = MagicMock(id=1)
        
        log_immutability_violation(
            table_name='test_table',
            record_id=123,
            operation='UPDATE',
            old_values={'status': 'PENDING'},
            attempted_by='test_user',
        )
        
        mock_violation_model.objects.create.assert_called_once()
        call_kwargs = mock_violation_model.objects.create.call_args[1]
        
        self.assertEqual(call_kwargs['table_name'], 'test_table')
        self.assertEqual(call_kwargs['record_id'], 123)
        self.assertEqual(call_kwargs['attempted_operation'], 'UPDATE')
        self.assertTrue(call_kwargs['blocked'])


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestForensicIntegration(TestCase):
    """Integration tests for forensic protection."""
    
    def test_complete_flow_with_context(self):
        """Complete flow: context → save → record tracking."""
        model = TestableProtectedModel(pk=None)  # New record
        
        with forensic_operation(
            actor_id=1,
            entity_type='TestModel',
            operation_type='CREATE'
        ) as ctx:
            model.save()
            
            # Context should track the save
            self.assertEqual(ctx._save_count, 1)
    
    def test_exception_raised_for_unauthorized_update(self):
        """Unauthorized update should raise and log."""
        model = TestableProtectedModel(pk=1)
        
        with self.assertRaises(ForensicImmutabilityError):
            model.save()
    
    def test_context_cleans_up_on_exception(self):
        """Context should be cleared even if exception occurs."""
        def failing_operation():
            with forensic_operation():
                raise ValueError("Test error")
        
        with self.assertRaises(ValueError):
            failing_operation()
        
        # Context should still be None
        self.assertIsNone(get_forensic_context())
