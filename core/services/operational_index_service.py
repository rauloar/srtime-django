"""
Operational Index Service
Builds fast index for operational attendance review.

NO calculation, NO result modification.
Only indexing for HR queries.
"""
from typing import Dict, Any, List, Optional
import logging

from django.conf import settings
from django.utils import timezone

from core.models_operational_index import AttendanceDayIndex


logger = logging.getLogger('operational.index')


class OperationalIndexService:
    """
    Service to build operational index for attendance days.
    
    Purpose: Create fast queryable index for HR review.
    NOT for modifying calculations, only for finding issues.
    """
    
    def __init__(self):
        self.enabled = getattr(settings, 'OPERATIONAL_INDEX_ENABLED', True)
    
    def build_day_index(
        self,
        employee,
        date,
        result: Dict[str, Any],
        explanation: Optional[Any] = None,
        timeline_blocks: Optional[List[Any]] = None,
    ) -> Optional[AttendanceDayIndex]:
        """
        Build operational index for a day.
        
        Args:
            employee: Employee instance
            date: Calculation date
            result: Calculation result from engine
            explanation: AttendanceExplanation instance (optional)
            timeline_blocks: List of timeline blocks (optional)
        
        Returns:
            AttendanceDayIndex instance or None if disabled
        """
        if not self.enabled:
            return None
        
        try:
            # Extract anomalies from explanation
            anomalies = []
            if explanation:
                anomalies = getattr(explanation, 'anomalies', [])
            
            # Check timeline for gaps
            has_gaps = False
            has_unclassified = False
            
            if timeline_blocks:
                for block in timeline_blocks:
                    block_type = getattr(block, 'block_type', None)
                    if block_type == 'GAP_ANOMALY':
                        has_gaps = True
                    elif block_type == 'GAP_UNCLASSIFIED':
                        has_unclassified = True
            
            # Determine if requires attention
            requires_attention = self._should_require_attention(
                status=result.get('status', 'UNKNOWN'),
                anomalies=anomalies,
                has_gaps=has_gaps,
                has_unclassified=has_unclassified,
                minutes_diff=result.get('worked_minutes', 0) - result.get('expected_minutes', 0)
            )
            
            # Create or update index
            index, created = AttendanceDayIndex.objects.update_or_create(
                employee=employee,
                date=date,
                defaults={
                    'status': result.get('status', 'UNKNOWN'),
                    'worked_minutes': result.get('worked_minutes', 0),
                    'expected_minutes': result.get('expected_minutes', 0),
                    'has_anomalies': bool(anomalies),
                    'anomaly_count': len(anomalies),
                    'has_gaps': has_gaps,
                    'has_unclassified_time': has_unclassified,
                    'requires_attention': requires_attention,
                }
            )
            
            action = 'Created' if created else 'Updated'
            logger.info(
                f"{action} index for {employee.employee_number} on {date} "
                f"(requires_attention={requires_attention})"
            )
            
            return index
        
        except Exception as e:
            logger.error(
                f"Failed to build index for {employee.id} on {date}: {e}"
            )
            # Don't raise - index failure should not break calculations
            return None
    
    def _should_require_attention(
        self,
        status: str,
        anomalies: list,
        has_gaps: bool,
        has_unclassified: bool,
        minutes_diff: int
    ) -> bool:
        """
        Determine if day requires HR attention.
        
        Requires attention if:
        - Status is not normal (PRESENT, OK)
        - Has anomalies
        - Has anomalous gaps
        - Has unclassified time
        - Large time deficit (>30 min)
        """
        # Status-based
        normal_statuses = ['PRESENT', 'OK', 'COMPLETE']
        if status not in normal_statuses:
            return True
        
        # Anomalies
        if anomalies:
            return True
        
        # Timeline issues
        if has_gaps or has_unclassified:
            return True
        
        # Significant time deficit
        if minutes_diff < -30:  # More than 30 minutes deficit
            return True
        
        return False
    
    def get_days_requiring_attention(
        self,
        from_date,
        to_date,
        employee=None
    ) -> List[Dict[str, Any]]:
        """
        Get days requiring HR attention.
        
        Args:
            from_date: Start date
            to_date: End date
            employee: Optional employee filter
        
        Returns:
            List of day index dictionaries
        """
        queryset = AttendanceDayIndex.objects.filter(
            date__gte=from_date,
            date__lte=to_date,
            requires_attention=True
        )
        
        if employee:
            queryset = queryset.filter(employee=employee)
        
        queryset = queryset.order_by('-date')
        
        return [index.to_dict() for index in queryset]
    
    def get_employee_overview(
        self,
        employee,
        days=30
    ) -> Dict[str, Any]:
        """
        Get employee overview for recent days.
        
        Returns:
            {
                'total_days': 30,
                'days_with_anomalies': 5,
                'total_deficit_minutes': 120,
                'total_overtime_minutes': 45,
                'requires_attention_count': 3,
                ...
            }
        """
        from datetime import timedelta
        from django.utils import timezone
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        indices = AttendanceDayIndex.objects.filter(
            employee=employee,
            date__gte=start_date,
            date__lte=end_date
        )
        
        total_days = indices.count()
        days_with_anomalies = indices.filter(has_anomalies=True).count()
        requires_attention = indices.filter(requires_attention=True).count()
        
        # Calculate deficit/overtime
        total_deficit = 0
        total_overtime = 0
        
        for index in indices:
            diff = index.minutes_difference
            if diff < 0:
                total_deficit += abs(diff)
            elif diff > 0:
                total_overtime += diff
        
        return {
            'employee_id': employee.id,
            'employee_name': employee.full_name,
            'period_days': days,
            'total_days_indexed': total_days,
            'days_with_anomalies': days_with_anomalies,
            'days_requiring_attention': requires_attention,
            'total_deficit_minutes': total_deficit,
            'total_overtime_minutes': total_overtime,
            'avg_deficit_per_day': total_deficit / total_days if total_days > 0 else 0,
            'avg_overtime_per_day': total_overtime / total_days if total_days > 0 else 0,
        }
    
    def get_global_stats(
        self,
        from_date,
        to_date
    ) -> Dict[str, Any]:
        """
        Get global attendance statistics.
        
        Returns:
            {
                'total_days': 1000,
                'percent_with_gaps': 12.5,
                'percent_late': 8.2,
                'percent_absent': 3.1,
                ...
            }
        """
        indices = AttendanceDayIndex.objects.filter(
            date__gte=from_date,
            date__lte=to_date
        )
        
        total = indices.count()
        
        if total == 0:
            return {
                'total_days': 0,
                'message': 'No data for this period'
            }
        
        with_gaps = indices.filter(has_gaps=True).count()
        with_anomalies = indices.filter(has_anomalies=True).count()
        requires_attention = indices.filter(requires_attention=True).count()
        
        # Status breakdown
        status_counts = {}
        for index in indices.values('status').annotate(count=models.Count('status')):
            status_counts[index['status']] = index['count']
        
        return {
            'period': {
                'from': str(from_date),
                'to': str(to_date),
            },
            'total_days_indexed': total,
            'percent_with_gaps': round((with_gaps / total) * 100, 2),
            'percent_with_anomalies': round((with_anomalies / total) * 100, 2),
            'percent_requiring_attention': round((requires_attention / total) * 100, 2),
            'status_breakdown': status_counts,
        }


# Import for aggregation
from django.db import models
