"""
Snapshot API Views
REST API endpoints for engine snapshots.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime

from core.models import Employee
from core.services.snapshot_service import EngineSnapshotService


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_engine_snapshot(request, employee_id, date_str):
    """
    Get engine snapshot for a specific day.
    
    GET /api/attendance/{employee_id}/snapshot/{date}/
    
    Returns:
        {
            "date": "2025-01-15",
            "engine_version": "V2",
            "inputs": {
                "punches": [...],
                "schedule": {...},
                "tolerances": {...}
            },
            "context": {
                "flexible_mode": false,
                "holiday": false,
                "absence_type": ""
            },
            "result": {
                "status": "PRESENT",
                "worked_minutes": 480,
                "expected_minutes": 480,
                "overtime_minutes": 0,
                "deficit_minutes": 0
            },
            "calculated_at": "2025-01-15T18:00:00Z"
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
    
    snapshot_service = EngineSnapshotService()
    snapshot = snapshot_service.get_snapshot(employee, date)
    
    if not snapshot:
        return Response(
            {
                'error': 'No snapshot found for this date',
                'hint': 'Snapshot may not have been created yet. Run attendance calculation first.'
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response(snapshot)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def compare_engine_snapshots(request, employee_id, date_str):
    """
    Compare snapshots between engine versions.
    
    GET /api/attendance/{employee_id}/snapshot/{date}/compare/?version_a=V1&version_b=V2
    
    Returns:
        {
            "date": "2025-01-15",
            "versions": {
                "V1": {
                    "status": "PRESENT",
                    "worked_minutes": 475,
                    "overtime_minutes": -5
                },
                "V2": {
                    "status": "PRESENT",
                    "worked_minutes": 480,
                    "overtime_minutes": 0
                }
            },
            "differences": {
                "status_changed": false,
                "minutes_diff": 5,
                "overtime_diff": 5
            }
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
    
    version_a = request.query_params.get('version_a', 'V1')
    version_b = request.query_params.get('version_b', 'V2')
    
    snapshot_service = EngineSnapshotService()
    comparison = snapshot_service.compare_snapshots(
        employee, date, version_a, version_b
    )
    
    if not comparison:
        return Response(
            {'error': f'Snapshots not found for versions {version_a} and {version_b}'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response(comparison)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_snapshot_history(request, employee_id):
    """
    Get snapshot history for an employee.
    
    GET /api/attendance/{employee_id}/snapshot/history/?days=30
    
    Returns:
        {
            "employee_id": 123,
            "snapshots": [
                {
                    "date": "2025-01-15",
                    "status": "PRESENT",
                    "worked_minutes": 480
                },
                ...
            ],
            "count": 30
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
    
    from core.models_engine_snapshot import AttendanceEngineSnapshot
    
    snapshots = AttendanceEngineSnapshot.objects.filter(
        employee=employee
    ).order_by('-date')[:days]
    
    snapshot_data = [
        {
            'date': str(s.date),
            'status': s.status,
            'worked_minutes': s.worked_minutes,
            'overtime_minutes': s.overtime_minutes,
            'engine_version': s.engine_version,
            'calculated_at': s.calculated_at.isoformat(),
        }
        for s in snapshots
    ]
    
    return Response({
        'employee_id': employee_id,
        'snapshots': snapshot_data,
        'count': len(snapshot_data),
    })
