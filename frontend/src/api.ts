import axios from 'axios';
import type { DayViewResponse } from './types/contracts';

// Usar siempre ruta relativa ya que Django sirve el frontend
const API_URL = (import.meta.env.VITE_API_URL || '/api/v1').replace(/\/$/, '');

export const api = axios.create({
    baseURL: API_URL,
    withCredentials: true, // Enable cookies for CSRF
    timeout: 300000, // 5 minutes for long-running operations
});

// Helper to get CSRF token from cookies
function getCookie(name: string): string | null {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop()?.split(';').shift() || null;
    return null;
}

// Add request interceptor to inject Authorization header and CSRF token
api.interceptors.request.use((config) => {
    const token = sessionStorage.getItem('auth_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }

    // Add CSRF token for POST, PUT, PATCH, DELETE requests
    if (['post', 'put', 'patch', 'delete'].includes(config.method?.toLowerCase() || '')) {
        const csrfToken = getCookie('csrftoken');
        if (csrfToken) {
            config.headers['X-CSRFToken'] = csrfToken;
        }
    }

    return config;
}, (error) => {
    return Promise.reject(error);
});

api.interceptors.response.use((response) => response, (error) => {
    if (error?.code === 'ECONNABORTED') {
        return Promise.reject(new Error('Tiempo de espera agotado'));
    }

    if (!error?.response) {
        return Promise.reject(new Error('Error de conexión'));
    }

    const status = error.response.status;

    if (status === 401) {
        sessionStorage.removeItem('auth_token');
        return Promise.reject(new Error('Sesión expirada'));
    }

    if (status === 403) {
        return Promise.reject(new Error('Acceso denegado'));
    }

    if (status >= 500) {
        return Promise.reject(new Error('Error del servidor'));
    }

    return Promise.reject(error);
});

export interface Device {
    id?: number;
    name: string;
    ip: string;
    port: number;
    created_at?: string;

    // Status & Identity
    enabled?: boolean;
    serialnumber?: string;
    device_name?: string;
    zone?: string;
    location?: string;
    firmware_version?: string;
    platform?: string;
    mac?: string;

    // Stats
    user_count?: number;
    face_count?: number;
    fp_count?: number;
    transaction_count?: number;

    last_seen?: string;
    last_error?: string;
}

export interface AttendanceLog {
    id: number;
    device_id: number;
    employee?: number;
    user_id: string;
    timestamp: string;
    status: number;
    punch: number;

    // Enhanced Details
    verify_mode?: number;
    workstate?: number;
    workcode?: number;
    punch_source?: string;
    user_name?: string;

    // Labels from backend (source of truth)
    status_label?: string;
    verify_mode_label?: string;
}

export interface TestResponse {
    success: boolean;
    message: string;
    firmware_version?: string;
    serial_number?: string;
    platform?: string;
    mac?: string;
    device_name?: string;
    users_count?: number;
    fingers_count?: number;
    records_count?: number;
}

export interface JobResponse {
    job_id: string;
    status: string;
}

export interface Job {
    id: string;
    type: string;
    device_id?: number;
    status: string;
    progress: number;
    started_at?: string;
    finished_at?: string;
    error?: string;
}

export interface JobLog {
    id: number;
    job_id: string;
    device_id?: number;
    level: string;
    message: string;
    timestamp: string;
}

export interface User {
    id: number;
    device: number;
    uid: number;
    name: string | null;
    privilege: number | null;
    password: string | null;
    group_id: number | null;
    user_id: string | null;
    card: string | null;
    finger_count: number;
    face_count: number;
    updated_at: string;
    device_name?: string;
}

export interface Setting {
    key: string;
    value: string;
    description?: string;
}

export const getDevices = async () => {
    const response = await api.get('/devices/');
    if (Array.isArray(response.data)) return response.data;
    // @ts-ignore
    return response.data.results || [];
};
export const getDevice = async (id: number) => (await api.get<Device>(`/devices/${id}`)).data;
export const createDevice = async (device: Device) => (await api.post<Device>('/devices/', device)).data;
export const updateDevice = async (id: number, device: Partial<Device>) => (await api.put<Device>(`/devices/${id}/`, device)).data;
export const getAllDevicesConnectionStatus = async () => (await api.get<DevicesConnectionStatusResponse>('/devices/connection-status/all')).data;

// Async Job Endpoints
export const testConnection = async (id: number) => (await api.post<JobResponse>(`/devices/${id}/test-connection/`)).data;
export const importAttendance = async (id: number) => (await api.post<JobResponse>(`/devices/${id}/import-attendance/`)).data;
export const clearAttendance = async (id: number) => (await api.post<JobResponse>(`/devices/${id}/clear-attendance/`)).data;
export const downloadUsers = async (id: number) => (await api.post<JobResponse>(`/devices/${id}/download-users/`)).data;
export const syncUsers = async (id: number, userIds?: string[]) => (await api.post<JobResponse>(`/devices/${id}/sync-users/`, { user_ids: userIds })).data;

// New Additional Functions Endpoints
export const checkDeviceOnline = async (id: number) => (await api.get<CheckOnlineResponse>(`/devices/${id}/test-connection-sync/`)).data;
export const restartDevice = async (id: number) => (await api.post<CommandResponse>(`/devices/${id}/restart`)).data;
export const poweroffDevice = async (id: number) => (await api.post<CommandResponse>(`/devices/${id}/poweroff`)).data;
export const syncTime = async (id: number) => (await api.post<CommandResponse>(`/devices/${id}/sync-time`)).data;
export const testVoice = async (id: number, voiceIndex: number = 0) => (await api.post<CommandResponse>(`/devices/${id}/test-voice?voice_index=${voiceIndex}`)).data;
export const getMemoryInfo = async (id: number) => (await api.get<MemoryInfo>(`/devices/${id}/memory`)).data;
export const clearAllData = async (id: number) => (await api.post<JobResponse>(`/devices/${id}/clear-all-data`)).data;
export const getRecentAttendance = async (id: number, limit: number = 50) => (await api.get<RecentAttendanceResponse>(`/devices/${id}/attendance/recent?limit=${limit}`)).data;
export const getDeviceTemplates = async (id: number) => (await api.post<TemplatesResponse>(`/devices/${id}/templates`)).data;
export const getNextUid = async (id: number) => (await api.get<{ next_uid: number }>(`/devices/${id}/next-uid/`)).data;

// Attendance Day View
export const getDayView = async (
    employeeIdOrUserId: number | string,
    date: string
): Promise<DayViewResponse> => {
    const identityParams: any = { date };
    if (typeof employeeIdOrUserId === 'number') {
        identityParams.employee_id = employeeIdOrUserId;
    } else if (/^\d+$/.test(employeeIdOrUserId)) {
        identityParams.employee_id = Number(employeeIdOrUserId);
        identityParams.user_id = employeeIdOrUserId;
    } else {
        identityParams.user_id = employeeIdOrUserId;
    }
    return (await api.get<DayViewResponse>('/attendance/day/', {
        params: identityParams
    })).data;
};

// Response Types for New Endpoints
export interface DeviceConnectionStatus {
    device_id: number;
    name: string;
    enabled: boolean;  // Activo/Inactivo (persistente)
    connected: boolean; // Conectada/Desconectada (dinámico)
    message: string;
}

export interface DevicesConnectionStatusResponse {
    devices: DeviceConnectionStatus[];
}

export interface CheckOnlineResponse {
    online: boolean;
    device_id: number;
    name: string;
    error?: string;
}

export interface CommandResponse {
    success: boolean;
    message: string;
}

// DayViewResponse re-exported from contracts.ts (see line 610)

export interface MemoryInfo {
    success: boolean;
    message: string;
    users: number;
    users_cap: number;
    fingers: number;
    fingers_cap: number;
    records: number;
    records_cap: number;
}

export interface RecentAttendanceRecord {
    user_id: string;
    timestamp: string;
    status: number;
    punch: number;
}

export interface RecentAttendanceResponse {
    success: boolean;
    message: string;
    records: RecentAttendanceRecord[];
}

export interface TemplateItem {
    uid: number;
    fid: number;
    size: number;
    valid: boolean;
}

export interface TemplatesResponse {
    success: boolean;
    message: string;
    count: number;
    templates: TemplateItem[];
}

// Still Sync (mostly)
// Still Sync (mostly)
export const getDeviceInfo = async (id: number) => (await api.get<TestResponse>(`/devices/${id}/info/`)).data;
export const getDeviceUsers = async (id: number) => (await api.get<DeviceUser[]>(`/devices/${id}/users/`)).data;

export interface DeviceUser {
    id: number;
    uid: number;
    user_id: string;
    name?: string;
    privilege?: number;
    password?: string;
    card?: string;
    finger_count?: number;
    face_count?: number;
    group_id?: number;
}

export const getAttendanceLogs = async (params: {
    device_id?: number;
    employee_id?: number;
    user_id?: string;
    from_date?: string;
    to_date?: string;
    name?: string;  // Search by user_name via backend search
    search?: string;  // Alternative search parameter
    page?: number;
    page_size?: number;
}) => {
    const backendParams: any = { ...params };
    if (backendParams.employee_id) {
        backendParams.employee = backendParams.employee_id;
        delete backendParams.employee_id;
    }
    const response = await api.get<{ count: number; next: string | null; previous: string | null; results: AttendanceLog[] }>('/attendance/', { params: backendParams });
    return response.data;
};

// Schedule Compliance Validation
export interface ExpectedSchedule {
    on_duty: string | null;
    off_duty: string | null;
    shift_name: string;
    source: string;
    timetable_id: number | null;
}

export interface ActualTimes {
    in_time: string | null;
    out_time: string | null;
    duration: string | null;
}

export interface ScheduleValidation {
    is_compliant: boolean;
    warning: boolean;
    message: string;
    discrepancy_type: string | null;
    expected_schedule: ExpectedSchedule;
    actual: ActualTimes;
}

export interface LogsWithValidation {
    employee: {
        id: number;
        name: string;
        department: string | null;
        user_id: string;
    } | null;
    date: string;
    logs: Array<{
        timestamp: string;
        punch: number;
        time: string;
    }>;
    validation: ScheduleValidation | null;
    error?: string;
}

export const getLogsWithValidation = async (employeeIdOrUserId: number | string, date: string) => {
    const identityParams: any = { date };
    if (typeof employeeIdOrUserId === 'number') {
        identityParams.employee_id = employeeIdOrUserId;
    } else if (/^\d+$/.test(employeeIdOrUserId)) {
        identityParams.employee_id = Number(employeeIdOrUserId);
        identityParams.user_id = employeeIdOrUserId;
    } else {
        identityParams.user_id = employeeIdOrUserId;
    }
    const response = await api.get<LogsWithValidation>('/attendance/logs-validated/', {
        params: identityParams
    });
    return response.data;
};

export const updateAttendanceLog = async (id: number, data: Partial<AttendanceLog>) =>
    (await api.put<AttendanceLog>(`/attendance-logs/${id}/`, data)).data;

// Settings & Jobs
export const getSettings = async () => (await api.get<Setting[]>('/settings/')).data;
export const updateSetting = async (setting: Setting) => (await api.put<Setting>(`/settings/${setting.key}/`, setting)).data;
export const getJob = async (jobId: string) => (await api.get<Job>(`/jobs/${jobId}`)).data;
export const getJobLogs = async (jobId: string) => (await api.get<JobLog[]>(`/jobs/${jobId}/logs`)).data;

// Personnel
export interface Department {
    id?: number;
    name: string;
    code?: string;
    company?: number;
    company_name?: string;
    parent_id?: number;
    parent_name?: string;
    children?: Department[];
}

export interface Company {
    id?: number;
    name: string;
    code?: string;
    address?: string;
    website?: string;
    logo_path?: string;
}

export interface Employee {
    id?: number;
    device?: number;
    uid?: number;
    user_id: string; // Global ID
    name?: string;
    email?: string;
    card?: string;
    phone?: string;
    mobile_phone?: string;  // Teléfono Celular
    address?: string;
    city?: string;
    country?: string;  // País

    // Personal Data
    gender?: string;
    birthday?: string;  // Fecha de Nacimiento
    ssn?: string;  // DNI / Documento de Identidad

    // Biometric
    finger_count?: number;
    face_count?: number;
    department_id?: number;
    department_name?: string; // Read-only
    privilege?: number;
    is_active?: boolean;
    active?: boolean;

    current_shift?: {
        id: number;
        name: string;
        scope: 'EMPLOYEE' | 'DEPARTMENT';
        start_date: string;
        end_date?: string | null;
    } | null;
    current_timetable?: {
        id: number;
        name: string;
        on_duty_time?: string | null;
        off_duty_time?: string | null;
        is_flexible?: boolean;
        break_minutes?: number;
        late_allow_minutes?: number;
        early_leave_allow_minutes?: number;
        overtime_threshold_minutes?: number;
    } | null;
    schedule_source?: {
        is_valid: boolean;
        source?: string | null;
        error?: string | null;
        description?: string | null;
    } | null;
}

export const getDepartments = async () => (await api.get<Department[]>('/departments/')).data;
export const createDepartment = async (dept: Department) => (await api.post<Department>('/departments/', dept)).data;
export const updateDepartment = async (id: number, dept: Partial<Department>) => (await api.put<Department>(`/departments/${id}/`, dept)).data;
export const deleteDepartment = async (id: number) => (await api.delete(`/departments/${id}/`)).data;

export const getCompanies = async () => (await api.get<Company[]>('/companies/')).data;
export const getCompany = async (id: number) => (await api.get<Company>(`/companies/${id}/`)).data;
export const createCompany = async (company: Company) => (await api.post<Company>('/companies/', company)).data;
export const updateCompany = async (id: number, company: Partial<Company>) => (await api.put<Company>(`/companies/${id}/`, company)).data;
export const deleteCompany = async (id: number) => (await api.delete(`/companies/${id}/`)).data;


export const getEmployees = async (skip = 0, limit = 100) => (await api.get<Employee[]>('/employees/', { params: { skip, limit } })).data;
export const getEmployeesByDate = async (date: string, skip = 0, limit = 100) => (
    await api.get<Employee[]>('/employees/', { params: { skip, limit, date } })
).data;
export const searchEmployees = async (query: string) => (await api.get<Employee[]>('/employees/', { params: { search: query } })).data;
export const getEmployee = async (employeeId: number | string) => (await api.get<Employee>(`/employees/${employeeId}/`)).data;
export const getEmployeeByDate = async (employeeId: number | string, date: string) => (
    await api.get<Employee>(`/employees/${employeeId}/`, { params: { date } })
).data;
const serializeEmployeePayload = (emp: Employee) => ({
    user_id: emp.user_id,
    name: emp.name,
    email: emp.email,
    phone: emp.phone,
    mobile_phone: emp.mobile_phone,
    ssn: emp.ssn,
    department: emp.department_id,
    position: (emp as { position?: number }).position,
    hire_date: (emp as { hire_date?: string }).hire_date,
    birthday: emp.birthday,
    gender: emp.gender,
    is_active: emp.is_active ?? emp.active,
    address: emp.address,
    city: emp.city,
    country: emp.country,
    photo_path: (emp as { photo_path?: string }).photo_path,
});

export const createEmployee = async (emp: Employee) => (
    await api.post<Employee>('/employees/', serializeEmployeePayload(emp))
).data;
export const updateEmployee = async (employeeId: number, emp: Employee) => (
    await api.put<Employee>(`/employees/${employeeId}/`, serializeEmployeePayload(emp))
).data;
export const deleteEmployee = async (employeeId: number) => (await api.delete(`/employees/${employeeId}/`)).data;

export interface ImportResult {
    success: number;
    errors: string[];
    total: number;
}

export const importEmployees = async (file: File): Promise<ImportResult> => {
    const formData = new FormData();
    formData.append('file', file);
    return (await api.post<ImportResult>('/employees/import', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    })).data;
};


// Attendance - Schedules
export interface Timetable {
    id?: number;
    name: string;
    on_duty_time: string;
    off_duty_time: string;
    late_allow_minutes?: number;
    early_leave_allow_minutes?: number;
    check_in_start?: string;
    check_in_end?: string;
    check_out_start?: string;
    check_out_end?: string;
    break_minutes?: number;
    rounding_rule?: string;
    required_minutes?: number;
    work_days?: number;
    is_flexible?: boolean;
}

export interface Shift {
    id?: number;
    name: string;
}

export const getTimetables = async () => (await api.get<Timetable[]>('/schedules/timetables/')).data;
export const createTimetable = async (tt: Timetable) => (await api.post<Timetable>('/schedules/timetables/', tt)).data;
export const updateTimetable = async (id: number, tt: Timetable) => (await api.put<Timetable>(`/timetables/${id}/`, tt)).data;
export const deleteTimetable = async (id: number) => (await api.delete(`/timetables/${id}/`)).data;

export const getShifts = async () => (await api.get<Shift[]>('/shifts/')).data;
export const createShift = async (shift: Shift) => (await api.post<Shift>('/shifts/', shift)).data;
export const deleteShift = async (id: number) => (await api.delete(`/shifts/${id}/`)).data;

// Assignments & Cycle
export interface ShiftCycleItem {
    timetable_id: number;
    day_index: number;
    timetable_name?: string;
}

export const configureShiftCycle = async (shiftId: number, items: { timetable_id: number; day_index: number }[]) => {
    return (await api.post(`/shifts/${shiftId}/timetables/`, items)).data;
};

export const getShiftCycle = async (shiftId: number) => {
    return (await api.get<ShiftCycleItem[]>(`/shifts/${shiftId}/timetables/`)).data;
};

export interface AssignShiftRequest {
    employee_id?: number;
    user_id?: string;
    department_id?: number;
    scope?: 'EMPLOYEE' | 'DEPARTMENT';
    shift_id: number;
    start_date: string;
    end_date?: string;
}

export const assignShift = async (data: AssignShiftRequest) => {
    const payload = {
        employee_id: data.employee_id,
        user_id: data.user_id,
        department: data.department_id,
        shift: data.shift_id,
        start_date: data.start_date,
        end_date: data.end_date,
        scope: data.scope
    };
    return (await api.post('/employee-shifts/', payload)).data;
};

export interface ShiftAssignment {
    id: number;
    employee_id?: number;
    user_id?: string;
    department_id?: number;
    scope?: 'EMPLOYEE' | 'DEPARTMENT';
    shift_id: number;
    shift_name: string;
    start_date: string;
    end_date?: string;
}

export const getAssignments = async (startDate: string, endDate: string, departmentId?: number) => {
    const params: any = { start_date: startDate, end_date: endDate };
    if (departmentId) params.department_id = departmentId;
    return (await api.get<ShiftAssignment[]>('/employee-shifts/', { params })).data;
};

export interface ScheduleOverride {
    id: number;
    employee: number | string;
    employee_name?: string;
    timetable: number;
    timetable_name?: string;
    date: string;
}

export const getScheduleOverrides = async (startDate: string, endDate: string, userId?: string) => {
    const params: any = { 'date__gte': startDate, 'date__lte': endDate };
    if (userId) params.employee__user_id = userId;
    return (await api.get<ScheduleOverride[]>('/schedule-overrides/', { params })).data;
};

export const createScheduleOverrideFromShift = async (payload: {
    employee_id?: number;
    user_id?: string;
    shift_id: number;
    date: string;
    start_date?: string;
}) => (await api.post<ScheduleOverride>('/schedule-overrides/from-shift/', payload)).data;

// Calculation & Reports
// ============================================================================
// CONTRATO FORMAL: Re-exportado desde types/contracts.ts
// NO modificar aquí - editar contracts.ts para cambios de contrato
// ============================================================================
export type { DailyAttendance, DayViewResponse, StatusCode, StatusInfo } from './types/contracts';

export interface DashboardSummaryReport {
    date: string;
    total_records: number;
    present: number;
    absent: number;
    avg_worked_minutes: number | null;
}

export interface DashboardSummary {
    company_name: string | null;
    counts: {
        employees: number;
        departments: number;
        shifts: number;
        timetables: number;
        groups: number;
    };
    recent_reports: DashboardSummaryReport[];
    meta?: {
        limit?: number;
    };
}

export const getDashboardSummary = async (limit = 5) => {
    return (await api.get<DashboardSummary>('/dashboard/summary/', { params: { limit } })).data;
};

export const calculateAttendance = async (startDate: string, endDate: string, departmentId?: number) => {
    const payload: any = { start_date: startDate, end_date: endDate };
    if (departmentId) payload.department_id = departmentId;
    return (await api.post('/attendance/calculate/', payload)).data;
};

// ============================================================================
// V2 API - DOMINIO FUERTE (CONTRATO FORMAL)
// ============================================================================

import type {
    StatusCode as StatusCodeV2,
    DailyAttendanceV2Response
} from './types/contractsV2';

export {
    type DailyAttendanceV2,
    type DailyAttendanceV2Response
} from './types/contractsV2';

export type { StatusCodeV2 };

/**
 * V2 - Obtener reportes de asistencia diaria con dominio fuerte
 * 
 * ENDPOINT: GET /api/v2/attendance/reports/daily/
 * 
 * CONTRATO GARANTIZADO:
 * - Estructura jerárquica (identity, status, metrics, schedule, employee)
 * - Campos numéricos NUNCA null
 * - status.code siempre en formato UPPER_CASE
 * - Backend garantiza integridad (no fallbacks defensivos)
 * 
 * DIFERENCIAS DE V1:
 * - Usa estructura v2 (no campos planos)
 * - status es objeto (no string textual)
 * - Lógica: usar status.code === "LATE" (no strings)
 */
export const getDailyReportsV2 = async (
    fromDate: string,
    toDate: string,
    departmentId?: number,
    userIdFilter?: string,
    nameFilter?: string
): Promise<DailyAttendanceV2Response> => {
    const params: any = { from_date: fromDate, to_date: toDate };
    if (departmentId) params.department_id = departmentId;
    if (userIdFilter?.trim()) params.employee_user_id = userIdFilter.trim();
    if (nameFilter?.trim()) params.employee_name = nameFilter.trim();
    return (await api.get<DailyAttendanceV2Response>('/attendance/reports/daily/v2/', { params })).data;
};

// Absences
export interface Absence {
    id?: number | string;
    employee_id?: number;
    user_id?: string;
    employee_name?: string; // Read only
    employee_user_id?: string; // From backend
    start_date: string;
    end_date: string;
    type: string;
    reason?: string;
    approved?: boolean;
    source?: 'Manual' | 'Detected'; // Manual (Leave) or Detected (DailyAttendance)
    status?: string; // Pending, Approved, Rejected, Detected
}

export const getAbsences = async () => {
    try {
        const response = await api.get('/attendance/absences/');
        const data = response.data as Absence[] | { results?: Absence[] } | null;
        if (Array.isArray(data)) return data;
        if (data && Array.isArray(data.results)) return data.results;
        return [];
    } catch {
        return [];
    }
};
export const createAbsence = async (abs: Absence) => {
    const payload: any = { ...abs };
    return (await api.post<Absence>('/leaves/', payload)).data;
};
export const deleteAbsence = async (id: number) => (await api.delete(`/leaves/${id}/`)).data;

// Auth System
export interface AuthUser {
    id: number;
    username: string;
    is_active: boolean;
    is_staff: boolean;
    is_superuser: boolean;
    email: string;
    first_name: string;
    last_name: string;
    date_joined: string;
}

export interface LoginResponse {
    access_token: string;
    token_type: string;
    username: string;
    role: string;
}

export interface AuthMeResponse {
    username: string;
    groups: string[];
    is_superuser: boolean;
}

export const login = async (username: string, password: string) => (await api.post<LoginResponse>('/auth/login', { username, password })).data;
export const getAuthMe = async () => (await api.get<AuthMeResponse>('/auth/me')).data;
export const getAuthUsers = async () => (await api.get<AuthUser[]>('/auth/users')).data;
export const createAuthUser = async (user: Partial<AuthUser> & { password: string }) => (await api.post<AuthUser>('/auth/users', user)).data;
export const deleteAuthUser = async (id: number) => (await api.delete(`/auth/users/${id}`)).data;
export const updateAuthUserPassword = async (id: number, password: string) => (await api.put(`/auth/users/${id}/password`, { password })).data;

// System Tools
export interface BackupResponse {
    success: boolean;
    message: string;
    file: string;
    size_mb: number;
    timestamp: string;
}

export interface BackupFile {
    filename: string;
    path: string;
    size_mb: number;
    created_at: string;
}

export interface DatabaseTestResponse {
    success: boolean;
    database: string;
    tables_count: number;
    tables: string[];
    records: Record<string, number>;
    size_mb: number;
    connection: string;
}

export const backupDatabase = async () => (await api.post<BackupResponse>('/system/database/backup')).data;
export const listBackups = async () => (await api.get<{ backups: BackupFile[] }>('/system/database/backups')).data;
export const restoreDatabase = async (filename: string) => (await api.post<{ success: boolean; message: string }>('/system/database/restore', null, { params: { backup_filename: filename } })).data;
export const testDatabase = async () => (await api.get<DatabaseTestResponse>('/system/database/test')).data;
export const importDatabase = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return (await api.post<{ success: boolean; message: string }>('/system/database/import', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    })).data;
};

// Attendance - Day View
export interface TimelineBlock {
    type: string;
    start_time: string;
    end_time: string;
    duration_minutes: number;
}

export interface TimelineData {
    blocks: TimelineBlock[];
}

export interface ExplanationData {
    summary: string;
    anomalies: string[];
    recommendations: string[];
}

export const getTimeline = async (employeeIdOrUserId: number | string, date: string) =>
    (await api.get<TimelineData>(`/attendance/${employeeIdOrUserId}/timeline/${date}/`)).data;

export const getExplanation = async (employeeIdOrUserId: number | string, date: string) =>
    (await api.get<ExplanationData>(`/attendance/${employeeIdOrUserId}/explanation/${date}/`)).data;
