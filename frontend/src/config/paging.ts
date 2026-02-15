const DEFAULT_EMPLOYEE_PAGE_SIZE = 1000;
const envEmployeePageSize = Number(import.meta.env.VITE_EMPLOYEE_PAGE_SIZE);

export const EMPLOYEE_PAGE_SIZE = Number.isFinite(envEmployeePageSize) && envEmployeePageSize > 0
    ? envEmployeePageSize
    : DEFAULT_EMPLOYEE_PAGE_SIZE;
