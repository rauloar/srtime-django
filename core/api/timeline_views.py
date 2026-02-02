"""
Timeline API Views
REST API endpoints for attendance timeline visualization.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime

from core.models import Employee
from core.services.timeline_service import TimelineService


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_attendance_timeline(request, employee_id, date_str):
    """
    Get visual timeline for an attendance day.
    
    GET /api/attendance/{employee_id}/timeline/{date}/
    
    Returns:
        {
            "date": "2025-01-15",
            "employee": {"id": 1, "full_name": "John Doe"},
            "blocks": [
                {
                    "type": "SCHEDULE",
                    "start": "08:00",
                    "end": "17:00",
                    "duration_minutes": 540,
                    ...
                },
                {
                    "type": "WORK",
                    "start": "08:07",
                    "end": "12:01",
                    "duration_minutes": 234,
                    ...
                }
            ]
        }
    """
    try:
        # Parse date
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {'error': 'Invalid date format. Use YYYY-MM-DD'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get employee
    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        return Response(
            {'error': 'Employee not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get timeline
    timeline_service = TimelineService()
    blocks = timeline_service.get_timeline(employee, date)
    
    if not blocks:
        return Response(
            {
                'error': 'No timeline found for this date',
                'hint': 'Timeline may not have been generated yet. Run attendance calculation first.'
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response({
        'date': date_str,
        'employee': {
            'id': employee.id,
            'full_name': employee.full_name,
        },
        'blocks': blocks,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_timeline_summary(request, employee_id, date_str):
    """
    Get summarized timeline statistics.
    
    GET /api/attendance/{employee_id}/timeline/{date}/summary/
    
    Returns:
        {
            "date": "2025-01-15",
            "total_work_minutes": 480,
            "total_gap_minutes": 60,
            "anomaly_count": 1,
            "blocks_count": 5
        }
    """
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {'error': 'Invalid date format. Use YYYY-MM-DD'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        return Response(
            {'error': 'Employee not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get timeline blocks
    from core.models_timeline import AttendanceTimelineBlock, BlockType
    
    blocks = AttendanceTimelineBlock.objects.filter(
        employee=employee,
        date=date
    )
    
    if not blocks.exists():
        return Response(
            {'error': 'No timeline found for this date'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Calculate summary
    total_work_minutes = sum(
        b.duration_minutes for b in blocks if b.block_type == BlockType.WORK
    )
    
    total_gap_minutes = sum(
        b.duration_minutes for b in blocks
        if b.block_type in [BlockType.GAP_PLANNED, BlockType.GAP_ANOMALY]
    )
    
    anomaly_count = blocks.filter(
        block_type=BlockType.GAP_ANOMALY
    ).count()
    
    return Response({
        'date': date_str,
        'total_work_minutes': total_work_minutes,
        'total_gap_minutes': total_gap_minutes,
        'anomaly_count': anomaly_count,
        'blocks_count': blocks.count(),
        'has_schedule': blocks.filter(block_type=BlockType.SCHEDULE).exists(),
        'has_tolerance': blocks.filter(block_type=BlockType.TOLERANCE).exists(),
    })
