"""
Operational API Views
REST API endpoints for operational attendance management.

Focus: Help HR find and fix issues in base data.
NOT for modifying calculation results.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime, timedelta

from core.models import Employee
from core.services.operational_index_service import OperationalIndexService


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_days_requiring_attention(request):
    """
    Get days requiring HR attention.
    
    GET /api/attendance/attention/?from=2025-01-01&to=2025-01-31&employee_id=123
    
    Returns days with:
    - Anomalies
    - Gaps
    - Unclassified time
    - Abnormal status
    - Time deficits
    
    Returns:
        {
            "period": {"from": "2025-01-01", "to": "2025-01-31"},
            "total_requiring_attention": 15,
            "days": [
                {
                    "date": "2025-01-15",
                    "employee": {"id": 123, "name": "John Doe"},
                    "status": "LATE",
                    "worked_minutes": 450,
                    "expected_minutes": 480,
                    "minutes_difference": -30,
                    "flags": {
                        "has_anomalies": true,
                        "anomaly_count": 2,
                        "has_gaps": true,
                        "has_unclassified_time": false,
                        "requires_attention": true
                    }
                },
                ...
            ]
        }
    """
    # Parse dates
    from_str = request.query_params.get('from')
    to_str = request.query_params.get('to')
    
    if not from_str or not to_str:
        return Response(
            {'error': 'Both from and to parameters are required (YYYY-MM-DD)'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        from_date = datetime.strptime(from_str, '%Y-%m-%d').date()
        to_date = datetime.strptime(to_str, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {'error': 'Invalid date format. Use YYYY-MM-DD'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Optional employee filter
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
    
    # Get days requiring attention
    service = OperationalIndexService()
    days = service.get_days_requiring_attention(from_date, to_date, employee)
    
    return Response({
        'period': {
            'from': from_str,
            'to': to_str,
        },
        'total_requiring_attention': len(days),
        'days': days,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_employee_overview(request, employee_id):
    """
    Get employee attendance overview.
    
    GET /api/attendance/employee/{employee_id}/overview/?days=30
    
    Returns summary statistics for recent period.
    
    Returns:
        {
            "employee_id": 123,
            "employee_name": "John Doe",
            "period_days": 30,
            "total_days_indexed": 28,
            "days_with_anomalies": 5,
            "days_requiring_attention": 3,
            "total_deficit_minutes": 120,
            "total_overtime_minutes": 45,
            "avg_deficit_per_day": 4.3,
            "avg_overtime_per_day": 1.6
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
    
    service = OperationalIndexService()
    overview = service.get_employee_overview(employee, days)
    
    return Response(overview)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_global_stats(request):
    """
    Get global attendance statistics.
    
    GET /api/attendance/stats/global/?from=2025-01-01&to=2025-01-31
    
    Returns:
        {
            "period": {"from": "2025-01-01", "to": "2025-01-31"},
            "total_days_indexed": 1000,
            "percent_with_gaps": 12.5,
            "percent_with_anomalies": 18.3,
            "percent_requiring_attention": 15.2,
            "status_breakdown": {
                "PRESENT": 850,
                "LATE": 75,
                "ABSENT": 50,
                "EARLY_LEAVE": 25
            }
        }
    """
    from_str = request.query_params.get('from')
    to_str = request.query_params.get('to')
    
    if not from_str or not to_str:
        return Response(
            {'error': 'Both from and to parameters are required (YYYY-MM-DD)'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        from_date = datetime.strptime(from_str, '%Y-%m-%d').date()
        to_date = datetime.strptime(to_str, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {'error': 'Invalid date format. Use YYYY-MM-DD'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    service = OperationalIndexService()
    stats = service.get_global_stats(from_date, to_date)
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_anomaly_breakdown(request):
    """
    Get breakdown of anomaly types.
    
    GET /api/attendance/stats/anomalies/?from=2025-01-01&to=2025-01-31
    
    Returns frequency of different anomaly types.
    
    Returns:
        {
            "period": {"from": "2025-01-01", "to": "2025-01-31"},
            "total_days_with_anomalies": 183,
            "anomaly_types": {
                "LATE_ENTRY": 75,
                "EARLY_LEAVE": 48,
                "MISSING_OUT": 35,
                "ORPHAN_PUNCH": 25
            }
        }
    """
    from_str = request.query_params.get('from')
    to_str = request.query_params.get('to')
    
    if not from_str or not to_str:
        return Response(
            {'error': 'Both from and to parameters are required (YYYY-MM-DD)'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        from_date = datetime.strptime(from_str, '%Y-%m-%d').date()
        to_date = datetime.strptime(to_str, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {'error': 'Invalid date format. Use YYYY-MM-DD'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get days with anomalies
    from core.models_explanation import AttendanceExplanation
    
    explanations = AttendanceExplanation.objects.filter(
        date__gte=from_date,
        date__lte=to_date,
        anomalies__len__gt=0
    )
    
    # Count anomaly types
    anomaly_counts = {}
    total_with_anomalies = 0
    
    for explanation in explanations:
        if explanation.anomalies:
            total_with_anomalies += 1
            for anomaly in explanation.anomalies:
                anomaly_counts[anomaly] = anomaly_counts.get(anomaly, 0) + 1
    
    return Response({
        'period': {
            'from': from_str,
            'to': to_str,
        },
        'total_days_with_anomalies': total_with_anomalies,
        'anomaly_types': anomaly_counts,
    })
