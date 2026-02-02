"""
Tests for Forensic Middleware
Verifies request tracking, idempotency enforcement, and audit logging.
"""
import json
from unittest.mock import MagicMock, patch

from django.test import TestCase, RequestFactory
from django.http import JsonResponse

from core.forensic.middleware import (
    ForensicRequestMiddleware,
    IdempotencyKeyRequiredMiddleware,
    ForensicAuditMiddleware,
)


class TestForensicRequestMiddleware(TestCase):
    """Tests for ForensicRequestMiddleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.mock_response = MagicMock(status_code=200)
        self.mock_response.__setitem__ = MagicMock()
        self.mock_get_response = MagicMock(return_value=self.mock_response)
        self.middleware = ForensicRequestMiddleware(self.mock_get_response)
    
    def test_extracts_idempotency_key(self):
        """Middleware should extract X-Idempotency-Key header."""
        request = self.factory.get(
            '/api/forensic/test',
            HTTP_X_IDEMPOTENCY_KEY='test-key-123'
        )
        
        self.middleware(request)
        
        self.assertEqual(request.idempotency_key, 'test-key-123')
    
    def test_extracts_correlation_id(self):
        """Middleware should extract X-Correlation-ID header."""
        request = self.factory.get(
            '/api/forensic/test',
            HTTP_X_CORRELATION_ID='corr-456'
        )
        
        self.middleware(request)
        
        self.assertEqual(request.correlation_id, 'corr-456')
    
    def test_generates_correlation_id_if_missing(self):
        """Middleware should generate correlation ID if not provided."""
        request = self.factory.get('/api/forensic/test')
        
        self.middleware(request)
        
        self.assertIsNotNone(request.correlation_id)
        self.assertTrue(len(request.correlation_id) > 0)
    
    def test_attaches_forensic_meta(self):
        """Middleware should attach forensic_meta to request."""
        request = self.factory.get('/api/forensic/test')
        
        self.middleware(request)
        
        self.assertTrue(hasattr(request, 'forensic_meta'))
        self.assertIn('correlation_id', request.forensic_meta)
        self.assertIn('idempotency_key', request.forensic_meta)
        self.assertIn('endpoint', request.forensic_meta)
    
    def test_adds_correlation_header_to_response(self):
        """Middleware should add X-Correlation-ID to response."""
        request = self.factory.get('/api/test')
        
        self.middleware(request)
        
        self.mock_response.__setitem__.assert_any_call(
            'X-Correlation-ID',
            request.correlation_id
        )


class TestIdempotencyKeyRequiredMiddleware(TestCase):
    """Tests for IdempotencyKeyRequiredMiddleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.mock_response = MagicMock(status_code=200)
        self.mock_get_response = MagicMock(return_value=self.mock_response)
        self.middleware = IdempotencyKeyRequiredMiddleware(self.mock_get_response)
    
    def test_requires_key_for_forensic_write(self):
        """Should return 400 for forensic write without idempotency key."""
        request = self.factory.post('/api/forensic/shadow/review/start')
        
        response = self.middleware(request)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'IDEMPOTENCY_KEY_REQUIRED')
    
    def test_allows_with_key(self):
        """Should allow request with idempotency key."""
        request = self.factory.post(
            '/api/forensic/shadow/review/start',
            HTTP_X_IDEMPOTENCY_KEY='key-123'
        )
        
        response = self.middleware(request)
        
        # Should pass through to next middleware
        self.assertEqual(response, self.mock_response)
    
    def test_allows_get_without_key(self):
        """Should allow GET requests without idempotency key."""
        request = self.factory.get('/api/forensic/shadow/review/start')
        
        response = self.middleware(request)
        
        self.assertEqual(response, self.mock_response)
    
    def test_allows_non_forensic_without_key(self):
        """Should allow non-forensic endpoints without key."""
        request = self.factory.post('/api/other/endpoint')
        
        response = self.middleware(request)
        
        self.assertEqual(response, self.mock_response)
    
    def test_decision_endpoint_requires_key(self):
        """Decision endpoint should require idempotency key."""
        request = self.factory.post('/api/forensic/shadow/review/decision')
        
        response = self.middleware(request)
        
        self.assertEqual(response.status_code, 400)
    
    def test_close_endpoint_requires_key(self):
        """Close endpoint should require idempotency key."""
        request = self.factory.post('/api/forensic/shadow/review/close')
        
        response = self.middleware(request)
        
        self.assertEqual(response.status_code, 400)


class TestForensicAuditMiddleware(TestCase):
    """Tests for ForensicAuditMiddleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.mock_response = MagicMock(status_code=200)
        self.mock_get_response = MagicMock(return_value=self.mock_response)
        self.middleware = ForensicAuditMiddleware(self.mock_get_response)
    
    def test_logs_forensic_requests(self):
        """Should log requests to forensic endpoints."""
        request = self.factory.get('/api/forensic/test')
        
        with patch('core.forensic.middleware.logger') as mock_logger:
            self.middleware(request)
            
            mock_logger.log.assert_called()
    
    def test_passes_through_non_forensic(self):
        """Should pass through non-forensic requests without logging."""
        request = self.factory.get('/api/other/endpoint')
        
        response = self.middleware(request)
        
        self.assertEqual(response, self.mock_response)
    
    def test_logs_warning_for_4xx(self):
        """Should log warning level for 4xx responses."""
        self.mock_response.status_code = 400
        request = self.factory.get('/api/forensic/test')
        
        with patch('core.forensic.middleware.logger') as mock_logger:
            self.middleware(request)
            
            # Check that log was called with WARNING level (30)
            call_args = mock_logger.log.call_args
            self.assertEqual(call_args[0][0], 30)  # WARNING level
    
    def test_logs_error_for_5xx(self):
        """Should log error level for 5xx responses."""
        self.mock_response.status_code = 500
        request = self.factory.get('/api/forensic/test')
        
        with patch('core.forensic.middleware.logger') as mock_logger:
            self.middleware(request)
            
            # Check that log was called with ERROR level (40)
            call_args = mock_logger.log.call_args
            self.assertEqual(call_args[0][0], 40)  # ERROR level
