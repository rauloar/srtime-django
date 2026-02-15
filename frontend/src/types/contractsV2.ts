/**
 * CONTRATO FORMAL v2 - DOMINIO FUERTE
 * 
 * Definiciones de tipos garantizadas por backend.
 * NO usar fallbacks, backend garantiza integridad.
 * 
 * VERSIÓN: v2 (alpha)
 * ENDPOINT: GET /api/v2/attendance/reports/daily/
 * 
 * @see core/serializers.py DailyAttendanceV2Serializer
 * @see core/views_attendance.py daily_reports_v2()
 */

/**
 * StatusCode - Códigos canónicos de estado (UPPER_CASE_WITH_UNDERSCORES)
 * Backend mapea "Late" → "LATE", "Rest Day" → "REST_DAY", etc.
 */
export type StatusCode =
  | "NORMAL"
  | "LATE"
  | "ABSENT"
  | "EARLY"
  | "PARTIAL"
  | "LEAVE"
  | "WORKED"
  | "INCOMPLETE"
  | "EXCESSIVE"
  | "HOLIDAY_WORKED"
  | "REST_DAY";

/**
 * Identity - Información de identificación del registro
 * GARANTIZADO: nunca null, siempre presente
 */
export interface Identity {
  id: number;
  employee_id: number;
  date: string; // YYYY-MM-DD
}

/**
 * Status - Estado normalizado con renderizado
 * GARANTIZADO: code, label, color siempre presentes
 * NO usar string comparisons contra status.label
 * SIEMPRE usar code para lógica: status.code === "LATE"
 */
export interface Status {
  /** Código canónico UPPER_CASE_WITH_UNDERSCORES */
  code: StatusCode;
  
  /** Etiqueta de renderizado (ej: "Llegó Tarde", "Ausente") */
  label: string;
  
  /** Color CSS (ej: "#ef6c00") */
  color: string;
}

/**
 * Metrics - Métricas numéricas de asistencia
 * GARANTIZADO: NUNCA null, fallback a 0 en backend
 * NUNCA usar ?? 0 en frontend (ya está garantizado backend)
 */
export interface Metrics {
  worked_minutes: number;
  late_minutes: number;
  early_minutes: number;
  overtime_minutes: number;
}

/**
 * Schedule - Timestamps de entrada/salida
 * NULLABLE: check_in y check_out pueden ser null si no hay marcación
 * Acceso seguro sin optional chaining
 */
export interface Schedule {
  check_in: string | null; // ISO 8601 timestamp
  check_out: string | null; // ISO 8601 timestamp
}

/**
 * Employee - Información del empleado
 * GARANTIZADO: name y user_id siempre presentes
 * department_name puede ser null
 */
export interface Employee {
  name: string;
  user_id: string;
  department_name: string | null;
}

/**
 * DailyAttendanceV2 - CONTRATO FORMAL ESTRUCTURA JERÁRQUICA
 * 
 * ESTRUCTURA GARANTIZADA:
 * {
 *   "identity": { "id", "employee_id", "date" },
 *   "status": { "code", "label", "color" },
 *   "metrics": { "worked_minutes", "late_minutes", "early_minutes", "overtime_minutes" },
 *   "schedule": { "check_in", "check_out" },
 *   "employee": { "name", "user_id", "department_name" }
 * }
 * 
 * DIFERENCIAS DE V1:
 * - Estructura jerárquica (no campos planos)
 * - status es objeto con code canónico (no string textual)
 * - Métricas nunca null (backend garantiza)
 * - Dominio fuerte, eliminadas defensivas de frontend
 * 
 * REGLAS DE USO:
 * 1. Lógica condicional: usar status.code (ej: status.code === "LATE")
 * 2. Renderizado: usar status.label y status.color directamente
 * 3. Agregaciones: NO usar ?? 0, backend garantiza nunca null
 * 4. Timestamps: ISO 8601, pueden ser null
 * 
 * EJEMPLOS CORRECTOS:
 * 
 * // ✅ Lógica: usar code (tipo-safe)
 * if (record.status.code === "LATE") { ... }
 * if (["LATE", "ABSENT"].includes(record.status.code)) { ... }
 * 
 * // ✅ Renderizado: usar label/color directamente
 * <span style={{ color: record.status.color }}>
 *   {record.status.label}
 * </span>
 * 
 * // ✅ Agregaciones: sin defensivas (backend garantiza)
 * const total = items.reduce((acc, curr) => acc + curr.metrics.worked_minutes, 0);
 * 
 * // ❌ INCORRECTO: comparar contra label (frágil)
 * if (record.status.label === "Llegó Tarde") { ... }  // MAL
 * 
 * // ❌ INCORRECTO: defensivas innecesarias
 * const mins = record.metrics.worked_minutes ?? 0;  // MAL (nunca null en v2)
 * 
 * // ❌ INCORRECTO: acceso a campos v1 que no existen
 * const name = record.employee_name;  // MAL (es record.employee.name)
 */
export interface DailyAttendanceV2 {
  identity: Identity;
  status: Status;
  metrics: Metrics;
  schedule: Schedule;
  employee: Employee;
}

/**
 * DailyAttendanceV2Response - Array de registros
 * Endpoint retorna: DailyAttendanceV2[]
 */
export type DailyAttendanceV2Response = DailyAttendanceV2[];
