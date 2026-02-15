import { useState, useEffect } from 'react';
import { api } from '../api';

/**
 * Schedule day for an employee
 */
export interface ScheduleDay {
    date: string;
    timetable: string | null;
    on_duty: string | null;
    off_duty: string | null;
    source: string;
    is_rest: boolean;
}

/**
 * Employee schedule projection
 */
export interface EmployeeSchedule {
    id: number;
    user_id: string;
    name: string;
    department_id: number | null;
    schedule: ScheduleDay[];
}

/**
 * Schedule calendar response
 */
export interface ScheduleCalendar {
    employees: EmployeeSchedule[];
}

/**
 * Hook to fetch schedule calendar from new endpoint.
 * Replaces 5 API calls with 1 single call.
 * 
 * @param startDate - Start date in YYYY-MM-DD format
 * @param endDate - End date in YYYY-MM-DD format
 * @returns Schedule calendar data, loading state, error, and refetch function
 */
export function useScheduleCalendar(startDate: string, endDate: string) {
    const [data, setData] = useState<ScheduleCalendar | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        let cancelled = false;

        async function fetchSchedule() {
            setLoading(true);
            setError(null);

            try {
                const response = await api.get<ScheduleCalendar>(
                    `/attendance/schedule/?start_date=${startDate}&end_date=${endDate}`
                );

                if (!cancelled) {
                    setData(response.data);
                }
            } catch (err) {
                if (!cancelled) {
                    setError(err as Error);
                }
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        }

        fetchSchedule();

        return () => {
            cancelled = true;
        };
    }, [startDate, endDate]);

    /**
     * Refetch schedule data (e.g., after creating an override).
     * Simple approach: just fetch everything again (OK for PyME).
     */
    const refetch = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await api.get<ScheduleCalendar>(
                `/attendance/schedule/?start_date=${startDate}&end_date=${endDate}`
            );
            setData(response.data);
        } catch (err) {
            setError(err as Error);
        } finally {
            setLoading(false);
        }
    };

    return { data, loading, error, refetch };
}
