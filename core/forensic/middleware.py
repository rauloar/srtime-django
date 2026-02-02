"""
Forensic Request Middleware
Django middleware for forensic request tracking and idempotency.

Provides:
- Extraction of X-Idempotency-Key header
- Generation of correlation IDs
- Attachment of forensic metadata to requests
"""
import uuid
import logging
from typing import Callable

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils import timezone

from core.forensic.context import forensic_context_from_request


logger = logging.getLogger('forensic.middleware')


class ForensicRequestMiddleware:
    """
    Middleware that prepares forensic metadata for each request.
    
    Does NOT automatically activate forensic context.
    The context is activated by ForensicReviewService/ForensicExportService.
    
    This middleware:
    1. Extracts X-Idempotency-Key header
    2. Generates X-Correlation-ID if not present
    3. Attaches forensic metadata to request object
    4. Adds tracing headers to response
    """
    
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Extract forensic context from request
        forensic_meta = forensic_context_from_request(request)
        
        # Attach to request for use by views
        request.forensic_meta = forensic_meta
        request.correlation_id = forensic_meta['correlation_id']
        request.idempotency_key = forensic_meta['idempotency_key']
        
        # Log request (for forensic endpoints)
        if request.path.startswith('/api/forensic/'):
            logger.info(
                f"Forensic request: {request.method} {request.path} "
                f"correlation_id={forensic_meta['correlation_id']} "
                f"idempotency_key={forensic_meta['idempotency_key']} "
                f"actor={forensic_meta['actor_username']}"
            )
        
        # Process request
        response = self.get_response(request)
        
        # Add tracing headers to response
        response['X-Correlation-ID'] = forensic_meta['correlation_id']
        
        if forensic_meta['idempotency_key']:
            response['X-Idempotency-Key'] = forensic_meta['idempotency_key']
        
        return response


class IdempotencyKeyRequiredMiddleware:
    """
    Middleware that REQUIRES X-Idempotency-Key for write operations
    on forensic endpoints.
    
    Returns 400 Bad Request if missing.
    """
    
    FORENSIC_WRITE_PATHS = [
        '/api/forensic/shadow/review/start',
        '/api/forensic/shadow/review/decision',
        '/api/forensic/shadow/review/close',
        '/api/forensic/shadow/export',
    ]
    
    WRITE_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
    
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Check if this is a forensic write operation
        if request.method in self.WRITE_METHODS:
            for path in self.FORENSIC_WRITE_PATHS:
                if request.path.startswith(path):
                    # Require idempotency key
                    idempotency_key = (
                        request.headers.get('X-Idempotency-Key') or
                        request.META.get('HTTP_X_IDEMPOTENCY_KEY')
                    )
                    
                    if not idempotency_key:
                        logger.warning(
                            f"Missing idempotency key: {request.method} {request.path} "
                            f"from {request.META.get('REMOTE_ADDR')}"
                        )
                        
                        return JsonResponse(
                            {
                                'error': 'IDEMPOTENCY_KEY_REQUIRED',
                                'message': (
                                    'X-Idempotency-Key header is required for '
                                    'forensic write operations'
                                ),
                                'path': request.path,
                            },
                            status=400
                        )
                    break
        
        return self.get_response(request)


class ForensicAuditMiddleware:
    """
    Middleware that logs all access to forensic endpoints for audit purposes.
    
    Logs:
    - All GET requests to forensic data
    - All write attempts (successful or not)
    - All authentication failures
    """
    
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Only process forensic endpoints
        if not request.path.startswith('/api/forensic/'):
            return self.get_response(request)
        
        start_time = timezone.now()
        
        # Process request
        response = self.get_response(request)
        
        # Calculate duration
        duration_ms = (timezone.now() - start_time).total_seconds() * 1000
        
        # Log based on response status
        log_level = logging.INFO
        if response.status_code >= 400:
            log_level = logging.WARNING
        if response.status_code >= 500:
            log_level = logging.ERROR
        
        # Extract user info
        actor = 'anonymous'
        if hasattr(request, 'user') and request.user.is_authenticated:
            actor = request.user.username
        
        logger.log(
            log_level,
            f"FORENSIC_AUDIT: {request.method} {request.path} "
            f"status={response.status_code} "
            f"duration={duration_ms:.2f}ms "
            f"actor={actor} "
            f"ip={request.META.get('REMOTE_ADDR')} "
            f"correlation_id={getattr(request, 'correlation_id', 'unknown')}"
        )
        
        return response
