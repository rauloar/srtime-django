"""
Attendance Application Service (RC1 - Simple Mode)

Flow:
resolve schedule → get logs → calculate → update_or_create
"""

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Optional, Tuple, List

from django.utils import timezone
from core import models
from core.domain.flexible import FlexPolicy, Punch
from core.domain.flexible.result import DailyCalculationResult

from .attendance_engine_v2 import (
    resolve_schedule,
    get_logs,
    get_holidays,
    check_employee_leave,
)
from .flexible_engine import calculate_flexible_day


# =============================================================================
# RESULT TYPES
# =============================================================================

class PersistenceStatus(Enum):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    ERROR = "ERROR"


@dataclass
class ProcessingResult:
    daily_attendance: Optional[models.DailyAttendance]
    status: PersistenceStatus
    message: str
    processed_at: Optional[datetime] = None


# =============================================================================
# APPLICATION SERVICE
# =============================================================================

class AttendanceApplicationService:

    def process_daily_attendance(
        self,
        employee_id: int,
        target_date: date,
    ) -> ProcessingResult:

        now = timezone.now()

        employee = models.Employee.objects.filter(id=employee_id).first()
        if not employee:
            return ProcessingResult(
                daily_attendance=None,
                status=PersistenceStatus.ERROR,
                message="Employee not found",
                processed_at=now,
            )

        context = self._gather_context(employee, target_date)
        result = self._execute_calculation(context)

        daily, created = models.DailyAttendance.objects.update_or_create(
            employee=employee,
            date=target_date,
            defaults={
                "check_in": result.check_in,
                "check_out": result.check_out,
                "worked_minutes": result.worked_minutes,
                "break_minutes": result.break_minutes,
                "net_worked_minutes": result.net_worked_minutes,
                "regular_minutes": result.regular_minutes,
                "overtime_minutes": result.overtime_minutes,
                "night_minutes": result.night_minutes,
                "late_minutes": result.late_minutes or 0,
                "early_minutes": result.early_out_minutes or 0,
                "status": result.status,
                "is_absent": result.status == "Absent",
                "timetable_id": result.timetable_id,
            },
        )

        status = PersistenceStatus.CREATED if created else PersistenceStatus.UPDATED

        return ProcessingResult(
            daily_attendance=daily,
            status=status,
            message=status.value,
            processed_at=now,
        )

    # =========================================================================

    def _gather_context(self, employee: models.Employee, target_date: date) -> dict:

        schedule_ctx = resolve_schedule(employee.id, target_date)

        if not schedule_ctx.is_valid:
            return {
                "has_schedule": False,
                "is_rest_day": True,
                "timetable": None,
                "logs": [],
                "holidays": set(),
                "has_leave": False,
                "policy": FlexPolicy(),
            }

        tt = schedule_ctx.timetable

        logs = []
        if employee.user_id and schedule_ctx.search_start and schedule_ctx.search_end:
            logs = get_logs(
                employee.user_id,
                schedule_ctx.search_start,
                schedule_ctx.search_end,
            )

        holidays = get_holidays(target_date)
        has_leave = check_employee_leave(employee.id, target_date)

        policy = FlexPolicy(
            break_threshold_minutes=360,
            break_duration_minutes=tt.break_minutes or 30,
            daily_regular_minutes=tt.required_minutes or 480,
            daily_max_minutes=720,
        )

        return {
            "has_schedule": True,
            "is_rest_day": False,
            "timetable": tt,
            "logs": logs,
            "holidays": holidays,
            "has_leave": has_leave,
            "policy": policy,
        }

    # =========================================================================

    def _execute_calculation(self, context: dict) -> DailyCalculationResult:

        if not context["has_schedule"]:
            return DailyCalculationResult(
                employee_id=0,
                target_date=date.today(),
                calculation_mode="FLEXIBLE",
                status="RestDay" if context["is_rest_day"] else "Absent",
            )

        tt = context["timetable"]
        logs = context["logs"]
        policy = context["policy"]
        holidays = context["holidays"]
        has_leave = context["has_leave"]

        punches = [
            Punch(
                id=log.id,
                timestamp=log.timestamp,
                device_id=str(log.device_id) if log.device_id else "UNKNOWN",
            )
            for log in logs
            if log.timestamp
        ]

        return calculate_flexible_day(
            employee_id=0,
            target_date=date.today(),
            punches=punches,
            policy=policy,
            holidays=list(holidays),
            has_leave=has_leave,
            is_rest_day=False,
        )


# =============================================================================
# SINGLETON
# =============================================================================

_application_service: Optional[AttendanceApplicationService] = None


def get_attendance_service() -> AttendanceApplicationService:
    global _application_service
    if _application_service is None:
        _application_service = AttendanceApplicationService()
    return _application_service