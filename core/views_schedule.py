"""
Schedule Calendar View

Simple APIView for schedule calendar endpoint.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from datetime import datetime
import logging

from core.services.schedule_calendar import get_schedule_calendar

logger = logging.getLogger(__name__)


class ScheduleCalendarView(APIView):
    """
    GET /api/v1/attendance/schedule/
    
    Query params:
        - start_date (required): YYYY-MM-DD
        - end_date (required): YYYY-MM-DD
        - employee_ids (optional): comma-separated IDs
    
    Returns:
        {
            "employees": [
                {
                    "id": 1,
                    "name": "Juan",
                    "schedule": [...]
                }
            ]
        }
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        # Parse dates
        start_str = request.query_params.get('start_date')
        end_str = request.query_params.get('end_date')
        
        if not start_str or not end_str:
            return Response(
                {"error": "start_date and end_date required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse employee_ids (optional)
        employee_ids = None
        employee_ids_str = request.query_params.get('employee_ids')
        if employee_ids_str:
            try:
                employee_ids = [int(x.strip()) for x in employee_ids_str.split(',')]
            except ValueError:
                return Response(
                    {"error": "Invalid employee_ids format"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Call service
        try:
            data = get_schedule_calendar(start_date, end_date, employee_ids)
            return Response(data)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Schedule calendar error: {e}", exc_info=True)
            return Response(
                {"error": "Internal error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
