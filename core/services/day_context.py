from typing import NamedTuple, Optional
from datetime import datetime

class DayContext(NamedTuple):
    """
    Representa el contexto de configuración de un día.
    Reemplaza a Optional[ScheduleContext].
    Siempre existe, evitando el uso de None.
    """
    is_valid: bool          # Reemplaza chequeo 'is not None'
    obligation: bool        # Contractual obligation (Future use mostly, current maps to is_valid)
    
    # Payload Data (Nullable if is_valid=False)
    timetable: Optional[object]  # models.Timetable
    on_duty_dt: Optional[datetime]
    off_duty_dt: Optional[datetime]
    search_start: Optional[datetime]
    search_end: Optional[datetime]
    is_cross_day: bool
    
    source: str # 'SHIFT', 'OVERRIDE', 'DEPARTMENT', 'IMPLICIT_REST'
    resolved_obligation: Optional[object] = None # Passive Obligation Result
    
    @classmethod
    def empty(cls):
        return cls(
            is_valid=False,
            obligation=False,
            timetable=None,
            on_duty_dt=None,
            off_duty_dt=None,
            search_start=None,
            search_end=None,
            is_cross_day=False,
            source="IMPLICIT_REST",
            resolved_obligation=None
        )
