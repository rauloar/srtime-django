"""
Adjustment API Views
REST API endpoints for HR to manage attendance adjustments.

Adjustments modify base data (punches/schedules), not results.
All adjustments trigger automatic recalculation.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime

from core.models import Employee
from core.models_operational_adjustments import AttendanceAdjustment, FlexibleWorkRule
from core.services.adjustment_service import AdjustmentService


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_adjustment(request):
    """
    Request an attendance adjustment.
    
    POST /api/hr/adjustments/request/
    
    Body:
        {
            "employee_id": 123,
            "date": "2025-01-15",
            "adjustment_type": "EDIT_PUNCH",
            "original_time": "08:00",
            "new_time": "07:52",
            "punch_type": "IN",
            "reason": "Biometric reader failed"
        }
    
    Returns:
        {
            "id": 456,
            "status": "pending_approval",
            "message": "Adjustment requested successfully"
        }
    """
    data = request.data
    
    # Validate employee
    try:
        employee = Employee.objects.get(id=data.get('employee_id'))
    except Employee.DoesNotExist:
        return Response(
            {'error': 'Employee not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Parse date
    try:
        date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return Response(
            {'error': 'Invalid date format. Use YYYY-MM-DD'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Parse times if provided
    original_time = None
    new_time = None
    
    if data.get('original_time'):
        try:
            original_time = datetime.strptime(data['original_time'], '%H:%M').time()
        except ValueError:
            return Response(
                {'error': 'Invalid original_time format. Use HH:MM'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    if data.get('new_time'):
        try:
            new_time = datetime.strptime(data['new_time'], '%H:%M').time()
        except ValueError:
            return Response(
                {'error': 'Invalid new_time format. Use HH:MM'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Create adjustment
    adjustment = AttendanceAdjustment.objects.create(
        employee=employee,
        date=date,
        adjustment_type=data.get('adjustment_type'),
        original_time=original_time,
        new_time=new_time,
        punch_type=data.get('punch_type', ''),
        reason=data.get('reason', ''),
        requested_by=request.user
    )
    
    return Response({
        'id': adjustment.id,
        'status': 'pending_approval',
        'message': 'Adjustment requested successfully',
        'adjustment': adjustment.to_dict()
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_adjustment(request, adjustment_id):
    """
    Approve an adjustment.
    
    POST /api/hr/adjustments/{id}/approve/
    
    Returns:
        {
            "status": "approved",
            "message": "Adjustment approved successfully"
        }
    """
    try:
        adjustment = AttendanceAdjustment.objects.get(id=adjustment_id)
    except AttendanceAdjustment.DoesNotExist:
        return Response(
            {'error': 'Adjustment not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    service = AdjustmentService()
    
    if service.approve_adjustment(adjustment, request.user):
        return Response({
            'status': 'approved',
            'message': 'Adjustment approved successfully',
            'adjustment': adjustment.to_dict()
        })
    else:
        return Response({
            'error': 'Adjustment already approved'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_adjustment(request, adjustment_id):
    """
    Apply an approved adjustment.
    
    POST /api/hr/adjustments/{id}/apply/
    
    This will:
    1. Modify base data (punches/schedules)
    2. Trigger automatic recalculation
    3. Update all derived data (timeline, index, etc.)
    
    Returns:
        {
            "status": "applied",
            "message": "Adjustment applied and day recalculated"
        }
    """
    try:
        adjustment = AttendanceAdjustment.objects.get(id=adjustment_id)
    except AttendanceAdjustment.DoesNotExist:
        return Response(
            {'error': 'Adjustment not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    service = AdjustmentService()
    
    if service.apply_adjustment(adjustment):
        return Response({
            'status': 'applied',
            'message': 'Adjustment applied and day recalculated',
            'adjustment': adjustment.to_dict()
        })
    else:
        return Response({
            'error': 'Failed to apply adjustment. Check logs for details.'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_adjustments(request):
    """
    Get pending adjustments.
    
    GET /api/hr/adjustments/pending/?employee_id=123
    
    Returns:
        {
            "count": 5,
            "adjustments": [...]
        }
    """
    employee_id = request.query_params.get('employee_id')
    employee = None
    
    if employee_id:
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response(
                {'error': 'Employee not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    service = AdjustmentService()
    adjustments = service.get_pending_adjustments(employee)
    
    return Response({
        'count': len(adjustments),
        'adjustments': [adj.to_dict() for adj in adjustments]
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_adjustment_history(request, employee_id):
    """
    Get adjustment history for an employee.
    
    GET /api/hr/adjustments/employee/{employee_id}/history/?days=30
    
    Returns:
        {
            "employee_id": 123,
            "employee_name": "John Doe",
            "count": 12,
            "adjustments": [...]
        }
    """
    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        return Response(
            {'error': 'Employee not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    days = int(request.query_params.get('days', 30))
    
    from datetime import timedelta
    from django.utils import timezone
    
    cutoff_date = timezone.now().date() - timedelta(days=days)
    
    adjustments = AttendanceAdjustment.objects.filter(
        employee=employee,
        date__gte=cutoff_date
    ).order_by('-created_at')
    
    return Response({
        'employee_id': employee_id,
        'employee_name': employee.full_name,
        'count': adjustments.count(),
        'adjustments': [adj.to_dict() for adj in adjustments]
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_flexible_rule(request):
    """
    Create flexible work rule.
    
    POST /api/hr/flexible-rules/
    
    Body:
        {
            "employee_id": 123,
            "weekly_expected_hours": 40.0,
            "daily_min_hours": 4.0,
            "daily_max_hours": 12.0,
            "core_start_time": "10:00",
            "core_end_time": "15:00",
            "effective_from": "2025-01-01"
        }
    """
    data = request.data
    
    try:
        employee = Employee.objects.get(id=data.get('employee_id'))
    except Employee.DoesNotExist:
        return Response(
            {'error': 'Employee not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        effective_from = datetime.strptime(data.get('effective_from'), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return Response(
            {'error': 'Invalid effective_from format. Use YYYY-MM-DD'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Parse optional times
    core_start_time = None
    core_end_time = None
    
    if data.get('core_start_time'):
        try:
            core_start_time = datetime.strptime(data['core_start_time'], '%H:%M').time()
        except ValueError:
            return Response(
                {'error': 'Invalid core_start_time format. Use HH:MM'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    if data.get('core_end_time'):
        try:
            core_end_time = datetime.strptime(data['core_end_time'], '%H:%M').time()
        except ValueError:
            return Response(
                {'error': 'Invalid core_end_time format. Use HH:MM'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    rule = FlexibleWorkRule.objects.create(
        employee=employee,
        weekly_expected_hours=data.get('weekly_expected_hours'),
        daily_min_hours=data.get('daily_min_hours'),
        daily_max_hours=data.get('daily_max_hours', 12.0),
        core_start_time=core_start_time,
        core_end_time=core_end_time,
        effective_from=effective_from
    )
    
    return Response({
        'message': 'Flexible rule created successfully',
        'rule': rule.to_dict()
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_flexible_rule(request, employee_id):
    """
    Get active flexible rule for employee.
    
    GET /api/hr/flexible-rules/employee/{employee_id}/
    
    Returns:
        {
            "rule": {...} or null
        }
    """
    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        return Response(
            {'error': 'Employee not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    from django.utils import timezone
    
    service = AdjustmentService()
    rule = service.get_flexible_rule(employee, timezone.now().date())
    
    return Response({
        'rule': rule.to_dict() if rule else None
    })
