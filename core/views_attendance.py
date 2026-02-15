"""
Attendance Calculation Views
"""
from datetime import datetime, date
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, F, Sum, Avg
from core import models
from core.serializers import DailyAttendanceSerializer, DailyAttendanceV2Serializer
from core.services import calculate_day, calculate_period
from core.services.schedule_resolver import validate_schedule_compliance
import json


class AttendanceAdminPermission(BasePermission):
    """Allow attendance admin actions for attendance_admin/admin_system groups."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or user.is_staff:
            return True
        return user.groups.filter(name__in=['attendance_admin', 'admin_system']).exists()


class AttendanceViewPermission(BasePermission):
    """Allow attendance read access for allowed groups."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or user.is_staff:
            return True
        return user.groups.filter(name__in=['attendance_admin', 'hr_manager', 'admin_system', 'viewer']).exists()


@api_view(['POST'])
@permission_classes([IsAuthenticated, AttendanceAdminPermission])
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
@permission_classes([IsAuthenticated, AttendanceAdminPermission])
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
@permission_classes([IsAuthenticated, AttendanceViewPermission])
def daily_reports(request):
    """
    GET /api/v1/attendance/reports/daily/?from_date=2025-01-01&to_date=2025-01-07&employee_id=1&department_id=1&employee_user_id=EMP001&employee_name=John
    
    Supports:
    - from_date, to_date: Date range (YYYY-MM-DD)
    - employee_id: Filter by specific employee
    - department_id: Filter by department
    - employee_user_id: Filter by employee user_id (exact or partial match)
    - employee_name: Filter by employee name (case-insensitive partial match)
    """
    from_date_str = request.query_params.get('from_date')
    to_date_str = request.query_params.get('to_date')
    employee_id = request.query_params.get('employee_id')
    department_id = request.query_params.get('department_id')
    user_id_search = request.query_params.get('employee_user_id')
    name_search = request.query_params.get('employee_name')
    
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
    
    # Build query with all filters
    from django.db.models import Q
    query = models.DailyAttendance.objects.filter(
        date__gte=from_date,
        date__lte=to_date
    )
    
    if employee_id:
        query = query.filter(employee_id=employee_id)
    
    if department_id:
        query = query.filter(employee__department_id=department_id)
    
    # Search filters (case-insensitive)
    if user_id_search:
        query = query.filter(employee__user_id__icontains=user_id_search)
    
    if name_search:
        query = query.filter(employee__name__icontains=name_search)
    
    records = query.select_related('employee', 'timetable').order_by('-date', 'employee')
    serializer = DailyAttendanceSerializer(records, many=True)
    
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, AttendanceViewPermission])
def daily_reports_v2(request):
    """
    GET /api/v2/attendance/reports/daily/?from_date=2025-01-01&to_date=2025-01-07&employee_id=1&department_id=1&employee_user_id=EMP001&employee_name=John
    
    VERSION 2 - CONTRATO FORMAL CON DOMINIO FUERTE
    
    Estructura garantizada:
    {
      "identity": { "id", "employee_id", "date" },
      "status": { "code" (UPPER_CASE), "label", "color" },
      "metrics": { "worked_minutes", "late_minutes", "early_minutes", "overtime_minutes" },
      "schedule": { "check_in", "check_out" },
      "employee": { "name", "user_id", "department_name" }
    }
    
    Reglas garantizadas:
    - Campos numéricos NUNCA null (fallback a 0)
    - status.code SIEMPRE en formato UPPER_CASE_WITH_UNDERSCORES
    - status.label y color SIEMPRE presentes
    - employee.name y user_id SIEMPRE presentes
    
    Soporta mismos filtros que v1:
    - from_date, to_date: Rango de fechas (YYYY-MM-DD)
    - employee_id: ID específico del empleado
    - department_id: ID del departamento
    - employee_user_id: user_id (búsqueda parcial case-insensitive)
    - employee_name: nombre (búsqueda parcial case-insensitive)
    
    DIFERENCIAS DE V1:
    - Estructura jerárquica, no campos planos
    - status es objeto, no string
    - Dominio fuerte, sin fallbacks defensivos en frontend
    - Backend garantiza integridad
    """
    from_date_str = request.query_params.get('from_date')
    to_date_str = request.query_params.get('to_date')
    employee_id = request.query_params.get('employee_id')
    department_id = request.query_params.get('department_id')
    user_id_search = request.query_params.get('employee_user_id')
    name_search = request.query_params.get('employee_name')
    
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
    
    # Build query with all filters (same as v1)
    from django.db.models import Q
    query = models.DailyAttendance.objects.filter(
        date__gte=from_date,
        date__lte=to_date
    )
    
    if employee_id:
        query = query.filter(employee_id=employee_id)
    
    if department_id:
        query = query.filter(employee__department_id=department_id)
    
    # Search filters (case-insensitive)
    if user_id_search:
        query = query.filter(employee__user_id__icontains=user_id_search)
    
    if name_search:
        query = query.filter(employee__name__icontains=name_search)
    
    records = query.select_related('employee', 'timetable').order_by('-date', 'employee')
    serializer = DailyAttendanceV2Serializer(records, many=True)
    
    return Response(serializer.data)



@api_view(['POST'])
@permission_classes([IsAuthenticated, AttendanceAdminPermission])
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
@permission_classes([IsAuthenticated, AttendanceViewPermission])
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


@api_view(['GET'])
@permission_classes([IsAuthenticated, AttendanceViewPermission])
def get_all_absences(request):
    """
    GET /api/v1/attendance/absences/
    Retorna tanto absences manuales (Leave) como detectadas (DailyAttendance con status='Absent')
    Query Params:
    - from_date: YYYY-MM-DD (para absences detectadas)
    - to_date: YYYY-MM-DD (para absences detectadas)
    - employee_id: integer
    - employee_user_id: string (icontains)
    - employee_name: string (icontains)
    """
    # 1. Obtener absences manuales (Leave)
    manual_absences = models.Leave.objects.select_related('employee').all()
    
    # 2. Obtener absences detectadas (DailyAttendance con status='Absent')
    detected_absences = models.DailyAttendance.objects.filter(
        status='Absent'
    ).select_related('employee').all()
    
    # 3. Aplicar filtros query params
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')
    employee_id = request.query_params.get('employee_id')
    employee_user_id = request.query_params.get('employee_user_id')
    employee_name = request.query_params.get('employee_name')
    
    if from_date:
        detected_absences = detected_absences.filter(date__gte=from_date)
    if to_date:
        detected_absences = detected_absences.filter(date__lte=to_date)
    if employee_id:
        manual_absences = manual_absences.filter(employee_id=int(employee_id))
        detected_absences = detected_absences.filter(employee_id=int(employee_id))
    if employee_user_id:
        manual_absences = manual_absences.filter(employee__user_id__icontains=employee_user_id)
        detected_absences = detected_absences.filter(employee__user_id__icontains=employee_user_id)
    if employee_name:
        manual_absences = manual_absences.filter(employee__name__icontains=employee_name)
        detected_absences = detected_absences.filter(employee__name__icontains=employee_name)
    
    # 4. Transformar absences manuales al formato unificado
    manual_data = []
    for leave in manual_absences:
        manual_data.append({
            'id': leave.id,
            'employee_id': leave.employee_id,
            'employee_name': leave.employee.name,
            'employee_user_id': leave.employee.user_id,
            'type': leave.leave_type,
            'source': 'Manual',  # Indica que es manual
            'start_date': leave.start_time.date().isoformat(),
            'end_date': leave.end_time.date().isoformat(),
            'reason': leave.reason or leave.leave_type,
            'status': leave.status,
        })
    
    # 5. Transformar absences detectadas al formato unificado
    detected_data = []
    for daily in detected_absences:
        detected_data.append({
            'id': f"detected_{daily.id}",  # Prefijo para evitar conflicto con IDs manuales
            'employee_id': daily.employee_id,
            'employee_name': daily.employee.name,
            'employee_user_id': daily.employee.user_id,
            'type': 'Detected Absence',
            'source': 'Detected',  # Indica que fue detectada automáticamente
            'start_date': daily.date.isoformat(),
            'end_date': daily.date.isoformat(),
            'reason': daily.exception_reason or 'No logs found',
            'status': 'Detected',
        })
    
    # 6. Combinar y ordenar
    all_absences = manual_data + detected_data
    all_absences.sort(key=lambda x: x['start_date'], reverse=True)
    
    return Response(all_absences)


@api_view(['GET'])
@permission_classes([IsAuthenticated, AttendanceViewPermission])
def get_logs_with_validation(request):
    """
    GET /api/v1/attendance/logs-validated/?employee_id=1&date=2026-02-09
    
    Endpoint aditivo que obtiene logs del día con validación de compliance.
    No modifica engines V1/V2, solo agrega capa de validación.
    
    REGLA DE ORO: Nunca devuelve 404, siempre 200. Sin errores en UI.
    
    Response (siempre 200 OK):
    {
        "employee": {
            "id": 1,
            "name": "Fulano",
            "department": "Administración",
            "user_id": "A001"
        },
        "date": "2026-02-09",
        "logs": [
            {"timestamp": "2026-02-09T16:00:00Z", "punch": 0, "time": "16:00"},
            {"timestamp": "2026-02-09T22:00:00Z", "punch": 1, "time": "22:00"}
        ],
        "validation": {
            "is_compliant": false,
            "warning": true,
            "message": "Horario marcado no correspondería",
            "discrepancy_type": "WRONG_HOURS",
            "expected_schedule": {
                "on_duty": "08:00",
                "off_duty": "16:00",
                "shift_name": "Turno Mañana",
                "source": "EMPLOYEE_SHIFT",
                "timetable_id": 1
            },
            "actual": {
                "in_time": "16:00",
                "out_time": "22:00",
                "duration": "06:00:00"
            }
        }
    }
    """
    employee_id = request.query_params.get('employee_id')
    date_str = request.query_params.get('date')
    
    # Validación de parámetros
    if not employee_id or not date_str:
        return Response({
            "employee": None,
            "date": date_str,
            "logs": [],
            "validation": None,
            "error": "employee_id and date (YYYY-MM-DD) required"
        }, status=status.HTTP_200_OK)
    
    # Validación del formato de fecha
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response({
            "employee": None,
            "date": date_str,
            "logs": [],
            "validation": None,
            "error": "Invalid date format. Use YYYY-MM-DD"
        }, status=status.HTTP_200_OK)
    
    # 1. Get Employee (sin 404 - retorna payload vacío)
    try:
        emp = models.Employee.objects.get(id=employee_id)
    except (models.Employee.DoesNotExist, ValueError):
        return Response({
            "employee": None,
            "date": date_str,
            "logs": [],
            "validation": None,
            "error": f"Employee {employee_id} not found"
        }, status=status.HTTP_200_OK)
    
    # 2. Get logs for the day (puede estar vacío, eso es OK)
    logs_qs = models.AttendanceLog.objects.filter(
        user_id=str(emp.user_id),
        timestamp__date=target_date
    ).order_by('timestamp')
    
    # Parse IN/OUT logs
    in_time = None
    out_time = None
    logs_data = []
    
    for log in logs_qs:
        log_time = log.timestamp
        punch_type = "IN" if log.punch == 0 else "OUT"
        
        logs_data.append({
            "timestamp": log.timestamp.isoformat(),
            "punch": log.punch,
            "time": log_time.strftime("%H:%M")
        })
        
        # Track IN/OUT for validation
        if log.punch == 0 and in_time is None:
            in_time = log_time
        elif log.punch == 1:
            out_time = log_time
    
    # 3. Validate compliance (sin errores - siempre devuelve ComplianceResult)
    compliance_result = validate_schedule_compliance(
        employee_id=employee_id,
        target_date=target_date,
        in_time=in_time,
        out_time=out_time
    )
    
    # Build response (siempre 200 OK, nunca 404)
    return Response({
        "employee": {
            "id": emp.id,
            "name": emp.name,
            "department": emp.department.name if emp.department else None,
            "user_id": emp.user_id
        },
        "date": date_str,
        "logs": logs_data,
        "validation": {
            "is_compliant": compliance_result.is_compliant,
            "warning": compliance_result.warning,
            "message": compliance_result.message,
            "discrepancy_type": compliance_result.discrepancy_type,
            "expected_schedule": compliance_result.expected_schedule,
            "actual": compliance_result.actual
        }
    }, status=status.HTTP_200_OK)
