import axios from 'axios';

// Detectar automáticamente la URL de la API según el ambiente
const API_URL = (() => {
    // Prioridad: variable de entorno
    if (import.meta.env.VITE_API_BASE_URL) {
        return import.meta.env.VITE_API_BASE_URL;
    }

    // Dev fallback explícito
    if (import.meta.env.DEV) {
        return 'http://127.0.0.1:9000/api/v1';
    }

    // Prod fallback: mismo host/puerto (embedded)
    return '/api/v1';
})();

export const api = axios.create({
    baseURL: API_URL,
    withCredentials: true, // Enable cookies for CSRF
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
export const syncUsers = async (id: number, employeeIds?: number[]) => (await api.post<JobResponse>(`/devices/${id}/sync-users/`, { employee_ids: employeeIds })).data;

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
    user_id?: string; 
    from_date?: string; 
    to_date?: string;
    name?: string;  // Search by user_name via backend search
    search?: string;  // Alternative search parameter
    page?: number;
    page_size?: number;
}) => {
    const response = await api.get<{ count: number; next: string | null; previous: string | null; results: AttendanceLog[] }>('/attendance/', { params });
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

export const getLogsWithValidation = async (employee_id: number, date: string) => {
    const response = await api.get<LogsWithValidation>('/attendance/logs-validated/', {
        params: { employee_id, date }
    });
    return response.data;
};

export const updateAttendanceLog = async (id: number, data: Partial<AttendanceLog>) => 
    (await api.put<AttendanceLog>(`/attendance/${id}/`, data)).data;

// Settings & Jobs
export const getSettings = async () => (await api.get<Setting[]>('/settings/')).data;
export const updateSetting = async (setting: Setting) => (await api.put<Setting>(`/settings/${setting.key}/`, setting)).data;
export const getJob = async (jobId: string) => (await api.get<Job>(`/jobs/${jobId}`)).data;
export const getJobLogs = async (jobId: string) => (await api.get<JobLog[]>(`/jobs/${jobId}/logs`)).data;

// Organization Module
export interface Company {
    id: number;
    name: string;
    code?: string;
    address?: string;
    website?: string;
    logo_path?: string;
}

export const getCompany = async () => (await api.get<Company[]>('/companies/')).data;
export const updateCompany = async (company: Company) => (await api.put<Company>(`/companies/${company.id}/`, company)).data;

export interface Position {
    id?: number;
    name: string;
    code?: string;
    description?: string;
}

export const getPositions = async () => (await api.get<Position[]>('/positions/')).data;
export const createPosition = async (pos: Position) => (await api.post<Position>('/positions/', pos)).data;
export const updatePosition = async (id: number, pos: Position) => (await api.put<Position>(`/positions/${id}/`, pos)).data;
export const deletePosition = async (id: number) => (await api.delete(`/positions/${id}/`)).data;

export interface Zone {
    id?: number;
    name: string;
    code?: string;
    description?: string;
}

export const getZones = async () => (await api.get<Zone[]>('/zones/')).data;
export const createZone = async (z: Zone) => (await api.post<Zone>('/zones/', z)).data;
export const updateZone = async (id: number, z: Zone) => (await api.put<Zone>(`/zones/${id}/`, z)).data;
export const deleteZone = async (id: number) => (await api.delete(`/zones/${id}/`)).data;


// Personnel
export interface Department {
    id?: number;
    name: string;
    code?: string;
    parent_id?: number;
    children?: Department[];
}

export interface Employee {
    id?: number;
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
export const updateDepartment = async (id: number, dept: Department) => (await api.put<Department>(`/departments/${id}/`, dept)).data;
export const deleteDepartment = async (id: number) => (await api.delete(`/departments/${id}/`)).data;

export const getEmployees = async (skip = 0, limit = 100) => (await api.get<Employee[]>('/employees/', { params: { skip, limit } })).data;
export const getEmployeesByDate = async (date: string, skip = 0, limit = 100) => (
    await api.get<Employee[]>('/employees/', { params: { skip, limit, date } })
).data;
export const searchEmployees = async (query: string) => (await api.get<Employee[]>('/employees/', { params: { search: query } })).data;
export const getEmployee = async (id: number) => (await api.get<Employee>(`/employees/${id}/`)).data;
export const getEmployeeByDate = async (id: number, date: string) => (
    await api.get<Employee>(`/employees/${id}/`, { params: { date } })
).data;
export const createEmployee = async (emp: Employee) => (await api.post<Employee>('/employees/', emp)).data;
export const updateEmployee = async (id: number, emp: Employee) => (await api.put<Employee>(`/employees/${id}/`, emp)).data;
export const deleteEmployee = async (id: number) => (await api.delete(`/employees/${id}/`)).data;

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
    department_id?: number;
    scope?: 'EMPLOYEE' | 'DEPARTMENT';
    shift_id: number;
    start_date: string;
    end_date?: string;
}

export const assignShift = async (data: AssignShiftRequest) => {
    const payload = {
        employee: data.employee_id,
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
    employee: number;
    employee_name?: string;
    timetable: number;
    timetable_name?: string;
    date: string;
}

export const getScheduleOverrides = async (startDate: string, endDate: string, employeeId?: number) => {
    const params: any = { 'date__gte': startDate, 'date__lte': endDate };
    if (employeeId) params.employee = employeeId;
    return (await api.get<ScheduleOverride[]>('/schedule-overrides/', { params })).data;
};

export const createScheduleOverrideFromShift = async (payload: {
    employee_id: number;
    shift_id: number;
    date: string;
    start_date?: string;
}) => (await api.post<ScheduleOverride>('/schedule-overrides/from-shift/', payload)).data;

// Calculation & Reports
export interface DailyAttendance {
    id: number;
    employee_id: number;
    date: string;
    timetable_id?: number;
    check_in?: string;
    check_out?: string;
    on_duty?: string;
    off_duty?: string;
    late_minutes: number;
    early_minutes: number;
    worked_minutes: number;
    overtime_minutes: number; // Added
    status: string;
    exception_reason?: string;
    employee_name?: string; // From serializer (employee.name)
    employee_user_id?: string; // From serializer (employee.user_id)
    
    // Status color and label from backend
    status_info?: {
        label: string;
        display: string;
        color: string;
        color_dark?: string;
        icon?: string;
    };
    // Audit
    schedule_type?: string;
    source_logs_count?: number;
    is_absent?: boolean;

    employee?: Employee;
}

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

export const getDailyReports = async (
    fromDate: string, 
    toDate: string, 
    departmentId?: number,
    userIdFilter?: string,
    nameFilter?: string
) => {
    const params: any = { from_date: fromDate, to_date: toDate };
    if (departmentId) params.department_id = departmentId;
    if (userIdFilter?.trim()) params.employee_user_id = userIdFilter.trim();
    if (nameFilter?.trim()) params.employee_name = nameFilter.trim();
    return (await api.get<DailyAttendance[]>('/attendance/reports/daily/', { params })).data;
};

// Absences
export interface Absence {
    id?: number | string;
    employee_id: number;
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
export const createAbsence = async (abs: Absence) => (await api.post<Absence>('/attendance/absences/', abs)).data;
export const deleteAbsence = async (id: number) => (await api.delete(`/attendance/absences/${id}`)).data;

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

export const login = async (username: string, password: string) => (await api.post<LoginResponse>('/auth/login', { username, password })).data;
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

export const getTimeline = async (employeeId: string, date: string) =>
    (await api.get<TimelineData>(`/attendance/${employeeId}/timeline/${date}/`)).data;

export const getExplanation = async (employeeId: string, date: string) =>
    (await api.get<ExplanationData>(`/attendance/${employeeId}/explanation/${date}/`)).data;
