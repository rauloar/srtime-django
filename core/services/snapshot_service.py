"""
Engine Snapshot Service
Creates technical snapshots of attendance engine calculations.

NO forensic features, NO legal evidence.
Only technical reproducibility.
"""
from typing import Dict, Any, Optional
import logging

from django.conf import settings
from django.utils import timezone

from core.models_engine_snapshot import AttendanceEngineSnapshot


logger = logging.getLogger('engine.snapshot')


class EngineSnapshotService:
    """
    Service to create technical snapshots of engine calculations.
    
    Purpose: Capture exact inputs and context at calculation time
    for debugging and version comparison.
    
    NOT for legal/forensic purposes.
    """
    
    def __init__(self):
        self.enabled = getattr(settings, 'SNAPSHOT_ENABLED', True)
    
    def create_snapshot(
        self,
        employee,
        date,
        punches: list,
        schedule: dict,
        result: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[AttendanceEngineSnapshot]:
        """
        Create or update engine snapshot.
        
        Args:
            employee: Employee instance
            date: Calculation date
            punches: List of punch records used
            schedule: Schedule configuration used
            result: Calculation result from engine
            context: Additional context (tolerances, flags, etc.)
        
        Returns:
            AttendanceEngineSnapshot instance or None if disabled
        """
        if not self.enabled:
            return None
        
        context = context or {}
        
        try:
            # Prepare snapshot data
            snapshot_data = {
                'punches': self._serialize_punches(punches),
                'schedule': self._serialize_schedule(schedule),
                'tolerances': context.get('tolerances', {}),
                'flexible_mode': context.get('flexible_mode', False),
                'holiday': context.get('holiday', False),
                'absence_type': context.get('absence_type', ''),
                'status': result.get('status', 'UNKNOWN'),
                'worked_minutes': result.get('worked_minutes', 0),
                'expected_minutes': result.get('expected_minutes', 0),
                'overtime_minutes': result.get('overtime_minutes', 0),
                'deficit_minutes': result.get('deficit_minutes', 0),
            }
            
            # Create or update snapshot
            snapshot, created = AttendanceEngineSnapshot.objects.update_or_create(
                employee=employee,
                date=date,
                engine_version='V2',
                defaults=snapshot_data
            )
            
            action = 'Created' if created else 'Updated'
            logger.info(
                f"{action} snapshot for {employee.employee_number} on {date}"
            )
            
            return snapshot
        
        except Exception as e:
            logger.error(
                f"Failed to create snapshot for {employee.id} on {date}: {e}"
            )
            # Don't raise - snapshot failure should not break calculations
            return None
    
    def get_snapshot(self, employee, date, engine_version='V2') -> Optional[Dict[str, Any]]:
        """
        Get snapshot for a specific day.
        
        Returns:
            Snapshot dictionary or None if not found
        """
        try:
            snapshot = AttendanceEngineSnapshot.objects.get(
                employee=employee,
                date=date,
                engine_version=engine_version
            )
            return snapshot.to_dict()
        except AttendanceEngineSnapshot.DoesNotExist:
            return None
    
    def compare_snapshots(
        self,
        employee,
        date,
        version_a='V1',
        version_b='V2'
    ) -> Optional[Dict[str, Any]]:
        """
        Compare snapshots between two engine versions.
        
        Returns:
            Comparison dictionary with differences
        """
        try:
            snapshot_a = AttendanceEngineSnapshot.objects.get(
                employee=employee,
                date=date,
                engine_version=version_a
            )
            snapshot_b = AttendanceEngineSnapshot.objects.get(
                employee=employee,
                date=date,
                engine_version=version_b
            )
            
            return {
                'date': str(date),
                'versions': {
                    version_a: {
                        'status': snapshot_a.status,
                        'worked_minutes': snapshot_a.worked_minutes,
                        'overtime_minutes': snapshot_a.overtime_minutes,
                    },
                    version_b: {
                        'status': snapshot_b.status,
                        'worked_minutes': snapshot_b.worked_minutes,
                        'overtime_minutes': snapshot_b.overtime_minutes,
                    },
                },
                'differences': {
                    'status_changed': snapshot_a.status != snapshot_b.status,
                    'minutes_diff': snapshot_b.worked_minutes - snapshot_a.worked_minutes,
                    'overtime_diff': snapshot_b.overtime_minutes - snapshot_a.overtime_minutes,
                },
            }
        
        except AttendanceEngineSnapshot.DoesNotExist:
            return None
    
    def _serialize_punches(self, punches: list) -> list:
        """Serialize punches to JSON-safe format."""
        serialized = []
        
        for punch in punches:
            # Handle both dict and object punches
            if hasattr(punch, 'timestamp'):
                serialized.append({
                    'timestamp': punch.timestamp.isoformat(),
                    'punch_type': getattr(punch, 'punch_type', 'UNKNOWN'),
                })
            elif isinstance(punch, dict):
                serialized.append({
                    'timestamp': str(punch.get('timestamp', '')),
                    'punch_type': punch.get('punch_type', 'UNKNOWN'),
                })
        
        return serialized
    
    def _serialize_schedule(self, schedule: dict) -> dict:
        """Serialize schedule to JSON-safe format."""
        if not schedule:
            return {}
        
        # Convert time objects to strings
        serialized = {}
        for key, value in schedule.items():
            if hasattr(value, 'isoformat'):
                serialized[key] = value.isoformat()
            else:
                serialized[key] = value
        
        return serialized
