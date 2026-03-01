import { useMemo } from 'react';
import type { EmployeeSchedule, ScheduleDay } from '../hooks/useScheduleCalendar';

/**
 * Schedule map for O(1) access by employee ID and date.
 * 
 * Structure:
 * {
 *   [employeeKey]: {
 *     [dateStr]: ScheduleDay
 *   }
 * }
 * 
 * This avoids .find() in nested loops which would be O(n²) or O(n³).
 */
export type ScheduleMap = Record<string, Record<string, ScheduleDay>>;

/**
 * Transform schedule calendar data into a map for O(1) access.
 * 
 * Use this in a useMemo to avoid recomputing on every render.
 * 
 * @param employees - Array of employee schedules
 * @returns Schedule map indexed by employee ID and date
 * 
 * @example
 * const scheduleMap = useMemo(
 *   () => buildScheduleMap(data.employees),
 *   [data.employees]
 * );
 * 
 * // O(1) access instead of O(n) .find()
 * const schedule = scheduleMap[employee.id]?.[dateStr];
 */
export function buildScheduleMap(employees: EmployeeSchedule[]): ScheduleMap {
    const map: ScheduleMap = {};

    for (const employee of employees) {
        const employeeKey = String(employee.id);
        map[employeeKey] = {};

        for (const day of employee.schedule) {
            map[employeeKey][day.date] = day;
        }
    }

    return map;
}

/**
 * Get schedule for a specific employee and date from the map.
 * 
 * @param scheduleMap - Pre-built schedule map
 * @param employeeKey - Employee key (usually employee.id as string)
 * @param dateStr - Date in YYYY-MM-DD format
 * @returns Schedule day or null if not found
 */
export function getScheduleFromMap(
    scheduleMap: ScheduleMap,
    employeeKey: string,
    dateStr: string
): ScheduleDay | null {
    return scheduleMap[employeeKey]?.[dateStr] || null;
}

/**
 * Hook to build schedule map with useMemo optimization.
 * 
 * @param employees - Array of employee schedules
 * @returns Memoized schedule map
 * 
 * @example
 * const scheduleMap = useScheduleMap(data.employees);
 * const schedule = getScheduleFromMap(scheduleMap, employee.id, dateStr);
 */
export function useScheduleMap(employees: EmployeeSchedule[]): ScheduleMap {
    return useMemo(() => buildScheduleMap(employees), [employees]);
}
