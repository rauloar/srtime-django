from typing import NamedTuple, Optional

class ObligationResult(NamedTuple):
    is_obligated: bool
    reason: str 
    # reason values: 'SHIFT', 'OVERRIDE', 'DEPT_SHIFT', 'IMPLICIT_REST', 'FORCED_REST', 'NO_CONTEXT'

class ObligationResolver:
    """
    Componente determinístico para resolver la obligación contractual de un día.
    Actualmente en modo PASIVO (No conectado al motor de cálculo).
    """

    @staticmethod
    def resolve(
        context: Optional[object],  # Timetable
        source_type: str = "NONE"
    ) -> ObligationResult:
        """
        Determina si existe obligación de asistir basada en la presencia de contexto.
        
        Args:
            context: El Timetable resuelto (o None si no hay).
            source_type: El origen del contexto ('OVERRIDE', 'SHIFT', 'DEPARTMENT', 'NONE')
            
        Returns:
            ObligationResult indicando si debe trabajar y por qué.
        """
        if not context:
            return ObligationResult(
                is_obligated=False,
                reason="IMPLICIT_REST"
            )

        # En la lógica actual, si hay horario => hay obligación.
        # A futuro, aquí se chequearían excepciones de "Día Libre Forzado" 
        # que podrían venir como overrides con timetable especial.
        
        if source_type == "OVERRIDE":
            return ObligationResult(True, "OVERRIDE_WORK")
        
        if source_type == "DEPARTMENT":
            return ObligationResult(True, "DEPT_SHIFT")
        
        return ObligationResult(True, "SHIFT")
