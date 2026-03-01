/**
 * SIMPLIFIED EMPLOYEE SCHEDULE - Using new /attendance/schedule endpoint
 * 
 * This is a simplified reference implementation showing how to:
 * 1. Replace 5 API calls with 1 call
 * 2. Use scheduleMap for O(1) access instead of .find()
 * 3. Eliminate getDayAssignment() logic duplication
 * 
 * NOTE: This is a simplified version. The production component has more features
 * (batch assignment, multi-selection, etc.) that should be preserved.
 */

import { useState, useMemo } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useScheduleCalendar } from '../../hooks/useScheduleCalendar';
import { useScheduleMap, getScheduleFromMap } from '../../utils/scheduleMap';
import { createScheduleOverrideFromShift } from '../../api';
import { PageToolbar } from '../../components/ui/PageToolbar';

export function EmployeeScheduleSimplified() {
    const [currentMonth, setCurrentMonth] = useState(new Date());
    const [selectedCell, setSelectedCell] = useState<{ employeeId: number, date: string } | null>(null);
    const [selectedShiftId, setSelectedShiftId] = useState<number | null>(null);

    // Get month range
    const { start: monthStart, end: monthEnd } = useMemo(() => {
        const year = currentMonth.getFullYear();
        const month = currentMonth.getMonth();
        return {
            start: new Date(year, month, 1),
            end: new Date(year, month + 1, 0)
        };
    }, [currentMonth]);

    // Format dates for API
    const startDate = monthStart.toISOString().split('T')[0];
    const endDate = monthEnd.toISOString().split('T')[0];

    // SINGLE API CALL - Replaces 5 separate calls
    const { data, loading, error, refetch } = useScheduleCalendar(startDate, endDate);

    // Build scheduleMap for O(1) access (instead of O(n) .find())
    const scheduleMap = useScheduleMap(data?.employees || []);

    // Generate days in month
    const daysInMonth = useMemo(() => {
        const days: Date[] = [];
        const lastDay = monthEnd.getDate();
        for (let day = 1; day <= lastDay; day++) {
            days.push(new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day));
        }
        return days;
    }, [currentMonth, monthEnd]);

    // Navigation
    const handlePrevMonth = () => {
        const newDate = new Date(currentMonth);
        newDate.setMonth(newDate.getMonth() - 1);
        setCurrentMonth(newDate);
    };

    const handleNextMonth = () => {
        const newDate = new Date(currentMonth);
        newDate.setMonth(newDate.getMonth() + 1);
        setCurrentMonth(newDate);
    };

    // Cell click handler
    const handleCellClick = (employeeId: number, date: string) => {
        setSelectedCell({ employeeId, date });
        setSelectedShiftId(null);
    };

    // Assign shift
    const handleAssignShift = async () => {
        if (!selectedCell || !selectedShiftId) return;

        try {
            await createScheduleOverrideFromShift({
                employee_id: selectedCell.employeeId,
                shift_id: selectedShiftId,
                date: selectedCell.date,
                start_date: startDate
            });

            // Simple refetch (OK for PyME - no need for optimistic updates)
            await refetch();

            setSelectedCell(null);
            setSelectedShiftId(null);
        } catch (err) {
            console.error('Failed to assign shift:', err);
            alert('Error al asignar turno');
        }
    };

    if (loading) {
        return <div className="loading-spinner">Cargando calendario...</div>;
    }

    if (error) {
        return <div className="error-message">Error: {error.message}</div>;
    }

    if (!data) {
        return null;
    }

    return (
        <div className="page-container">
            <PageToolbar title="Calendario de Turnos" />

            {/* Month Navigation */}
            <div className="month-nav">
                <button onClick={handlePrevMonth}>
                    <ChevronLeft size={20} />
                </button>
                <span className="month-label">
                    {currentMonth.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })}
                </span>
                <button onClick={handleNextMonth}>
                    <ChevronRight size={20} />
                </button>
            </div>

            {/* Calendar Table */}
            <div className="month-calendar-wrapper">
                <table className="month-calendar-table">
                    <thead>
                        <tr>
                            <th className="employee-column sticky">Empleado</th>
                            {daysInMonth.map((day) => (
                                <th key={day.toISOString()} className="day-header">
                                    <div>{day.getDate()}</div>
                                    <div className="day-abbr">
                                        {day.toLocaleDateString('es-ES', { weekday: 'short' })}
                                    </div>
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {data.employees.map((employee) => (
                            <tr key={employee.id}>
                                <td className="employee-column sticky">
                                    {employee.name}
                                </td>
                                {daysInMonth.map((day) => {
                                    const dateStr = day.toISOString().split('T')[0];

                                    // O(1) access instead of O(n) .find()
                                    const schedule = getScheduleFromMap(scheduleMap, String(employee.id), dateStr);

                                    return (
                                        <td
                                            key={dateStr}
                                            className={`month-data-cell ${schedule?.source === 'OVERRIDE' ? 'has-override' : ''}`}
                                            onClick={() => handleCellClick(employee.id, dateStr)}
                                        >
                                            <div className="cell-content" title={schedule?.timetable || 'Sin turno'}>
                                                {schedule?.timetable || '-'}
                                            </div>
                                        </td>
                                    );
                                })}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Simple Assignment Modal */}
            {selectedCell && (
                <div className="modal-overlay" onClick={() => setSelectedCell(null)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h3>Asignar Turno</h3>
                        <p>Fecha: {selectedCell.date}</p>

                        <select
                            value={selectedShiftId || ''}
                            onChange={(e) => setSelectedShiftId(Number(e.target.value))}
                        >
                            <option value="">Seleccionar turno...</option>
                            {/* You'd need to fetch shifts separately or include in response */}
                        </select>

                        <div className="modal-actions">
                            <button onClick={handleAssignShift} disabled={!selectedShiftId}>
                                Asignar
                            </button>
                            <button onClick={() => setSelectedCell(null)}>
                                Cancelar
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

/**
 * KEY IMPROVEMENTS:
 * 
 * 1. BEFORE: 5 API calls in loadData()
 *    AFTER: 1 API call via useScheduleCalendar
 * 
 * 2. BEFORE: getDayAssignment() with complex find logic (duplicated from backend)
 *    AFTER: getScheduleFromMap() - O(1) access from pre-built map
 * 
 * 3. BEFORE: Resolving priority (Override → Employee → Department) in frontend
 *    AFTER: Backend resolves via schedule_resolver, frontend just displays
 * 
 * 4. BEFORE: Refetch all 5 API calls after POST
 *    AFTER: Simple refetch() of single endpoint
 * 
 * 5. BEFORE: getDayOverride() separate function
 *    AFTER: Included in schedule response (source: "OVERRIDE")
 * 
 * COMPLEXITY REDUCTION:
 * - Removed ~100 lines of resolution logic
 * - Removed state for assignments, overrides, shifts, departments
 * - Single source of truth: backend schedule_resolver
 * - O(n³) → O(1) for cell rendering
 */
