"""
Forensic API Permissions
Role-based access control for attendance and shadow review operations.

ROLES:
- IsAttendanceAdmin: Can calculate and view attendance
- IsShadowReviewer: Can view and decide on shadow differences

DESIGN:
- Permissions check user.is_authenticated first
- Then check for specific group membership or custom attribute
- Safe denials with audit logging
"""
import logging
from rest_framework.permissions import BasePermission


logger = logging.getLogger(__name__)


class IsAuthenticated(BasePermission):
    """Require authentication for all forensic endpoints."""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsAttendanceAdmin(BasePermission):
    """
    Permission for attendance administration operations.
    
    Required for:
    - Calculating attendance
    - Viewing official results
    - Force recalculation
    
    Granted to:
    - Users in 'attendance_admin' group
    - Staff users
    - Superusers
    """
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user or not user.is_authenticated:
            return False
        
        # Superuser always allowed
        if user.is_superuser:
            return True
        
        # Staff with appropriate role
        if user.is_staff:
            return True
        
        # Check group membership
        if hasattr(user, 'groups'):
            if user.groups.filter(name='attendance_admin').exists():
                return True
        
        # Check custom attribute (for flexibility)
        if hasattr(user, 'can_admin_attendance'):
            return user.can_admin_attendance
        
        logger.warning(
            f"Permission denied: {user.id} attempted attendance admin action"
        )
        return False


class IsShadowReviewer(BasePermission):
    """
    Permission for shadow review operations.
    
    Required for:
    - Viewing shadow differences
    - Starting reviews
    - Submitting decisions
    - Closing cases
    
    Granted to:
    - Users in 'shadow_reviewer' group
    - Users in 'hr_supervisor' group
    - Users in 'legal' group
    - Superusers
    """
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user or not user.is_authenticated:
            return False
        
        # Superuser always allowed
        if user.is_superuser:
            return True
        
        # Check group membership
        if hasattr(user, 'groups'):
            allowed_groups = ['shadow_reviewer', 'hr_supervisor', 'legal']
            if user.groups.filter(name__in=allowed_groups).exists():
                return True
        
        # Check custom attribute
        if hasattr(user, 'can_review_shadow'):
            return user.can_review_shadow
        
        logger.warning(
            f"Permission denied: {user.id} attempted shadow review action"
        )
        return False


class IsAssignedReviewer(BasePermission):
    """
    Object-level permission for review ownership.
    
    Only the assigned reviewer can submit decisions.
    """
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Superuser bypass
        if user.is_superuser:
            return True
        
        # Check if user is the assigned reviewer
        if hasattr(obj, 'reviewer_id'):
            return obj.reviewer_id == user.id
        
        if hasattr(obj, 'review_decision'):
            return obj.review_decision.reviewer_id == user.id
        
        return False


class ReadOnly(BasePermission):
    """Allow only safe methods (GET, HEAD, OPTIONS)."""
    
    def has_permission(self, request, view):
        return request.method in ('GET', 'HEAD', 'OPTIONS')
