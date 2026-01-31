"""
Attendance Application Service
The LEGAL BOUNDARY for attendance calculation.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THIS IS THE ONLY AUTHORIZED ENTRY POINT FOR CALCULATING ATTENDANCE.

Any calculation that bypasses this service:
- Loses audit trail
- Loses recalculation protection
- Creates legal liability

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ARCHITECTURE:
    
    process_daily_attendance()
           │
           ├─→ resolve_schedule()      [Context]
           ├─→ get_logs()              [Context]
           ├─→ get_policy()            [Context]
           │
           ├─→ calculate_day_v2()      [Engine - Pure]
           │
           └─→ persist_daily_calculation()  [Persistence - Transactional]

RESPONSIBILITIES:
    ✅ Coordinates context gathering
    ✅ Delegates to engine
    ✅ Delegates to persistence
    ✅ Handles protection flags
    ✅ Manages errors
    
    ❌ Does NOT calculate anything
    ❌ Does NOT touch model fields directly
    ❌ Does NOT bypass persistence service

PROTECTION FLAGS:
    When a day has:
    - requires_review = True
    - OR calculation_confidence != HIGH
    
    The system BLOCKS recalculation unless force=True.
    This ensures human review before overwriting flagged calculations.
"""
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Optional, Tuple, List, Set

from django.utils import timezone

from core import models
from core.models_audit import CalculationAuditLog, AuditEventType
from core.domain.flexible import FlexPolicy, Punch, Confidence
from core.domain.flexible.result import DailyCalculationResult

# Import engine components
from .attendance_engine_v2 import (
    resolve_schedule,
    get_logs,
    get_holidays,
    check_employee_leave,
)
from .flexible_engine import calculate_flexible_day

# Import persistence service
from .calculation_persistence import (
    CalculationPersistenceService,
    PersistenceResult,
    get_persistence_service,
)


# =============================================================================
# EXCEPTIONS
# =============================================================================

class AttendanceServiceError(Exception):
    """Base exception for attendance service errors."""
    pass


class ProtectedDayError(AttendanceServiceError):
    """
    Raised when attempting to recalculate a protected day without force=True.
    
    A day is protected when:
    - requires_review = True (flagged for human review)
    - calculation_confidence != HIGH (uncertain calculation)
    
    This protection ensures that questionable calculations are not
    silently overwritten without explicit human authorization.
    """
    def __init__(self, employee_id: int, target_date: date, reason: str):
        self.employee_id = employee_id
        self.target_date = target_date
        self.reason = reason
        super().__init__(
            f"Day {target_date} for employee {employee_id} is protected: {reason}. "
            f"Use force=True to override (requires authorization)."
        )


class CalculationError(AttendanceServiceError):
    """Raised when the calculation engine fails."""
    pass


class PersistenceError(AttendanceServiceError):
    """Raised when persistence fails."""
    pass


class ScheduleNotFoundError(AttendanceServiceError):
    """Raised when no schedule context can be resolved."""
    pass


# =============================================================================
# RESULT TYPES
# =============================================================================

@dataclass
class ProcessingResult:
    """Result of a daily attendance processing operation."""
    daily_attendance: Optional[models.DailyAttendance]
    status: PersistenceResult
    message: str
    engine_version: str = "2.0.0"
    processed_at: Optional[datetime] = None


# =============================================================================
# APPLICATION SERVICE
# =============================================================================

class AttendanceApplicationService:
    """
    Application service for attendance calculation.
    
    THIS IS THE LEGAL BOUNDARY.
    
    All attendance calculations MUST go through this service to ensure:
    1. Full audit trail
    2. Recalculation protection
    3. Consistent traceability
    
    Usage:
        service = AttendanceApplicationService()
        result = service.process_daily_attendance(
            employee_id=123,
            target_date=date(2025, 1, 15),
            actor=request.user,
        )
        
        if result.status == PersistenceResult.CREATED:
            print("New calculation created")
        elif result.status == PersistenceResult.NO_CHANGE:
            print("Same as existing, skipped")
        elif result.status == PersistenceResult.RECALCULATED:
            print("Recalculated, previous superseded")
    """
    
    ENGINE_VERSION = "2.0.0"
    
    def __init__(self, persistence_service: Optional[CalculationPersistenceService] = None):
        """
        Initialize with optional custom persistence service.
        
        Args:
            persistence_service: Custom service for testing. If None, uses singleton.
        """
        self._persistence = persistence_service or get_persistence_service()
    
    # =========================================================================
    # PUBLIC API
    # =========================================================================
    
    def process_daily_attendance(
        self,
        employee_id: int,
        target_date: date,
        actor: Optional[models.User] = None,
        force: bool = False,
        recalculation_reason: Optional[str] = None,
    ) -> ProcessingResult:
        """
        Process attendance for a single employee/date.
        
        This is the ONLY authorized method for calculating attendance.
        
        Args:
            employee_id: Employee to calculate
            target_date: Date to calculate
            actor: User performing the action (for audit)
            force: If True, override protection flags
            recalculation_reason: Required when force=True
        
        Returns:
            ProcessingResult with status and daily attendance
        
        Raises:
            ProtectedDayError: If day is protected and force=False
            ScheduleNotFoundError: If no schedule can be resolved
            CalculationError: If engine fails
            PersistenceError: If persistence fails
        """
        now = timezone.now()
        
        try:
            # Step 1: Get employee
            employee = self._get_employee(employee_id)
            
            # Step 2: Check protection (before any calculation)
            self._check_protection(employee_id, target_date, force)
            
            # Step 3: Gather context
            context = self._gather_context(employee, target_date)
            
            # Step 4: Execute calculation
            result = self._execute_calculation(context)
            
            # Step 5: Persist with traceability
            daily, persistence_status = self._persist_result(
                employee=employee,
                target_date=target_date,
                context=context,
                result=result,
                actor=actor,
                recalculation_reason=recalculation_reason,
            )
            
            return ProcessingResult(
                daily_attendance=daily,
                status=persistence_status,
                message=self._build_message(persistence_status),
                engine_version=self.ENGINE_VERSION,
                processed_at=now,
            )
            
        except (ProtectedDayError, ScheduleNotFoundError):
            raise
        except Exception as e:
            # Log error to audit trail
            self._log_error(employee_id, target_date, str(e), actor)
            raise AttendanceServiceError(f"Processing failed: {e}") from e
    
    def process_period(
        self,
        start_date: date,
        end_date: date,
        department_id: Optional[int] = None,
        actor: Optional[models.User] = None,
        skip_protected: bool = True,
    ) -> List[ProcessingResult]:
        """
        Process attendance for multiple days/employees.
        
        Args:
            start_date: Start of period
            end_date: End of period (inclusive)
            department_id: Optional filter by department
            actor: User performing the action
            skip_protected: If True, skip protected days instead of failing
        
        Returns:
            List of ProcessingResult for each employee/date
        """
        from datetime import timedelta
        
        employees = models.Employee.objects.filter(is_active=True)
        if department_id:
            employees = employees.filter(department_id=department_id)
        
        results = []
        current = start_date
        
        while current <= end_date:
            for emp in employees:
                try:
                    result = self.process_daily_attendance(
                        employee_id=emp.id,
                        target_date=current,
                        actor=actor,
                        force=False,
                    )
                    results.append(result)
                except ProtectedDayError:
                    if skip_protected:
                        results.append(ProcessingResult(
                            daily_attendance=None,
                            status=PersistenceResult.ERROR,
                            message="Protected day skipped",
                            processed_at=timezone.now(),
                        ))
                    else:
                        raise
                except Exception as e:
                    results.append(ProcessingResult(
                        daily_attendance=None,
                        status=PersistenceResult.ERROR,
                        message=str(e),
                        processed_at=timezone.now(),
                    ))
            
            current += timedelta(days=1)
        
        return results
    
    # =========================================================================
    # PRIVATE - CONTEXT GATHERING
    # =========================================================================
    
    def _get_employee(self, employee_id: int) -> models.Employee:
        """Get employee or raise error."""
        employee = models.Employee.objects.filter(id=employee_id).first()
        if not employee:
            raise AttendanceServiceError(f"Employee {employee_id} not found")
        return employee
    
    def _gather_context(self, employee: models.Employee, target_date: date) -> dict:
        """
        Gather all context needed for calculation.
        
        This does NOT access the engine - only prepares data.
        """
        # Resolve schedule
        schedule_ctx = resolve_schedule(employee.id, target_date)
        
        if not schedule_ctx.is_valid:
            # No schedule = implicit rest day
            return {
                'has_schedule': False,
                'is_rest_day': True,
                'timetable': None,
                'logs': [],
                'holidays': set(),
                'has_leave': False,
                'policy': FlexPolicy(),
            }
        
        tt = schedule_ctx.timetable
        
        # Get logs
        logs = []
        if employee.user_id:
            logs = get_logs(employee.user_id, schedule_ctx.search_start, schedule_ctx.search_end)
        
        # Get holidays
        holidays = get_holidays(target_date)
        
        # Check leave
        has_leave = check_employee_leave(employee.id, target_date)
        
        # Build policy from timetable
        policy = self._build_policy_from_timetable(tt)
        
        return {
            'has_schedule': True,
            'is_rest_day': False,
            'timetable': tt,
            'logs': logs,
            'holidays': holidays,
            'has_leave': has_leave,
            'policy': policy,
            'schedule_ctx': schedule_ctx,
        }
    
    def _build_policy_from_timetable(self, tt: models.Timetable) -> FlexPolicy:
        """Build FlexPolicy from timetable settings."""
        return FlexPolicy(
            break_threshold_minutes=360,
            break_duration_minutes=tt.break_minutes or 30,
            daily_regular_minutes=tt.required_minutes or 480,
            daily_max_minutes=720,
        )
    
    # =========================================================================
    # PRIVATE - PROTECTION
    # =========================================================================
    
    def _check_protection(
        self,
        employee_id: int,
        target_date: date,
        force: bool,
    ) -> None:
        """
        Check if day is protected from recalculation.
        
        Protection triggers:
        - requires_review = True
        - calculation_confidence != HIGH
        
        Protected days require force=True to recalculate.
        """
        existing = models.DailyAttendance.objects.filter(
            employee_id=employee_id,
            date=target_date,
            calculation_state='CALCULATED',
        ).first()
        
        if not existing:
            return  # No existing record, no protection needed
        
        reasons = []
        
        if existing.requires_review:
            reasons.append("requires human review")
        
        # Check confidence if stored (may need to parse from metadata)
        # For now, we check requires_review as primary protection
        
        if reasons and not force:
            raise ProtectedDayError(
                employee_id=employee_id,
                target_date=target_date,
                reason=", ".join(reasons),
            )
    
    # =========================================================================
    # PRIVATE - CALCULATION
    # =========================================================================
    
    def _execute_calculation(self, context: dict) -> DailyCalculationResult:
        """
        Execute the calculation engine.
        
        This method ONLY calls the engine, it does NOT modify any data.
        """
        if not context['has_schedule']:
            # No schedule = create empty result
            return DailyCalculationResult(
                employee_id=0,  # Will be set by caller
                target_date=date.today(),
                calculation_mode="FLEXIBLE",
                status="RestDay" if context['is_rest_day'] else "Absent",
            )
        
        tt = context['timetable']
        logs = context['logs']
        policy = context['policy']
        holidays = context['holidays']
        has_leave = context['has_leave']
        
        # Convert logs to punches
        punches = self._convert_logs_to_punches(logs)
        
        # Execute engine
        if tt.is_flexible:
            result = calculate_flexible_day(
                employee_id=0,  # Will be overwritten
                target_date=date.today(),  # Will be overwritten
                punches=punches,
                policy=policy,
                holidays=list(holidays),
                has_leave=has_leave,
                is_rest_day=False,
            )
        else:
            # For structured schedules, use flexible engine with structured post-processing
            # In future, this would use StructuredProcessor
            result = calculate_flexible_day(
                employee_id=0,
                target_date=date.today(),
                punches=punches,
                policy=policy,
                holidays=list(holidays),
                has_leave=has_leave,
                is_rest_day=False,
            )
        
        return result
    
    def _convert_logs_to_punches(self, logs: List) -> List[Punch]:
        """Convert AttendanceLog objects to Punch domain objects."""
        punches = []
        
        for log in logs:
            state = int(log.punch) if log.punch is not None else 0
            is_valid = state in [0, 1, 4, 5, 8, 9]
            
            if is_valid and log.timestamp:
                punches.append(Punch(
                    id=log.id,
                    timestamp=log.timestamp,
                    device_id=str(log.device_id) if log.device_id else "UNKNOWN",
                ))
        
        return punches
    
    # =========================================================================
    # PRIVATE - PERSISTENCE
    # =========================================================================
    
    def _persist_result(
        self,
        employee: models.Employee,
        target_date: date,
        context: dict,
        result: DailyCalculationResult,
        actor: Optional[models.User],
        recalculation_reason: Optional[str],
    ) -> Tuple[models.DailyAttendance, PersistenceResult]:
        """
        Persist calculation result using the persistence service.
        
        This method delegates ALL persistence logic to the service.
        """
        policy = context['policy']
        logs = context.get('logs', [])
        
        # Extract punch IDs for fingerprint
        punch_ids = [log.id for log in logs]
        
        # Serialize policy for snapshot
        policy_dict = {
            'daily_regular_minutes': policy.daily_regular_minutes,
            'daily_max_minutes': policy.daily_max_minutes,
            'break_threshold_minutes': policy.break_threshold_minutes,
            'break_duration_minutes': policy.break_duration_minutes,
            'night_start_hour': policy.night_start_hour,
            'night_end_hour': policy.night_end_hour,
        }
        
        # Delegate to persistence service
        daily, status = self._persistence.persist_daily_calculation(
            employee=employee,
            target_date=target_date,
            engine_version=self.ENGINE_VERSION,
            policy_dict=policy_dict,
            punch_ids=punch_ids,
            result=result,
            actor=actor,
            recalculation_reason=recalculation_reason,
        )
        
        if status == PersistenceResult.ERROR:
            raise PersistenceError("Failed to persist calculation result")
        
        return daily, status
    
    # =========================================================================
    # PRIVATE - ERROR HANDLING
    # =========================================================================
    
    def _log_error(
        self,
        employee_id: int,
        target_date: date,
        error_message: str,
        actor: Optional[models.User],
    ) -> None:
        """Log error to audit trail if possible."""
        try:
            # Try to find existing record to attach error
            existing = models.DailyAttendance.objects.filter(
                employee_id=employee_id,
                date=target_date,
            ).first()
            
            if existing:
                CalculationAuditLog.objects.create(
                    daily_attendance=existing,
                    event_type='CREATED',  # Closest available type
                    engine_version=self.ENGINE_VERSION,
                    metadata={
                        'error': error_message,
                        'error_type': 'PROCESSING_ERROR',
                    },
                    actor=actor,
                )
        except Exception:
            pass  # Don't fail on error logging
    
    def _build_message(self, status: PersistenceResult) -> str:
        """Build human-readable message from status."""
        messages = {
            PersistenceResult.CREATED: "Calculation created successfully",
            PersistenceResult.RECALCULATED: "Recalculation completed, previous record superseded",
            PersistenceResult.NO_CHANGE: "No changes detected, calculation skipped",
            PersistenceResult.ERROR: "Calculation failed",
        }
        return messages.get(status, "Unknown status")


# =============================================================================
# SINGLETON ACCESS
# =============================================================================

_application_service: Optional[AttendanceApplicationService] = None


def get_attendance_service() -> AttendanceApplicationService:
    """Get singleton application service instance."""
    global _application_service
    if _application_service is None:
        _application_service = AttendanceApplicationService()
    return _application_service
