"""
Adjustment Service
Applies operational adjustments to attendance data.

NO result modification - only base data corrections.
All adjustments trigger automatic recalculation.
"""
from typing import Optional
from datetime import datetime, time
import logging

from django.conf import settings
from django.utils import timezone
from django.db import transaction

from core.models_operational_adjustments import AttendanceAdjustment, FlexibleWorkRule


logger = logging.getLogger('operational.adjustments')


class AdjustmentService:
    """
    Service to apply operational adjustments.
    
    Philosophy:
    - Never modify calculation results directly
    - Only correct base data (punches, schedules)
    - Always recalculate after adjustment
    - Maintain operational audit trail
    """
    
    def apply_adjustment(
        self,
        adjustment: AttendanceAdjustment
    ) -> bool:
        """
        Apply an approved adjustment.
        
        Args:
            adjustment: AttendanceAdjustment instance (must be approved)
        
        Returns:
            True if successful, False otherwise
        """
        if not adjustment.approved:
            logger.warning(
                f"Attempted to apply unapproved adjustment {adjustment.id}"
            )
            return False
        
        if adjustment.applied:
            logger.warning(
                f"Adjustment {adjustment.id} already applied"
            )
            return False
        
        try:
            with transaction.atomic():
                # Apply the adjustment to base data
                if adjustment.adjustment_type == 'ADD_PUNCH':
                    self._add_punch(adjustment)
                
                elif adjustment.adjustment_type == 'REMOVE_PUNCH':
                    self._remove_punch(adjustment)
                
                elif adjustment.adjustment_type == 'EDIT_PUNCH':
                    self._edit_punch(adjustment)
                
                elif adjustment.adjustment_type == 'JUSTIFIED_ABSENCE':
                    self._mark_justified_absence(adjustment)
                
                elif adjustment.adjustment_type == 'FLEX_OVERRIDE':
                    # Flexible override may not need base data change
                    # Just mark the day for special processing
                    pass
                
                # Mark as applied
                adjustment.applied = True
                adjustment.applied_at = timezone.now()
                adjustment.save()
                
                # ALWAYS recalculate
                self._recalculate_day(adjustment.employee, adjustment.date)
                
                logger.info(
                    f"Applied adjustment {adjustment.id} for "
                    f"{adjustment.employee.employee_number} on {adjustment.date}"
                )
                
                return True
        
        except Exception as e:
            logger.error(
                f"Failed to apply adjustment {adjustment.id}: {e}"
            )
            return False
    
    def _add_punch(self, adjustment: AttendanceAdjustment) -> None:
        """Add a new punch."""
        from core.models import Punch
        
        if not adjustment.new_time:
            raise ValueError("new_time required for ADD_PUNCH")
        
        timestamp = datetime.combine(adjustment.date, adjustment.new_time)
        
        Punch.objects.create(
            employee=adjustment.employee,
            timestamp=timestamp,
            punch_type=adjustment.punch_type or 'IN',
            source='MANUAL_ADJUSTMENT',
            notes=f"Added via adjustment #{adjustment.id}: {adjustment.reason}"
        )
        
        logger.info(
            f"Added punch for {adjustment.employee.employee_number} "
            f"at {timestamp} ({adjustment.punch_type})"
        )
    
    def _remove_punch(self, adjustment: AttendanceAdjustment) -> None:
        """Remove an erroneous punch."""
        from core.models import Punch
        
        if not adjustment.original_time:
            raise ValueError("original_time required for REMOVE_PUNCH")
        
        # Find punch at original time
        punches = Punch.objects.filter(
            employee=adjustment.employee,
            timestamp__date=adjustment.date,
            timestamp__time=adjustment.original_time
        )
        
        if not punches.exists():
            raise ValueError(
                f"No punch found at {adjustment.original_time} on {adjustment.date}"
            )
        
        # Mark as deleted (or actually delete if preferred)
        for punch in punches:
            punch.is_deleted = True
            punch.deleted_reason = f"Adjustment #{adjustment.id}: {adjustment.reason}"
            punch.save()
        
        logger.info(
            f"Removed punch for {adjustment.employee.employee_number} "
            f"at {adjustment.original_time}"
        )
    
    def _edit_punch(self, adjustment: AttendanceAdjustment) -> None:
        """Edit punch time."""
        from core.models import Punch
        
        if not adjustment.original_time or not adjustment.new_time:
            raise ValueError("original_time and new_time required for EDIT_PUNCH")
        
        # Find punch at original time
        punches = Punch.objects.filter(
            employee=adjustment.employee,
            timestamp__date=adjustment.date,
            timestamp__time=adjustment.original_time
        )
        
        if not punches.exists():
            raise ValueError(
                f"No punch found at {adjustment.original_time} on {adjustment.date}"
            )
        
        punch = punches.first()
        
        # Update timestamp
        new_timestamp = datetime.combine(adjustment.date, adjustment.new_time)
        punch.timestamp = new_timestamp
        punch.notes = (
            f"{punch.notes or ''}\n"
            f"Edited via adjustment #{adjustment.id}: {adjustment.reason}"
        ).strip()
        punch.save()
        
        logger.info(
            f"Edited punch for {adjustment.employee.employee_number} "
            f"from {adjustment.original_time} to {adjustment.new_time}"
        )
    
    def _mark_justified_absence(self, adjustment: AttendanceAdjustment) -> None:
        """Mark absence as justified."""
        # This could create an absence record or flag
        # For now, just log it - specific implementation depends on absence model
        logger.info(
            f"Marked justified absence for {adjustment.employee.employee_number} "
            f"on {adjustment.date}: {adjustment.reason}"
        )
    
    def _recalculate_day(self, employee, date) -> None:
        """
        Trigger recalculation for the day.
        
        This is the CRITICAL step - adjustments must trigger recalculation.
        """
        try:
            # Import here to avoid circular dependency
            from core.services.attendance_engine_v2 import AttendanceEngineV2
            
            engine = AttendanceEngineV2()
            
            # Get punches and schedule
            from core.models import Punch, Schedule
            
            punches = Punch.objects.filter(
                employee=employee,
                timestamp__date=date,
                is_deleted=False
            ).order_by('timestamp')
            
            schedule = Schedule.objects.filter(
                employee=employee,
                active=True
            ).first()
            
            # Recalculate
            result = engine.calculate_day(
                employee=employee,
                date=date,
                punches=list(punches),
                schedule=schedule
            )
            
            logger.info(
                f"Recalculated {employee.employee_number} on {date}: "
                f"status={result.get('status')}, "
                f"worked={result.get('worked_minutes')}min"
            )
        
        except Exception as e:
            logger.error(
                f"Failed to recalculate {employee.employee_number} on {date}: {e}"
            )
            # Re-raise to ensure adjustment transaction fails
            raise
    
    def get_pending_adjustments(self, employee=None) -> list:
        """Get adjustments pending approval."""
        queryset = AttendanceAdjustment.objects.filter(
            approved=False,
            applied=False
        )
        
        if employee:
            queryset = queryset.filter(employee=employee)
        
        return list(queryset.order_by('-created_at'))
    
    def approve_adjustment(
        self,
        adjustment: AttendanceAdjustment,
        approved_by_user
    ) -> bool:
        """
        Approve an adjustment.
        
        Does NOT apply it - application is separate step.
        """
        if adjustment.approved:
            logger.warning(f"Adjustment {adjustment.id} already approved")
            return False
        
        adjustment.approved = True
        adjustment.approved_by = approved_by_user
        adjustment.approved_at = timezone.now()
        adjustment.save()
        
        logger.info(
            f"Approved adjustment {adjustment.id} by {approved_by_user.username}"
        )
        
        return True
    
    def get_flexible_rule(
        self,
        employee,
        date
    ) -> Optional[FlexibleWorkRule]:
        """Get active flexible work rule for employee on date."""
        rules = FlexibleWorkRule.objects.filter(
            employee=employee,
            active=True,
            effective_from__lte=date
        ).filter(
            models.Q(effective_to__isnull=True) | models.Q(effective_to__gte=date)
        ).order_by('-effective_from')
        
        return rules.first()


# Import for filtering
from django.db import models
