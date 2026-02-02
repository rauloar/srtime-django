"""
Forensic API Exceptions
Custom exception handlers for clean error responses.

DESIGN:
- Never expose internal stack traces
- Provide actionable error codes
- Include request IDs for tracing
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


class ForensicAPIError(Exception):
    """Base exception for forensic API errors."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'FORENSIC_ERROR'
    
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class EmployeeNotFoundError(ForensicAPIError):
    """Raised when employee is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    error_code = 'EMPLOYEE_NOT_FOUND'


class AttendanceNotFoundError(ForensicAPIError):
    """Raised when attendance record is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    error_code = 'ATTENDANCE_NOT_FOUND'


class AnalysisNotFoundError(ForensicAPIError):
    """Raised when shadow analysis is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    error_code = 'ANALYSIS_NOT_FOUND'


class InvalidTransitionError(ForensicAPIError):
    """Raised when an invalid workflow transition is attempted."""
    status_code = status.HTTP_409_CONFLICT
    error_code = 'INVALID_TRANSITION'


class UnauthorizedActionError(ForensicAPIError):
    """Raised when user is not authorized for an action."""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = 'UNAUTHORIZED_ACTION'


class ProtectedDayError(ForensicAPIError):
    """Raised when trying to modify a protected day."""
    status_code = status.HTTP_409_CONFLICT
    error_code = 'PROTECTED_DAY'


def forensic_exception_handler(exc, context):
    """
    Custom exception handler for forensic API.
    
    Ensures:
    - Clean error responses
    - No internal stack traces exposed
    - Consistent error format
    """
    # Handle our custom exceptions
    if isinstance(exc, ForensicAPIError):
        return Response({
            'error': exc.error_code,
            'message': exc.message,
            'details': exc.details,
        }, status=exc.status_code)
    
    # Default DRF handling
    response = exception_handler(exc, context)
    
    if response is not None:
        # Wrap in standard format
        response.data = {
            'error': 'API_ERROR',
            'message': str(exc) if hasattr(exc, '__str__') else 'An error occurred',
            'details': response.data if isinstance(response.data, dict) else {'errors': response.data},
        }
    
    return response
