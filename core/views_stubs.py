from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from datetime import datetime
from core import models

@api_view(['GET'])
@permission_classes([AllowAny])
def stub_timeline(request, user_id, date):
    """
    Timeline v1: Hechos cronológicos desde AttendanceLog.
    
    🎯 CONTRATO v1:
    - Fuente: AttendanceLog (eventos crudos del dispositivo ZKTeco)
    - Bloques: Pares consecutivos IN→OUT usando alternancia naive (índice par=IN, impar=OUT)
    - Tipo: "WORK" = período contínuo de actividad
    - SIN: Horarios, políticas, validaciones, inferencias, reglas de negocio
    
    GET /api/v1/attendance/{user_id}/timeline/{date}/
    
    Response (200 OK):
    {
      "blocks": [
        {
          "type": "WORK",
          "start_time": "HH:MM",
          "end_time": "HH:MM",
          "duration_minutes": int
        },
        ...
      ]
    }
    
    Casos edge:
    - Employee no existe → {"blocks": []}
    - Sin logs en fecha → {"blocks": []}
    - Cantidad impar de logs → ignora último (sin OUT correspondiente)
    
    ⚠️ LIMITACIONES CONOCIDAS:
    - Alternancia es NAIVE: no valida contra AttendanceLog.punch
    - No se consulta Timetable ni horarios configurados
    - No hay inferencias de tardanza ni ausencias
    - No se procesan campos punch/workstate/punch_source
    
    📌 ESTABLE DESDE: 2026-02-02 (v1 congelado)
    """
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return Response({"blocks": []})

    # Get employee with legacy fallback
    emp = None
    try:
        emp = models.Employee.objects.get(user_id=user_id)
    except models.Employee.DoesNotExist:
        if str(user_id).isdigit():
            try:
                emp = models.Employee.objects.get(id=int(user_id))
            except models.Employee.DoesNotExist:
                pass
                
    if not emp:
        return Response({"blocks": []})

    # Query logs (same as day view)
    logs_qs = models.AttendanceLog.objects.filter(
        user_id=str(emp.user_id),
        timestamp__date=target_date
    ).order_by('timestamp')

    # Generate blocks from IN/OUT pairs (naive alternation)
    blocks = []
    logs_list = list(logs_qs)
    
    for i in range(0, len(logs_list) - 1, 2):
        in_log = logs_list[i]
        out_log = logs_list[i + 1] if i + 1 < len(logs_list) else None
        
        if out_log:
            # Complete IN→OUT pair
            start_time = in_log.timestamp.strftime("%H:%M")
            end_time = out_log.timestamp.strftime("%H:%M")
            duration = int((out_log.timestamp - in_log.timestamp).total_seconds() / 60)
            
            blocks.append({
                "type": "WORK",
                "start_time": start_time,
                "end_time": end_time,
                "duration_minutes": duration
            })

    return Response({
        "blocks": blocks
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def stub_explanation(request, user_id, date):
    """
    Explanation mínima: narrativa de hechos desde AttendanceLog.
    Reutiliza misma lógica que /attendance/day/
    Sin políticas de horarios, solo descripción.
    """
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return Response({
            "summary": "Fecha inválida",
            "anomalies": [],
            "recommendations": []
        })

    # Get employee with legacy fallback
    emp = None
    try:
        emp = models.Employee.objects.get(user_id=user_id)
        emp_name = emp.name or "Unknown"
    except models.Employee.DoesNotExist:
        if str(user_id).isdigit():
            try:
                emp = models.Employee.objects.get(id=int(user_id))
                emp_name = emp.name or "Unknown"
            except models.Employee.DoesNotExist:
                pass

    if not emp:
        return Response({
            "summary": "Empleado no encontrado",
            "anomalies": [],
            "recommendations": []
        })

    # Query logs (same query as day view and timeline)
    logs_qs = models.AttendanceLog.objects.filter(
        user_id=str(emp.user_id),
        timestamp__date=target_date
    ).order_by('timestamp')

    # Calculate simple metrics (same as day view)
    log_count = logs_qs.count()
    
    if log_count == 0:
        status = "Absent"
        worked_minutes = 0
        summary = f"{emp_name} no registró marcaciones en esta fecha."
    elif log_count == 1:
        status = "Partial"
        worked_minutes = 0
        first_log = logs_qs.first()
        summary = f"{emp_name} registró solo 1 marcación a las {first_log.timestamp.strftime('%H:%M')}. Día incompleto."
    else:
        status = "Normal"
        first_log = logs_qs.first()
        last_log = logs_qs.last()
        diff = last_log.timestamp - first_log.timestamp
        worked_minutes = int(diff.total_seconds() / 60)
        worked_hours = round(worked_minutes / 60, 1)
        
        summary = (
            f"{emp_name} trabajó {worked_minutes} minutos ({worked_hours} horas). "
            f"Entrada: {first_log.timestamp.strftime('%H:%M')}, "
            f"Salida: {last_log.timestamp.strftime('%H:%M')}."
        )  # Aligned with ZKTime.Net flexible schedule model

    return Response({
        "summary": summary,
        "anomalies": [],  # Sin políticas por ahora
        "recommendations": []  # Sin reglas de negocio aún
    })
