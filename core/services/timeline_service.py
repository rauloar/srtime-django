"""
Timeline Service
Generates visual timeline blocks from attendance calculation results.

NO calculation logic - only visual representation.
"""
from datetime import datetime, time, timedelta
from typing import List, Dict, Any, Optional
from decimal import Decimal
import logging

from django.conf import settings
from django.utils import timezone

from core.models_timeline import AttendanceTimelineBlock, BlockType
from core.services.timeline_integrity import TimelineNormalizer, TimelineIntegrityError


logger = logging.getLogger('timeline')


class TimelineService:
    """
    Service to generate visual timeline blocks for attendance days.
    
    This service transforms attendance calculation results into
    visual blocks for operational UX purposes.
    
    NOT for calculation, NOT for legal evidence, NOT for payroll.
    """
    
    def __init__(self):
        self.enabled = getattr(settings, 'TIMELINE_ENABLED', True)
        self.normalizer = TimelineNormalizer()

    
    def build_timeline(
        self,
        employee,
        date,
        result: Dict[str, Any],
        context: Dict[str, Any],
    ) -> List[AttendanceTimelineBlock]:
        """
        Build timeline blocks for a workday.
        
        Args:
            employee: Employee instance
            date: Calculation date
            result: Calculation result from AttendanceEngineV2
            context: Calculation context (schedule, punches, gaps)
        
        Returns:
            List of AttendanceTimelineBlock instances
        """
        if not self.enabled:
            return []
        
        # Clear existing timeline blocks for this day
        AttendanceTimelineBlock.objects.filter(
            employee=employee,
            date=date
        ).delete()
        
        blocks = []
        
        # 1. Schedule block (expected work time)
        schedule_blocks = self._create_schedule_blocks(date, context.get('schedule', {}))
        blocks.extend(schedule_blocks)
        
        # 2. Tolerance blocks (entry/exit grace periods)
        tolerance_blocks = self._create_tolerance_blocks(date, context.get('schedule', {}))
        blocks.extend(tolerance_blocks)
        
        # 3. Work blocks (actual punched time)
        work_blocks = self._create_work_blocks(date, context.get('punches', []))
        blocks.extend(work_blocks)
        
        # 4. Gap blocks (planned and anomaly)
        gap_blocks = self._create_gap_blocks(date, context.get('gaps', []))
        blocks.extend(gap_blocks)
        
        # NORMALIZE: Ensure temporal integrity
        # - Sort by time
        # - Fix overlaps
        # - Fill gaps with GAP_UNCLASSIFIED
        # - Recalculate durations
        try:
            normalized_blocks = self.normalizer.normalize(blocks)
        except Exception as e:
            logger.error(
                f"Timeline normalization failed for {employee.id} on {date}: {e}. "
                f"Saving original blocks without normalization."
            )
            normalized_blocks = blocks
        
        # Create all blocks in database
        created_blocks = []
        for block_data in normalized_blocks:
            try:
                block = AttendanceTimelineBlock.objects.create(
                    employee=employee,
                    date=date,
                    **block_data
                )
                created_blocks.append(block)
            except Exception as e:
                logger.error(
                    f"Failed to create timeline block: {block_data}. Error: {e}"
                )
        
        return created_blocks

    
    def _create_schedule_blocks(
        self,
        date,
        schedule: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create blocks representing expected schedule."""
        blocks = []
        
        if not schedule or not schedule.get('start') or not schedule.get('end'):
            return blocks
        
        start_time = self._parse_time(schedule['start'])
        end_time = self._parse_time(schedule['end'])
        
        if start_time and end_time:
            duration = self._calculate_duration_minutes(start_time, end_time)
            
            blocks.append({
                'block_type': BlockType.SCHEDULE,
                'start_time': start_time,
                'end_time': end_time,
                'duration_minutes': duration,
                'related_rule': schedule.get('type', 'FIXED_SCHEDULE'),
            })
        
        return blocks
    
    def _create_tolerance_blocks(
        self,
        date,
        schedule: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create blocks representing tolerance windows."""
        blocks = []
        
        if not schedule or not schedule.get('tolerance_minutes'):
            return blocks
        
        tolerance_minutes = schedule.get('tolerance_minutes', 0)
        if tolerance_minutes == 0:
            return blocks
        
        start_time = self._parse_time(schedule.get('start'))
        end_time = self._parse_time(schedule.get('end'))
        
        if start_time:
            # Entry tolerance window
            tolerance_start = self._subtract_minutes(start_time, tolerance_minutes)
            blocks.append({
                'block_type': BlockType.TOLERANCE,
                'start_time': tolerance_start,
                'end_time': start_time,
                'duration_minutes': tolerance_minutes,
                'related_rule': 'ENTRY_TOLERANCE',
            })
        
        if end_time:
            # Exit tolerance window (typically after scheduled end)
            tolerance_end = self._add_minutes(end_time, tolerance_minutes)
            blocks.append({
                'block_type': BlockType.TOLERANCE,
                'start_time': end_time,
                'end_time': tolerance_end,
                'duration_minutes': tolerance_minutes,
                'related_rule': 'EXIT_TOLERANCE',
            })
        
        return blocks
    
    def _create_work_blocks(
        self,
        date,
        punches: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create blocks representing actual work time between punches."""
        blocks = []
        
        if not punches or len(punches) < 2:
            return blocks
        
        # Sort punches by time
        sorted_punches = sorted(punches, key=lambda p: p['timestamp'])
        
        # Create work blocks for each IN/OUT pair
        for i in range(0, len(sorted_punches) - 1, 2):
            punch_in = sorted_punches[i]
            punch_out = sorted_punches[i + 1] if i + 1 < len(sorted_punches) else None
            
            if not punch_out:
                # Orphan punch - no work block
                continue
            
            start_time = self._extract_time(punch_in['timestamp'])
            end_time = self._extract_time(punch_out['timestamp'])
            
            if start_time and end_time:
                duration = self._calculate_duration_minutes(start_time, end_time)
                
                blocks.append({
                    'block_type': BlockType.WORK,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration_minutes': duration,
                    'related_rule': 'WORK_BETWEEN_PUNCHES',
                })
        
        return blocks
    
    def _create_gap_blocks(
        self,
        date,
        gaps: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create blocks representing gaps (planned and anomalies)."""
        blocks = []
        
        for gap in gaps:
            gap_type = gap.get('type', 'UNKNOWN')
            start_time = self._parse_time(gap.get('start'))
            end_time = self._parse_time(gap.get('end'))
            
            if not start_time or not end_time:
                continue
            
            duration = self._calculate_duration_minutes(start_time, end_time)
            
            # Classify gap as planned or anomaly
            is_planned = gap_type in ['LUNCH', 'BREAK', 'PLANNED_BREAK']
            
            block_type = BlockType.GAP_PLANNED if is_planned else BlockType.GAP_ANOMALY
            anomaly_code = '' if is_planned else gap_type
            
            blocks.append({
                'block_type': block_type,
                'start_time': start_time,
                'end_time': end_time,
                'duration_minutes': duration,
                'related_rule': f'GAP_{gap_type}',
                'anomaly_code': anomaly_code,
            })
        
        return blocks
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _parse_time(self, time_str) -> Optional[time]:
        """Parse time string to time object."""
        if isinstance(time_str, time):
            return time_str
        
        if not time_str:
            return None
        
        try:
            # Handle HH:MM format
            if isinstance(time_str, str):
                parts = time_str.split(':')
                if len(parts) >= 2:
                    hour = int(parts[0])
                    minute = int(parts[1])
                    return time(hour=hour, minute=minute)
            return None
        except (ValueError, AttributeError):
            return None
    
    def _extract_time(self, timestamp) -> Optional[time]:
        """Extract time from datetime or string."""
        if isinstance(timestamp, datetime):
            return timestamp.time()
        
        if isinstance(timestamp, str):
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                return dt.time()
            except (ValueError, AttributeError):
                return None
        
        return None
    
    def _calculate_duration_minutes(self, start: time, end: time) -> int:
        """Calculate duration in minutes between two times."""
        # Convert times to datetime for calculation
        today = datetime.today().date()
        start_dt = datetime.combine(today, start)
        end_dt = datetime.combine(today, end)
        
        # Handle crossing midnight
        if end < start:
            end_dt += timedelta(days=1)
        
        delta = end_dt - start_dt
        return int(delta.total_seconds() / 60)
    
    def _add_minutes(self, base_time: time, minutes: int) -> time:
        """Add minutes to a time object."""
        today = datetime.today().date()
        dt = datetime.combine(today, base_time)
        new_dt = dt + timedelta(minutes=minutes)
        return new_dt.time()
    
    def _subtract_minutes(self, base_time: time, minutes: int) -> time:
        """Subtract minutes from a time object."""
        today = datetime.today().date()
        dt = datetime.combine(today, base_time)
        new_dt = dt - timedelta(minutes=minutes)
        return new_dt.time()
    
    def get_timeline(self, employee, date) -> List[Dict[str, Any]]:
        """
        Get timeline blocks for a specific day.
        
        Returns:
            List of block dictionaries for API response
        """
        blocks = AttendanceTimelineBlock.objects.filter(
            employee=employee,
            date=date
        ).order_by('start_time')
        
        return [block.to_dict() for block in blocks]
