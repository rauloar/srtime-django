"""
Shadow Comparison Service
Validates V2 engine against V1 production without affecting official data.

PURPOSE:
This service runs V2 calculations in "shadow mode" and stores comparison
results for pre-migration analysis. It does NOT affect production data.

ARCHITECTURE:
    V1 Official Flow                   Shadow Flow (Parallel)
    ================                   ====================
    calculate_day_v1() → save          run_shadow_for_day()
                                              ↓
                                       calculate_day_v2()
                                              ↓
                                       compare(v1, v2)
                                              ↓
                                       ShadowCalculation.create()

ISOLATION GUARANTEES:
- Shadow failures do NOT affect official calculations
- Shadow data is stored in separate table
- No signals, no side effects on production models
"""
import hashlib
import json
import logging
from datetime import date
from typing import Optional, Tuple, List

from django.utils import timezone

from core import models
from core.models_shadow import ShadowCalculation, DifferenceType
from core.models_audit import PolicySnapshot
from core.domain.flexible import FlexPolicy, Punch
from core.domain.flexible.result import DailyCalculationResult

# Import V2 engine (pure, no side effects)
from .flexible_engine import calculate_flexible_day
from .attendance_engine_v2 import resolve_schedule, get_logs, get_holidays, check_employee_leave


logger = logging.getLogger(__name__)


class ShadowComparisonService:
    """
    Service for running V2 engine in shadow mode and comparing with V1.
    
    USAGE:
        shadow = ShadowComparisonService()
        result = shadow.run_shadow_for_day(employee, date, v1_daily_attendance)
    
    GUARANTEES:
        - Never modifies production data
        - Never throws exceptions that break caller flow
        - All failures are logged and absorbed
    """
    
    ENGINE_VERSION = "2.0.0"
    
    def run_shadow_for_day(
        self,
        employee: models.Employee,
        target_date: date,
        v1_daily_attendance: models.DailyAttendance,
    ) -> Optional[ShadowCalculation]:
        """
        Run V2 calculation in shadow mode and compare with V1.
        
        Args:
            employee: Employee being calculated
            target_date: Date being calculated
            v1_daily_attendance: The official V1 result (already persisted)
        
        Returns:
            ShadowCalculation record if successful, None if failed
        
        Note:
            This method NEVER raises exceptions. All errors are logged.
        """
        try:
            # Step 1: Gather context (same as V2 would use in production)
            context = self._gather_context(employee, target_date)
            
            if context is None:
                logger.warning(f"Shadow: No context for {employee.id} @ {target_date}")
                return None
            
            # Step 2: Execute V2 calculation (pure, no side effects)
            v2_result = self._execute_v2_calculation(employee.id, target_date, context)
            
            if v2_result is None:
                logger.warning(f"Shadow: V2 calculation failed for {employee.id} @ {target_date}")
                return None
            
            # Step 3: Create policy snapshot (if not exists)
            policy_snapshot = self._create_policy_snapshot(context['policy'])
            
            # Step 4: Compute fingerprint
            fingerprint = self._compute_fingerprint(
                employee.id, 
                target_date, 
                context['punch_ids'],
                policy_snapshot.policy_hash if policy_snapshot else None
            )
            
            # Step 5: Compare and classify
            difference = v2_result.net_worked_minutes - v1_daily_attendance.worked_minutes
            diff_type = ShadowCalculation.classify_difference(difference)
            requires_review = diff_type in [DifferenceType.MAJOR, DifferenceType.CRITICAL]
            
            # Step 6: Create shadow record
            shadow = ShadowCalculation.objects.create(
                employee=employee,
                date=target_date,
                
                # V1 data
                v1_worked_minutes=v1_daily_attendance.worked_minutes,
                v1_overtime_minutes=v1_daily_attendance.overtime_minutes,
                v1_status=v1_daily_attendance.status,
                
                # V2 data
                v2_worked_minutes=v2_result.worked_minutes,
                v2_net_minutes=v2_result.net_worked_minutes,
                v2_regular_minutes=v2_result.regular_minutes,
                v2_overtime_minutes=v2_result.overtime_minutes,
                v2_night_minutes=v2_result.night_minutes,
                v2_status=v2_result.status,
                
                # Comparison
                difference_minutes=difference,
                difference_type=diff_type,
                requires_review=requires_review,
                
                # Traceability
                fingerprint_v2=fingerprint,
                engine_version=self.ENGINE_VERSION,
                policy_snapshot=policy_snapshot,
                v1_daily_attendance_id=v1_daily_attendance.id,
            )
            
            logger.info(
                f"Shadow: {employee.id} @ {target_date} → "
                f"diff={difference}min ({diff_type})"
            )
            
            return shadow
            
        except Exception as e:
            # CRITICAL: Never let shadow failures affect production
            logger.error(f"Shadow: Exception for {employee.id} @ {target_date}: {e}")
            return None
    
    # =========================================================================
    # PRIVATE - CONTEXT GATHERING
    # =========================================================================
    
    def _gather_context(self, employee: models.Employee, target_date: date) -> Optional[dict]:
        """Gather calculation context (same as production would use)."""
        try:
            schedule_ctx = resolve_schedule(employee.id, target_date)
            
            if not schedule_ctx.is_valid:
                return None
            
            tt = schedule_ctx.timetable
            
            # Get logs
            logs = []
            if employee.user_id:
                logs = get_logs(employee.user_id, schedule_ctx.search_start, schedule_ctx.search_end)
            
            # Get holidays
            holidays = get_holidays(target_date)
            
            # Check leave
            has_leave = check_employee_leave(employee.id, target_date)
            
            # Build policy
            policy = self._build_policy_from_timetable(tt)
            
            # Extract punch IDs for fingerprint
            punch_ids = sorted([log.id for log in logs])
            
            return {
                'timetable': tt,
                'logs': logs,
                'holidays': holidays,
                'has_leave': has_leave,
                'policy': policy,
                'punch_ids': punch_ids,
            }
            
        except Exception as e:
            logger.error(f"Shadow: Context gathering failed: {e}")
            return None
    
    def _build_policy_from_timetable(self, tt: models.Timetable) -> FlexPolicy:
        """Build FlexPolicy from timetable settings."""
        return FlexPolicy(
            break_threshold_minutes=360,
            break_duration_minutes=tt.break_minutes or 30,
            daily_regular_minutes=tt.required_minutes or 480,
            daily_max_minutes=720,
        )
    
    # =========================================================================
    # PRIVATE - V2 CALCULATION
    # =========================================================================
    
    def _execute_v2_calculation(
        self,
        employee_id: int,
        target_date: date,
        context: dict,
    ) -> Optional[DailyCalculationResult]:
        """Execute V2 calculation (pure, no persistence)."""
        try:
            logs = context['logs']
            policy = context['policy']
            holidays = context['holidays']
            has_leave = context['has_leave']
            
            # Convert logs to punches
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
            
            # Execute V2 engine
            result = calculate_flexible_day(
                employee_id=employee_id,
                target_date=target_date,
                punches=punches,
                policy=policy,
                holidays=list(holidays),
                has_leave=has_leave,
                is_rest_day=False,
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Shadow: V2 execution failed: {e}")
            return None
    
    # =========================================================================
    # PRIVATE - TRACEABILITY
    # =========================================================================
    
    def _create_policy_snapshot(self, policy: FlexPolicy) -> Optional[PolicySnapshot]:
        """Create or reuse policy snapshot."""
        try:
            policy_dict = {
                'daily_regular_minutes': policy.daily_regular_minutes,
                'daily_max_minutes': policy.daily_max_minutes,
                'break_threshold_minutes': policy.break_threshold_minutes,
                'break_duration_minutes': policy.break_duration_minutes,
                'night_start_hour': policy.night_start_hour,
                'night_end_hour': policy.night_end_hour,
            }
            
            snapshot, created = PolicySnapshot.get_or_create_from_policy(
                policy_dict=policy_dict,
                policy_type='FLEX',
                source='TIMETABLE',
            )
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Shadow: Policy snapshot failed: {e}")
            return None
    
    def _compute_fingerprint(
        self,
        employee_id: int,
        target_date: date,
        punch_ids: List[int],
        policy_hash: Optional[str],
    ) -> str:
        """Compute deterministic fingerprint for V2 calculation."""
        fingerprint_data = {
            'employee_id': employee_id,
            'target_date': target_date.isoformat(),
            'punch_ids': punch_ids,
            'engine_version': self.ENGINE_VERSION,
            'policy_hash': policy_hash or 'none',
        }
        
        json_str = json.dumps(fingerprint_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()


# Singleton instance
_shadow_service: Optional[ShadowComparisonService] = None


def get_shadow_service() -> ShadowComparisonService:
    """Get singleton shadow comparison service instance."""
    global _shadow_service
    if _shadow_service is None:
        _shadow_service = ShadowComparisonService()
    return _shadow_service
