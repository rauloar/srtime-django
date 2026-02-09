"""
Shadow Mode Service for Dual-Engine Validation

Runs both V1 (production) and V2 (shadow) engines in parallel and compares results.
Shadow mode provides pre-migration validation without affecting production data.

ARCHITECTURE:
    Request → V1 Engine (official) → Save DailyAttendance
                    ↓
            Shadow Mode (parallel) → V2 Engine → Compare Results → Log Differences

GUARANTEES:
    - Shadow failures do NOT affect production calculations
    - All exceptions caught and logged, never propagated
    - No database modifications to production tables
    - Results stored only for audit/debugging
"""

import logging
from datetime import date, datetime, time
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, asdict

from django.conf import settings
from django.utils import timezone

from core import models
from core.services.schedule_resolver import resolve_schedule_unified, ScheduleSource

logger = logging.getLogger(__name__)
shadow_logger = logging.getLogger('attendance.shadow')


@dataclass
class ShadowComparison:
    """Result of V1 vs V2 comparison."""
    employee_id: int
    target_date: date
    
    # V1 (Production) Results
    v1_status: Optional[str]
    v1_worked_minutes: Optional[float]
    v1_late_minutes: Optional[float]
    v1_early_minutes: Optional[float]
    v1_error: Optional[str]
    
    # V2 (Shadow) Results
    v2_status: Optional[str]
    v2_worked_minutes: Optional[float]
    v2_late_minutes: Optional[float]
    v2_early_minutes: Optional[float]
    v2_error: Optional[str]
    
    # Comparison Results
    has_differences: bool
    differences: List[str]  # List of differences found
    comparison_timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


class ShadowModeService:
    """
    Manages shadow mode calculations and comparisons.
    
    Usage:
        shadow = ShadowModeService()
        comparison = shadow.validate_daily_calculation(employee, date, v1_attendance)
    """
    
    def __init__(self):
        self.enabled = getattr(settings, 'ATTENDANCE_SHADOW_ENABLED', False)
        self.log_level = getattr(settings, 'ATTENDANCE_SHADOW_LOG_LEVEL', 'WARNING')
    
    def validate_daily_calculation(
        self,
        employee_id: int,
        target_date: date,
        v1_daily_attendance: Optional[models.DailyAttendance] = None,
    ) -> Optional[ShadowComparison]:
        """
        Run shadow mode validation for a daily calculation.
        
        Args:
            employee_id: Employee ID
            target_date: Date to validate
            v1_daily_attendance: Official V1 DailyAttendance record (already saved)
        
        Returns:
            ShadowComparison with V1 vs V2 differences, or None if shadow disabled
        
        Note:
            Never raises exceptions. All errors logged and absorbed.
        """
        if not self.enabled:
            return None
        
        try:
            # Extract V1 results
            v1_results = self._extract_v1_results(v1_daily_attendance)
            
            # Run V2 calculation
            v2_results = self._execute_v2_calculation(employee_id, target_date)
            
            # Compare results
            comparison = self._compare_results(
                employee_id=employee_id,
                target_date=target_date,
                v1_results=v1_results,
                v2_results=v2_results,
            )
            
            # Log differences if any
            self._log_comparison(comparison)
            
            return comparison
            
        except Exception as e:
            logger.error(
                f"Shadow mode validation failed for employee {employee_id} on {target_date}: {e}",
                exc_info=True
            )
            return None
    
    def _extract_v1_results(
        self,
        daily_attendance: Optional[models.DailyAttendance],
    ) -> Dict[str, Any]:
        """Extract V1 calculation results."""
        if not daily_attendance:
            return {
                'status': None,
                'worked_minutes': None,
                'late_minutes': None,
                'early_minutes': None,
                'error': None,
            }
        
        return {
            'status': daily_attendance.status,
            'worked_minutes': daily_attendance.worked_minutes,
            'late_minutes': daily_attendance.late_minutes,
            'early_minutes': daily_attendance.early_minutes,
            'error': None,
        }
    
    def _execute_v2_calculation(
        self,
        employee_id: int,
        target_date: date,
    ) -> Dict[str, Any]:
        """
        Execute V2 engine calculation in shadow mode.
        
        For now, just returns status='PENDING' as shadow comparison.
        This is placeholder for when V2 engine is activated as shadow.
        """
        try:
            employee = models.Employee.objects.filter(id=employee_id).first()
            if not employee:
                return {'error': f'Employee {employee_id} not found'}
            
            # Get schedule using unified resolver
            schedule = resolve_schedule_unified(employee_id, target_date)
            
            # Get attendance logs for this day
            start_dt = datetime.combine(target_date, time.min)
            end_dt = datetime.combine(target_date, time.max)
            
            logs = models.AttendanceLog.objects.filter(
                employee=employee,
                log_date__range=[start_dt, end_dt],
            ).order_by('log_date')
            
            if not logs.exists():
                return {
                    'status': 'NO_LOGS',
                    'worked_minutes': 0,
                    'late_minutes': 0,
                    'early_minutes': 0,
                    'error': None,
                }
            
            # TODO: Call V2 engine when fully implemented
            # For now, shadow mode is logging-only
            return {
                'status': 'PENDING',
                'worked_minutes': None,
                'late_minutes': None,
                'early_minutes': None,
                'error': 'V2 engine shadow calculation not yet implemented',
            }
            
        except Exception as e:
            logger.error(
                f"V2 calculation execution failed for employee {employee_id}: {e}",
                exc_info=True
            )
            return {'error': str(e)}
    
    def _compare_results(
        self,
        employee_id: int,
        target_date: date,
        v1_results: Dict[str, Any],
        v2_results: Dict[str, Any],
    ) -> ShadowComparison:
        """Compare V1 and V2 results."""
        differences = []
        tolerance = 1  # 1 minute tolerance for rounding
        
        # Compare status
        if v1_results['status'] != v2_results['status']:
            differences.append(
                f"Status mismatch: V1={v1_results['status']}, V2={v2_results['status']}"
            )
        
        # Compare worked minutes
        v1_worked = v1_results.get('worked_minutes') or 0
        v2_worked = v2_results.get('worked_minutes') or 0
        if abs(v1_worked - v2_worked) > tolerance:
            differences.append(
                f"Worked minutes differ by {abs(v1_worked - v2_worked):.1f}min: V1={v1_worked}, V2={v2_worked}"
            )
        
        # Compare late minutes
        v1_late = v1_results.get('late_minutes') or 0
        v2_late = v2_results.get('late_minutes') or 0
        if abs(v1_late - v2_late) > tolerance:
            differences.append(
                f"Late minutes differ by {abs(v1_late - v2_late):.1f}min: V1={v1_late}, V2={v2_late}"
            )
        
        # Compare early minutes
        v1_early = v1_results.get('early_minutes') or 0
        v2_early = v2_results.get('early_minutes') or 0
        if abs(v1_early - v2_early) > tolerance:
            differences.append(
                f"Early minutes differ by {abs(v1_early - v2_early):.1f}min: V1={v1_early}, V2={v2_early}"
            )
        
        return ShadowComparison(
            employee_id=employee_id,
            target_date=target_date,
            v1_status=v1_results['status'],
            v1_worked_minutes=v1_worked,
            v1_late_minutes=v1_late,
            v1_early_minutes=v1_early,
            v1_error=v1_results.get('error'),
            v2_status=v2_results['status'],
            v2_worked_minutes=v2_worked,
            v2_late_minutes=v2_late,
            v2_early_minutes=v2_early,
            v2_error=v2_results.get('error'),
            has_differences=len(differences) > 0,
            differences=differences,
            comparison_timestamp=timezone.now(),
        )
    
    def _log_comparison(self, comparison: ShadowComparison) -> None:
        """Log comparison results."""
        if not comparison.has_differences:
            if self.log_level in ['DEBUG']:
                shadow_logger.debug(
                    f"[MATCH] Employee {comparison.employee_id} @ {comparison.target_date}: "
                    f"V1={comparison.v1_status}, V2={comparison.v2_status}"
                )
            return
        
        # Log differences
        message = (
            f"[DIFF] Employee {comparison.employee_id} @ {comparison.target_date}:\n"
            + "\n".join(f"  - {diff}" for diff in comparison.differences)
        )
        
        if self.log_level in ['DEBUG', 'INFO', 'WARNING']:
            shadow_logger.warning(message)
    
    @staticmethod
    def get_shadow_report(
        employee_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate a report of shadow mode comparisons.
        
        Note: Only available if shadow mode is enabled.
        """
        if not getattr(settings, 'ATTENDANCE_SHADOW_ENABLED', False):
            return []
        
        # This would query ShadowComparison records if we create them
        # For now, just return empty list - shadow data is only logged
        return []
