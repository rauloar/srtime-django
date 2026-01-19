"""
Attendance Calculation Views
"""
from datetime import datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from core import models
from core.serializers import DailyAttendanceSerializer
from core.services import calculate_day, calculate_period


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_attendance(request):
    """
    POST /api/v1/attendance/calculate/
    Body: {
        "start_date": "2025-01-01",
        "end_date": "2025-01-07",
        "department_id": 1  // Optional
    }
    """
    start_date_str = request.data.get('start_date')
    end_date_str = request.data.get('end_date')
    department_id = request.data.get('department_id')
    
    if not start_date_str or not end_date_str:
        return Response(
            {"error": "start_date and end_date are required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response(
            {"error": "Invalid date format. Use YYYY-MM-DD"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    results = calculate_period(start_date, end_date, department_id)
    
    return Response({
        "message": f"Calculated {len(results)} records",
        "count": len(results)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def daily_reports(request):
    """
    GET /api/v1/attendance/reports/daily/?from_date=2025-01-01&to_date=2025-01-07&employee_id=1&department_id=1
    """
    from_date_str = request.query_params.get('from_date')
    to_date_str = request.query_params.get('to_date')
    employee_id = request.query_params.get('employee_id')
    department_id = request.query_params.get('department_id')
    
    if not from_date_str or not to_date_str:
        return Response(
            {"error": "from_date and to_date are required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response(
            {"error": "Invalid date format. Use YYYY-MM-DD"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    query = models.DailyAttendance.objects.filter(
        date__gte=from_date,
        date__lte=to_date
    )
    
    if employee_id:
        query = query.filter(employee_id=employee_id)
    
    if department_id:
        query = query.filter(employee__department_id=department_id)
    
    records = query.select_related('employee', 'timetable').order_by('-date')
    serializer = DailyAttendanceSerializer(records, many=True)
    
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_single_day(request, employee_id):
    """
    POST /api/v1/attendance/calculate/{employee_id}/
    Body: {
        "date": "2025-01-15"
    }
    """
    date_str = request.data.get('date')
    
    if not date_str:
        return Response(
            {"error": "date is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response(
            {"error": "Invalid date format. Use YYYY-MM-DD"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify employee exists
    employee = get_object_or_404(models.Employee, id=employee_id)
    
    # Calculate
    daily = calculate_day(employee_id, target_date)
    serializer = DailyAttendanceSerializer(daily)
    
    return Response(serializer.data)
