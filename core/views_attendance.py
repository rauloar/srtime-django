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
# @permission_classes([IsAuthenticated])
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
# @permission_classes([IsAuthenticated])
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
    
    records = query.select_related('employee').order_by('-date')
    serializer = DailyAttendanceSerializer(records, many=True)
    
    return Response(serializer.data)


@api_view(['POST'])
# @permission_classes([IsAuthenticated])
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


@api_view(['GET'])
# @permission_classes([AllowAny]) - already default but explicit is good documentation
def get_simple_day_view(request):
    """
    GET /api/v1/attendance/day/?employee_id=1&date=2026-02-02
    Simplified endpoint for Day View (No scheduling logic).
    """
    employee_id = request.query_params.get('employee_id')
    date_str = request.query_params.get('date')

    if not employee_id or not date_str:
        return Response({"error": "employee_id and date required"}, status=400)

    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response({"error": "Invalid date YYYY-MM-DD"}, status=400)

    # 1. Get Employee Name
    try:
        emp = models.Employee.objects.get(id=employee_id)
        emp_name = emp.name
    except models.Employee.DoesNotExist:
        emp_name = "Unknown"

    # 2. Get Logs (Simple Query)
    logs_qs = models.AttendanceLog.objects.filter(
        user_id=str(emp.user_id) if emp_name != "Unknown" else "-1", # Match by user_id string
        timestamp__date=target_date
    ).order_by('timestamp')

    logs_data = []
    for log in logs_qs:
        logs_data.append({
            "type": "IN" if len(logs_data) % 2 == 0 else "OUT", # Naive alternation
            "time": log.timestamp.strftime("%H:%M")
        })

    # 3. Calculate (Naive IN/OUT)
    status = "Absent"
    worked_minutes = 0

    if len(logs_qs) > 0:
        if len(logs_qs) == 1:
            status = "Partial"
        else:
            status = "Normal"
            # Calc diff between first and last
            start = logs_qs.first().timestamp
            end = logs_qs.last().timestamp
            diff = end - start
            worked_minutes = int(diff.total_seconds() / 60)

    return Response({
        "employee_id": employee_id,
        "employee_name": emp_name,
        "date": date_str,
        "status": status,
        "worked_minutes": worked_minutes,
        "logs": logs_data
    })
