import { useEffect, useState } from 'react';
import { getEmployees, getAssignments, getShifts, getDepartments, getScheduleOverrides, createScheduleOverrideFromShift, getEmployeeByDate, assignShift } from '../../api';
import { EMPLOYEE_PAGE_SIZE } from '../../config/paging';
import type { Employee, ShiftAssignment, Shift, Department, ScheduleOverride } from '../../api';
import { ChevronLeft, ChevronRight, X } from 'lucide-react';
import { PageToolbar } from '../../components/ui/PageToolbar';

export function EmployeeSchedule() {
    const [employees, setEmployees] = useState<Employee[]>([]);
    const [assignments, setAssignments] = useState<ShiftAssignment[]>([]);
    const [overrides, setOverrides] = useState<ScheduleOverride[]>([]);
    const [shifts, setShifts] = useState<Shift[]>([]);
    const [departments, setDepartments] = useState<Department[]>([]);

    // Multi-selection states
    const [selectedEmployees, setSelectedEmployees] = useState<number[]>([]);
    const [selectedShifts, setSelectedShifts] = useState<number[]>([]);
    const [expandedDepts, setExpandedDepts] = useState<number[]>([]);

    // Batch assignment modal
    const [showBatchModal, setShowBatchModal] = useState(false);
    const [batchForm, setBatchForm] = useState({
        targetType: 'DEPARTMENT',
        deptId: '',
        employeeId: '',
        shiftId: '',
        startDate: '',
        endDate: ''
    });

    const [currentMonth, setCurrentMonth] = useState(new Date()); // Current month view

    // Helper: Get Month Range (first day to last day)
    const getMonthRange = (date: Date) => {
        const year = date.getFullYear();
        const month = date.getMonth();
        const start = new Date(year, month, 1);
        const end = new Date(year, month + 1, 0);
        return { start, end };
    };

    const { start: monthStart, end: monthEnd } = getMonthRange(currentMonth);

    useEffect(() => {
        loadData();
    }, [currentMonth]);

    const loadData = async () => {
        const [emps, dynShifts, depts, monthOverrides] = await Promise.all([
            getEmployees(0, EMPLOYEE_PAGE_SIZE),
            getShifts(),
            getDepartments(),
            getScheduleOverrides(monthStart.toISOString().split('T')[0], monthEnd.toISOString().split('T')[0])
        ]);

        setEmployees(emps);
        setShifts(dynShifts);
        setDepartments(depts);
        setOverrides(monthOverrides);

        // Fetch Assignments for month range
        const data = await getAssignments(monthStart.toISOString().split('T')[0], monthEnd.toISOString().split('T')[0]);
        setAssignments(data);
    };

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

    const getDayAssignment = (emp: Employee, date: Date) => {
        const dateStr = date.toISOString().split('T')[0];
        return assignments.find(a =>
            (
                (a.employee_id === emp.id) ||
                (a.user_id === emp.user_id) ||
                (a.scope === 'DEPARTMENT' && a.department_id === emp.department_id)
            ) &&
            a.start_date <= dateStr &&
            (!a.end_date || a.end_date >= dateStr)
        );
    };

    const getDayOverride = (emp: Employee, date: Date) => {
        const dateStr = date.toISOString().split('T')[0];
        return overrides.find(o => (String(o.employee) === String(emp.id) || String(o.employee) === String(emp.user_id)) && o.date === dateStr);
    };

    const [selectedCell, setSelectedCell] = useState<{ employeeId: number, date: Date } | null>(null);
    const [selectedScheduleInfo, setSelectedScheduleInfo] = useState<Employee | null>(null);

    const handleCellClick = async (employeeId: number, date: Date) => {
        setSelectedCell({ employeeId, date });
        try {
            const dateStr = date.toISOString().split('T')[0];
            const emp = await getEmployeeByDate(employeeId, dateStr);
            setSelectedScheduleInfo(emp);
        } catch (e) {
            setSelectedScheduleInfo(null);
        }
    };

    const handleAssign = async (shiftId: number) => {
        if (!selectedCell) return;
        try {
            await createScheduleOverrideFromShift({
                employee_id: selectedCell.employeeId,
                shift_id: shiftId,
                date: selectedCell.date.toISOString().split('T')[0]
            });
            loadData();
            setSelectedCell(null);
            setSelectedScheduleInfo(null);
        } catch (error: any) {
            const message =
                error?.response?.data?.shift ||
                error?.response?.data?.detail ||
                "No se pudo aplicar el cambio de turno para este día";
            alert(message);
        }
    };

    const handleBatchAssign = async () => {
        if (!batchForm.shiftId || !batchForm.startDate) return alert("Complete los campos requeridos");

        if (batchForm.targetType === 'DEPARTMENT' && !batchForm.deptId) return alert("Seleccione un Departamento");
        if (batchForm.targetType === 'EMPLOYEE' && !batchForm.employeeId) return alert("Seleccione un Empleado");

        try {
            const payload: any = {
                shift_id: parseInt(batchForm.shiftId),
                start_date: batchForm.startDate,
                end_date: batchForm.endDate || undefined,
                scope: batchForm.targetType
            };

            if (batchForm.targetType === 'DEPARTMENT') {
                payload.department_id = parseInt(batchForm.deptId);
            } else {
                payload.employee_id = parseInt(batchForm.employeeId);
            }

            await assignShift(payload);
            setShowBatchModal(false);
            loadData();
            alert("Asignación completada");
        } catch (error: any) {
            const message =
                error?.response?.data?.shift ||
                error?.response?.data?.detail ||
                "Error al asignar";
            alert(message);
        }
    };

    // Multi-selection handlers
    const toggleEmployee = (employeeId: number) => {
        setSelectedEmployees(prev =>
            prev.includes(employeeId) ? prev.filter(id => id !== employeeId) : [...prev, employeeId]
        );
    };

    const toggleDepartment = (deptId: number) => {
        const deptEmps = employees.filter(e => e.department_id === deptId && !!e.id).map(e => e.id as number);
        const allSelected = deptEmps.every(id => selectedEmployees.includes(id));

        if (allSelected) {
            setSelectedEmployees(prev => prev.filter(id => !deptEmps.includes(id)));
        } else {
            setSelectedEmployees(prev => [...new Set([...prev, ...deptEmps])]);
        }
    };

    const toggleAllEmployees = () => {
        if (selectedEmployees.length === employees.length) {
            setSelectedEmployees([]);
        } else {
            setSelectedEmployees(employees.filter(e => !!e.id).map(e => e.id as number));
        }
    };

    const toggleShift = (shiftId: number) => {
        setSelectedShifts(prev =>
            prev.includes(shiftId) ? prev.filter(id => id !== shiftId) : [...prev, shiftId]
        );
    };

    const toggleDeptExpand = (deptId: number) => {
        setExpandedDepts(prev =>
            prev.includes(deptId) ? prev.filter(id => id !== deptId) : [...prev, deptId]
        );
    };

    // Generate days for month
    const daysInMonth: Date[] = [];
    const current = new Date(monthStart);
    while (current <= monthEnd) {
        daysInMonth.push(new Date(current));
        current.setDate(current.getDate() + 1);
    }

    // Filter displayed employees
    const displayedEmployees = selectedEmployees.length > 0
        ? employees.filter(e => !!e.id && selectedEmployees.includes(e.id))
        : employees;

    // Month name
    const monthName = currentMonth.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' });

    return (
        <div className="w-full" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <PageToolbar
                title="Programación de Turnos"
                subtitle={`Vista mensual: ${monthName}`}
                actions={
                    <div className="flex-row gap-3">
                        <div className="flex-row gap-2 week-nav-control">
                            <button className="icon-btn" onClick={handlePrevMonth}><ChevronLeft size={16} /></button>
                            <span className="week-range-text">{monthName}</span>
                            <button className="icon-btn" onClick={handleNextMonth}><ChevronRight size={16} /></button>
                        </div>
                    </div>
                }
            />

            <div style={{ display: 'flex', flex: 1, gap: '16px', padding: '16px', overflow: 'hidden' }}>
                {/* Left Sidebar: Employee + Shift Selectors */}
                <div style={{ width: '280px', display: 'flex', flexDirection: 'column', gap: '16px', flexShrink: 0 }}>
                    {/* Employee Selector */}
                    <div className="card" style={{ padding: '16px', maxHeight: '50%', overflow: 'auto' }}>
                        <h4 style={{ margin: '0 0 12px 0' }}>Empleados</h4>
                        <div className="flex-row gap-2 mb-3">
                            <input
                                type="checkbox"
                                checked={selectedEmployees.length === employees.length && employees.length > 0}
                                onChange={toggleAllEmployees}
                            />
                            <label style={{ fontWeight: 500 }}>
                                Todos ({selectedEmployees.length}/{employees.length})
                            </label>
                        </div>

                        {departments.map(dept => {
                            const deptEmps = employees.filter(e => e.department_id === dept.id);
                            if (deptEmps.length === 0) return null;
                            const isExpanded = expandedDepts.includes(dept.id!);
                            const allDeptSelected = deptEmps.every(e => !!e.id && selectedEmployees.includes(e.id));

                            return (
                                <div key={dept.id} style={{ marginBottom: '8px' }}>
                                    <div className="flex-row gap-2" style={{ cursor: 'pointer', padding: '4px' }}>
                                        <input
                                            type="checkbox"
                                            checked={allDeptSelected}
                                            onChange={() => toggleDepartment(dept.id!)}
                                        />
                                        <label
                                            onClick={() => toggleDeptExpand(dept.id!)}
                                            style={{ flex: 1, fontWeight: 500 }}
                                        >
                                            {dept.name} ({deptEmps.length})
                                        </label>
                                        <span onClick={() => toggleDeptExpand(dept.id!)}>{isExpanded ? '▼' : '▶'}</span>
                                    </div>

                                    {isExpanded && deptEmps.map(emp => (
                                        <div key={emp.id ?? emp.user_id} className="flex-row gap-2" style={{ paddingLeft: '24px', padding: '2px 2px 2px 24px' }}>
                                            <input
                                                type="checkbox"
                                                checked={!!emp.id && selectedEmployees.includes(emp.id)}
                                                onChange={() => emp.id && toggleEmployee(emp.id)}
                                            />
                                            <label style={{ fontSize: '13px' }}>{emp.name} ({emp.user_id})</label>
                                        </div>
                                    ))}
                                </div>
                            );
                        })}
                    </div>

                    {/* Shift Selector */}
                    <div className="card" style={{ padding: '16px' }}>
                        <h4 style={{ margin: '0 0 12px 0' }}>Filtrar Turnos</h4>
                        {shifts.map(shift => (
                            <div key={shift.id} className="flex-row gap-2" style={{ marginBottom: '6px' }}>
                                <input
                                    type="checkbox"
                                    checked={selectedShifts.includes(shift.id!)}
                                    onChange={() => toggleShift(shift.id!)}
                                />
                                <label>{shift.name}</label>
                            </div>
                        ))}
                        <button
                            className="primary w-full mt-3"
                            onClick={() => setShowBatchModal(true)}
                        >
                            Asignación Masiva
                        </button>
                    </div>
                </div>

                {/* Right: Month Calendar */}
                <div className="card" style={{ flex: 1, padding: '16px', overflow: 'auto' }}>
                    <div className="month-calendar-wrapper">
                        <table className="month-calendar-table">
                            <thead>
                                <tr>
                                    <th style={{ position: 'sticky', left: 0, zIndex: 20, background: 'var(--bg-card)' }}>Empleado</th>
                                    {daysInMonth.map(day => (
                                        <th key={day.toISOString()} className="month-day-header">
                                            <div className="month-day-weekday">{day.toLocaleDateString('es-ES', { weekday: 'short' })}</div>
                                            <div className="month-day-number">{day.getDate()}</div>
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {displayedEmployees.map(emp => (
                                    <tr key={emp.id ?? emp.user_id}>
                                        <td className="month-employee-cell" style={{ position: 'sticky', left: 0, zIndex: 10, background: 'var(--bg-card)' }}>
                                            <div className="month-employee-name">{emp.name}</div>
                                            <div className="month-employee-id">{emp.user_id}</div>
                                        </td>
                                        {daysInMonth.map(day => {
                                            const override = getDayOverride(emp, day);
                                            const assign = getDayAssignment(emp, day);
                                            const shiftName = override?.timetable_name || assign?.shift_name;

                                            // Filter by selected shifts
                                            const isFiltered = selectedShifts.length > 0 && assign && !selectedShifts.includes(assign.shift_id);

                                            return (
                                                <td
                                                    key={day.toISOString()}
                                                    className={`month-data-cell ${isFiltered ? 'filtered-out' : ''}`}
                                                    onClick={() => emp.id && handleCellClick(emp.id, day)}
                                                    title={shiftName || 'Sin asignar'}
                                                >
                                                    {shiftName ? (
                                                        <div className="month-cell-shift">{shiftName.substring(0, 3)}</div>
                                                    ) : (
                                                        <span className="month-cell-empty">-</span>
                                                    )}
                                                </td>
                                            );
                                        })}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* Individual Assignment Modal */}
            {selectedCell && (
                <div className="shift-assignment-modal" onClick={() => { setSelectedCell(null); setSelectedScheduleInfo(null); }}>
                    <div className="shift-assignment-modal-content" onClick={e => e.stopPropagation()}>
                        <h4 className="mt-0">Cambiar Turno por Día</h4>
                        <p className="shift-assignment-modal-date">
                            {selectedCell?.date.toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                        </p>
                        {selectedScheduleInfo && (
                            <div className="mb-3 text-sm">
                                <div><strong>Turno actual:</strong> {selectedScheduleInfo.current_shift?.name || 'Sin turno'}</div>
                                <div><strong>Horario actual:</strong> {selectedScheduleInfo.current_timetable?.name || 'Sin horario'}</div>
                                <div><strong>Origen:</strong> {selectedScheduleInfo.schedule_source?.description || 'N/A'}</div>
                            </div>
                        )}
                        <div className="shift-assignment-modal-list">
                            {shifts.map(s => (
                                <button
                                    key={s.id}
                                    className="shift-assignment-modal-button"
                                    onClick={() => s.id && handleAssign(s.id)}
                                >
                                    {s.name}
                                </button>
                            ))}
                        </div>
                        <button className="secondary mt-2 w-full" onClick={() => setSelectedCell(null)}>
                            Cancelar
                        </button>
                    </div>
                </div>
            )}

            {/* Batch Assignment Modal */}
            {showBatchModal && (
                <div className="batch-assignment-modal" onClick={() => setShowBatchModal(false)}>
                    <div className="batch-assignment-modal-content" onClick={e => e.stopPropagation()}>
                        <div className="batch-assignment-modal-header">
                            <h3 className="m-0">Asignación Masiva</h3>
                            <button className="icon-btn" onClick={() => setShowBatchModal(false)}><X size={20} /></button>
                        </div>

                        {/* Tabs */}
                        <div className="batch-assignment-modal-tabs">
                            <div
                                className={`batch-assignment-modal-tab ${batchForm.targetType === 'DEPARTMENT' ? 'active' : ''}`}
                                onClick={() => setBatchForm(p => ({ ...p, targetType: 'DEPARTMENT' }))}
                            >
                                Por Departamento
                            </div>
                            <div
                                className={`batch-assignment-modal-tab ${batchForm.targetType === 'EMPLOYEE' ? 'active' : ''}`}
                                onClick={() => setBatchForm(p => ({ ...p, targetType: 'EMPLOYEE' }))}
                            >
                                Por Empleado
                            </div>
                        </div>

                        {/* Conditional Select */}
                        {batchForm.targetType === 'DEPARTMENT' ? (
                            <div className="form-group mb-4">
                                <label className="form-label">Departamento</label>
                                <select
                                    className="form-control w-full"
                                    value={batchForm.deptId}
                                    onChange={e => setBatchForm({ ...batchForm, deptId: e.target.value })}
                                >
                                    <option value="">Seleccionar Departamento</option>
                                    {departments.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
                                </select>
                            </div>
                        ) : (
                            <div className="form-group mb-4">
                                <label className="form-label">Empleado</label>
                                <select
                                    className="form-control w-full"
                                    value={batchForm.employeeId}
                                    onChange={e => setBatchForm({ ...batchForm, employeeId: e.target.value })}
                                >
                                    <option value="">Seleccionar Empleado</option>
                                    {employees.filter(e => !!e.id).map(e => <option key={e.id} value={e.id}>{e.name} ({e.user_id})</option>)}
                                </select>
                            </div>
                        )}

                        <div className="form-group mb-4">
                            <label className="form-label">Turno</label>
                            <select
                                className="form-control w-full"
                                value={batchForm.shiftId}
                                onChange={e => setBatchForm({ ...batchForm, shiftId: e.target.value })}
                            >
                                <option value="">Seleccionar Turno</option>
                                {shifts.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                            </select>
                        </div>

                        <div className="form-group mb-4">
                            <label className="form-label">Fecha Inicio</label>
                            <input
                                type="date"
                                className="form-control w-full"
                                value={batchForm.startDate}
                                onChange={e => setBatchForm({ ...batchForm, startDate: e.target.value })}
                            />
                        </div>

                        <div className="form-group mb-5">
                            <label className="form-label">Fecha Fin (Opcional)</label>
                            <input
                                type="date"
                                className="form-control w-full"
                                value={batchForm.endDate}
                                onChange={e => setBatchForm({ ...batchForm, endDate: e.target.value })}
                            />
                            <small className="text-muted">Dejar vacio para indefinido</small>
                        </div>

                        <div className="flex-row gap-3 flex-end">
                            <button className="secondary" onClick={() => setShowBatchModal(false)}>Cancelar</button>
                            <button className="primary" onClick={handleBatchAssign}>Confirmar Asignación</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
