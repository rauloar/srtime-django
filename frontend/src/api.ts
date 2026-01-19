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

    // Prod fallback: mismo host, puerto 8000
    const hostname = window.location.hostname;
    return `http://${hostname}:9000/api/v1`;
})();

export const api = axios.create({
    baseURL: API_URL,
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

export const getDevices = async () => (await api.get<Device[]>('/devices/')).data;
export const getDevice = async (id: number) => (await api.get<Device>(`/devices/${id}`)).data;
export const createDevice = async (device: Device) => (await api.post<Device>('/devices/', device)).data;
export const getAllDevicesConnectionStatus = async () => (await api.get<DevicesConnectionStatusResponse>('/devices/connection-status/all')).data;

// Async Job Endpoints
export const testConnection = async (id: number) => (await api.post<JobResponse>(`/devices/${id}/test-connection`)).data;
export const importAttendance = async (id: number) => (await api.post<JobResponse>(`/devices/${id}/attendance/import`)).data;
export const clearAttendance = async (id: number) => (await api.post<JobResponse>(`/devices/${id}/clear-attendance`)).data;
export const downloadUsers = async (id: number) => (await api.post<JobResponse>(`/devices/${id}/users/download`)).data;

// New Additional Functions Endpoints
export const checkDeviceOnline = async (id: number) => (await api.get<CheckOnlineResponse>(`/devices/${id}/test-connection-sync`)).data;
export const restartDevice = async (id: number) => (await api.post<CommandResponse>(`/devices/${id}/restart`)).data;
export const poweroffDevice = async (id: number) => (await api.post<CommandResponse>(`/devices/${id}/poweroff`)).data;
export const syncTime = async (id: number) => (await api.post<CommandResponse>(`/devices/${id}/sync-time`)).data;
export const testVoice = async (id: number, voiceIndex: number = 0) => (await api.post<CommandResponse>(`/devices/${id}/test-voice?voice_index=${voiceIndex}`)).data;
export const getMemoryInfo = async (id: number) => (await api.get<MemoryInfo>(`/devices/${id}/memory`)).data;
export const clearAllData = async (id: number) => (await api.post<JobResponse>(`/devices/${id}/clear-all-data`)).data;
export const getRecentAttendance = async (id: number, limit: number = 50) => (await api.get<RecentAttendanceResponse>(`/devices/${id}/attendance/recent?limit=${limit}`)).data;
export const getDeviceTemplates = async (id: number) => (await api.get<TemplatesResponse>(`/devices/${id}/templates`)).data;

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
export const getDeviceInfo = async (id: number) => (await api.get<TestResponse>(`/devices/${id}/info`)).data;
export const getDeviceUsers = async (id: number) => (await api.get<DeviceUser[]>(`/devices/${id}/users`)).data;

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

export const getAttendanceLogs = async (params: { device_id?: number; user_id?: string; from_date?: string; to_date?: string }) => {
    return (await api.get<AttendanceLog[]>('/attendance/', { params })).data;
};

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
}

export const getDepartments = async () => (await api.get<Department[]>('/departments/')).data;
export const createDepartment = async (dept: Department) => (await api.post<Department>('/departments/', dept)).data;
export const updateDepartment = async (id: number, dept: Department) => (await api.put<Department>(`/departments/${id}`, dept)).data;
export const deleteDepartment = async (id: number) => (await api.delete(`/departments/${id}`)).data;

export const getEmployees = async (skip = 0, limit = 100) => (await api.get<Employee[]>('/employees/', { params: { skip, limit } })).data;
export const getEmployee = async (id: number) => (await api.get<Employee>(`/employees/${id}`)).data;
export const createEmployee = async (emp: Employee) => (await api.post<Employee>('/employees/', emp)).data;
export const updateEmployee = async (id: number, emp: Employee) => (await api.put<Employee>(`/employees/${id}`, emp)).data;
export const deleteEmployee = async (id: number) => (await api.delete(`/employees/${id}`)).data;

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
export const updateTimetable = async (id: number, tt: Timetable) => (await api.put<Timetable>(`/schedules/timetables/${id}`, tt)).data;
export const deleteTimetable = async (id: number) => (await api.delete(`/schedules/timetables/${id}`)).data;

export const getShifts = async () => (await api.get<Shift[]>('/schedules/shifts/')).data;
export const createShift = async (shift: Shift) => (await api.post<Shift>('/schedules/shifts/', shift)).data;
export const deleteShift = async (id: number) => (await api.delete(`/schedules/shifts/${id}`)).data;

// Assignments & Cycle
export interface ShiftCycleItem {
    timetable_id: number;
    day_index: number;
    timetable_name?: string;
}

export const configureShiftCycle = async (shiftId: number, items: { timetable_id: number; day_index: number }[]) => {
    return (await api.post(`/schedules/shifts/${shiftId}/timetables`, items)).data;
};

export const getShiftCycle = async (shiftId: number) => {
    return (await api.get<ShiftCycleItem[]>(`/schedules/shifts/${shiftId}/timetables`)).data;
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
    return (await api.post('/schedules/assign/', data)).data;
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
    return (await api.get<ShiftAssignment[]>('/schedules/assignments/', { params })).data;
};

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

    // Audit
    schedule_type?: string;
    source_logs_count?: number;
    is_absent?: boolean;

    employee?: Employee;
}

export const calculateAttendance = async (startDate: string, endDate: string, departmentId?: number) => {
    const params: any = { start_date: startDate, end_date: endDate };
    if (departmentId) params.department_id = departmentId;
    return (await api.post('/attendance/calculate', null, { params })).data;
};

export const getDailyReports = async (fromDate: string, toDate: string, departmentId?: number) => {
    const params: any = { from_date: fromDate, to_date: toDate };
    if (departmentId) params.department_id = departmentId;
    return (await api.get<DailyAttendance[]>('/attendance/reports/daily', { params })).data;
};

// Absences
export interface Absence {
    id?: number;
    employee_id: number;
    employee_name?: string; // Read only
    start_date: string;
    end_date: string;
    type: string;
    reason?: string;
    approved?: boolean;
}

export const getAbsences = async () => {
    try {
        return (await api.get<Absence[]>('/attendance/absences/')).data;
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
    role: string;
    active: boolean;
    employee_id?: number | null;
    created_at?: string;
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
