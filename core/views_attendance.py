"""
Attendance Calculation Views
"""
from datetime import datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, F, Sum, Avg
from core import models
from core.serializers import DailyAttendanceSerializer
from core.services import calculate_day, calculate_period
import json


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
    
    results, skipped_employees = calculate_period(start_date, end_date, department_id)
    
    # Agrupar empleados saltados por razón
    skipped_by_reason = {}
    for skip in skipped_employees:
        reason = skip['reason']
        if reason not in skipped_by_reason:
            skipped_by_reason[reason] = []
        skipped_by_reason[reason].append({
            'id': skip['employee_id'],
            'name': skip['name']
        })
    
    # Analizar causas de Absent entre los procesados
    absence_reasons = {}
    for record in results:
        if record.status == "Absent" and record.exception_reason:
            reason = record.exception_reason
            if reason not in absence_reasons:
                absence_reasons[reason] = {'count': 0, 'employees': set()}
            absence_reasons[reason]['count'] += 1
            absence_reasons[reason]['employees'].add(record.employee_id)
    
    # Convertir sets a listas para JSON
    for reason in absence_reasons:
        absence_reasons[reason]['employees'] = list(absence_reasons[reason]['employees'])
    
    return Response({
        "message": f"✅ Calculated {len(results)} records successfully",
        "summary": {
            "processed_records": len(results),
            "skipped_employees": len(skipped_employees),
            "total_employees_expected": len(skipped_employees) + len(set(r.employee_id for r in results))
        },
        "date_range": {
            "start": str(start_date),
            "end": str(end_date),
            "days": (end_date - start_date).days + 1
        },
        "skipped_employees": {
            "total": len(skipped_employees),
            "by_reason": skipped_by_reason
        },
        "processed_analysis": {
            "absence_reasons": absence_reasons,
            "note": "Employees marked absent either have no shift timetables configured, no logs for the period, or didn't check in"
        }
    })


@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def calculate_attendance_detailed(request):
    """
    POST /api/v1/attendance/calculate/detailed/
    Body: {
        "start_date": "2025-01-01",
        "end_date": "2025-01-07",
        "department_id": 1  // Optional
    }
    
    Returns detailed breakdown per employee with logs count
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
    
    results, skipped_employees = calculate_period(start_date, end_date, department_id)
    
    # Agrupar resultados por empleado
    employee_details = {}
    for record in results:
        emp_id = record.employee_id
        if emp_id not in employee_details:
            emp = models.Employee.objects.get(id=emp_id)
            employee_details[emp_id] = {
                'id': emp_id,
                'name': emp.name,
                'user_id': emp.user_id,
                'status': 'PROCESSED',
                'days_processed': 0,
                'days_present': 0,
                'days_absent': 0,
                'total_worked_minutes': 0,
                'sample_records': []
            }
        
        employee_details[emp_id]['days_processed'] += 1
        if record.status == "Present":
            employee_details[emp_id]['days_present'] += 1
        else:
            employee_details[emp_id]['days_absent'] += 1
        
        employee_details[emp_id]['total_worked_minutes'] += record.worked_minutes or 0
        
        # Guardar 3 primeros registros como sample
        if len(employee_details[emp_id]['sample_records']) < 3:
            employee_details[emp_id]['sample_records'].append({
                'date': str(record.date),
                'status': record.status,
                'worked_minutes': record.worked_minutes,
                'reason': record.exception_reason
            })
    
    # Skipped employees
    skipped_by_reason = {}
    for skip in skipped_employees:
        reason = skip['reason']
        if reason not in skipped_by_reason:
            skipped_by_reason[reason] = []
        skipped_by_reason[reason].append({
            'id': skip['employee_id'],
            'name': skip['name'],
            'user_id': skip.get('user_id', 'N/A')
        })
    
    return Response({
        "summary": {
            "total_processed_employees": len(employee_details),
            "total_skipped_employees": len(skipped_employees),
            "total_records": len(results),
            "date_range": f"{start_date} to {end_date}"
        },
        "skipped_employees": skipped_by_reason,
        "processed_employees": list(employee_details.values())
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

    # 1. Get Employee (OPCIÓN B: never 404)
    try:
        emp = models.Employee.objects.get(id=employee_id)
    except models.Employee.DoesNotExist:
        # Return 200 with empty payload (consistent with timeline/explanation)
        return Response({
            "employee_id": employee_id,
            "employee_name": None,
            "date": date_str,
            "status": "NoData",
            "worked_minutes": 0,
            "logs": []
        })

    emp_name = emp.name or "Unknown"

    # 2. Get Logs (Simple Query)
    logs_qs = models.AttendanceLog.objects.filter(
        user_id=str(emp.user_id),
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
