/**
 * Frontend-Backend Contract Definitions
 * 
 * OBJETIVO: Contrato formal explícito entre frontend React/TS y backend Django.
 * Elimina acoplamientos frágiles (status string, NULLs implícitos, estructura ad-hoc).
 * 
 * REGLAS:
 * - Los tipos aquí son la FUENTE DE VERDAD del contrato API.
 * - Backend DEBE respetar estos contratos en serializers.
 * - Frontend NUNCA debe asumir estructura implícita fuera de estos tipos.
 * - Campos numéricos SIEMPRE definidos (no undefined), con ?? 0 defensivo.
 * - status_info es OPCIONAL (backend puede no enviarlo).
 * 
 * MANTENIMIENTO:
 * - Cambios aquí requieren coordinación backend/frontend.
 * - NO modificar sin actualizar serializers correspondientes.
 * 
 * @see core/serializers.py para implementación backend
 */

/**
 * Status Code - Union literal para códigos de estado válidos
 * Backend puede enviar estos valores en status_code (futuro).
 * Actualmente backend envía status como string libre.
 */
export type StatusCode =
    | "NORMAL"
    | "LATE"
    | "ABSENT"
    | "EARLY"
    | "PARTIAL"
    | "REST_DAY";

/**
 * Status Info - Información de renderizado de estado
 * Backend envía esta metadata para desacoplar frontend de lógica de colores.
 */
export interface StatusInfo {
    label: string;
    display: string;
    color: string;
    color_dark?: string;
    icon?: string;
}

/**
 * DailyAttendance - Contrato formal asistencia diaria
 * 
 * ENDPOINT: GET /api/v1/attendance/reports/daily/
 * BACKEND: core/serializers.py → DailyAttendanceSerializer
 * 
 * CAMPOS CRÍTICOS:
 * - id, user_id, date: Identificación obligatoria
 * - worked_minutes, late_minutes, early_minutes, overtime_minutes: Numéricos SIEMPRE (0 si no hay)
 * - status: String actual del backend (mantener compatibilidad)
 * - status_info: Metadata opcional (backend puede no enviar en cálculos parciales)
 * - check_in, check_out: Pueden ser null si no hay marcación
 * 
 * AGREGACIONES:
 * - SIEMPRE usar (record.worked_minutes ?? 0) en reduce/sum
 * - NUNCA asumir que campos numéricos no son null
 */
export interface DailyAttendance {
    // Identificación
    id: number;
    user_id: number;
    date: string; // YYYY-MM-DD

    // Estado
    status: string; // e.g. "Normal", "Late", "Absent" - mantener como string para compatibilidad
    status_info?: StatusInfo; // Metadata opcional del backend

    // Métricas numéricas (SIEMPRE definidas, usar ?? 0 defensivo)
    worked_minutes: number;
    late_minutes: number;
    early_minutes: number;
    overtime_minutes: number;

    // Timestamps (pueden ser null)
    check_in: string | null;
    check_out: string | null;
    on_duty?: string;
    off_duty?: string;

    // Información empleado (desde serializer)
    employee_name: string;
    employee_user_id: string;
    employee?: {
        department_name?: string;
    };

    // Metadata adicional (opcional)
    timetable_id?: number;
    exception_reason?: string;
    schedule_type?: string;
    source_logs_count?: number;
    is_absent?: boolean;
}

/**
 * DayViewResponse - Vista detallada día individual
 * 
 * ENDPOINT: GET /api/v1/attendance/day/
 * USO: Ver detalles de un empleado en un día específico
 */
export interface DayViewResponse {
    user_id: string;
    employee_name: string;
    date: string;
    status: string;
    worked_minutes: number;
    logs: Array<{
        type: string;
        time: string;
    }>;
}
