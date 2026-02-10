"""
Logging middleware for request/response tracking and error capturing.
"""
import logging
import time
import traceback
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('api')


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Log all API requests and responses with timing information.
    Captures errors and exceptions for debugging.
    """
    
    def process_request(self, request):
        """Log incoming request and start timer."""
        request._start_time = time.time()
        
        # Skip logging for static files and admin
        if request.path.startswith('/static/') or request.path.startswith('/admin/'):
            return None
        
        logger.info(
            f"→ {request.method} {request.path} | "
            f"IP: {self.get_client_ip(request)} | "
            f"User: {request.user if request.user.is_authenticated else 'Anonymous'}"
        )
        
        # Log request body for POST/PUT/PATCH (limited size)
        if request.method in ['POST', 'PUT', 'PATCH'] and hasattr(request, 'body'):
            try:
                body = request.body.decode('utf-8')
                if len(body) > 500:
                    body = body[:500] + '... (truncated)'
                logger.debug(f"  Request body: {body}")
            except Exception:
                pass
        
        return None
    
    def process_response(self, request, response):
        """Log response with status code and timing."""
        # Skip logging for static files and admin
        if request.path.startswith('/static/') or request.path.startswith('/admin/'):
            return response
        
        duration = time.time() - getattr(request, '_start_time', time.time())
        duration_ms = duration * 1000
        
        status_code = response.status_code
        log_level = self.get_log_level_for_status(status_code)
        
        logger.log(
            log_level,
            f"← {request.method} {request.path} | "
            f"Status: {status_code} | "
            f"Duration: {duration_ms:.2f}ms"
        )
        
        # Log response body for errors (4xx, 5xx)
        if status_code >= 400 and hasattr(response, 'content'):
            try:
                content = response.content.decode('utf-8')
                if len(content) > 500:
                    content = content[:500] + '... (truncated)'
                logger.warning(f"  Response body: {content}")
            except Exception:
                pass
        
        return response
    
    def process_exception(self, request, exception):
        """Log uncaught exceptions with full traceback."""
        duration = time.time() - getattr(request, '_start_time', time.time())
        duration_ms = duration * 1000
        
        logger.error(
            f"✗ EXCEPTION {request.method} {request.path} | "
            f"Duration: {duration_ms:.2f}ms | "
            f"Exception: {type(exception).__name__}: {str(exception)}",
            exc_info=True
        )
        
        # Also log the full traceback
        logger.error(
            f"Full traceback:\n{''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))}"
        )
        
        return None
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def get_log_level_for_status(status_code):
        """Determine appropriate log level based on HTTP status code."""
        if status_code >= 500:
            return logging.ERROR
        elif status_code >= 400:
            return logging.WARNING
        elif status_code >= 300:
            return logging.INFO
        else:
            return logging.INFO


class ErrorCaptureMiddleware(MiddlewareMixin):
    """
    Capture and log all errors with context information.
    Works as a safety net for errors not caught by views.
    """
    
    def process_exception(self, request, exception):
        """Log exception with full context."""
        error_logger = logging.getLogger('core')
        
        context = {
            'method': request.method,
            'path': request.path,
            'user': str(request.user) if request.user.is_authenticated else 'Anonymous',
            'ip': self.get_client_ip(request),
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
        }
        
        # Add GET params
        if request.GET:
            context['get_params'] = dict(request.GET)
        
        # Add POST data (limited)
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                if hasattr(request, 'body'):
                    body = request.body.decode('utf-8')
                    if len(body) > 500:
                        body = body[:500] + '... (truncated)'
                    context['request_body'] = body
            except Exception:
                pass
        
        error_logger.error(
            f"Unhandled exception in request: {context}",
            exc_info=True,
            extra=context
        )
        
        return None
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
