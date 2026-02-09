import { useEffect, useState } from 'react';
import { getEmployees, getAssignments, getShifts, assignShift, getDepartments } from '../../api';
import type { Employee, ShiftAssignment, Shift, Department } from '../../api';
import { ChevronLeft, ChevronRight, Users, X } from 'lucide-react';
import { PageToolbar } from '../../components/ui/PageToolbar';

export function EmployeeSchedule() {
    const [employees, setEmployees] = useState<Employee[]>([]);
    const [assignments, setAssignments] = useState<ShiftAssignment[]>([]);
    const [shifts, setShifts] = useState<Shift[]>([]);
    const [departments, setDepartments] = useState<Department[]>([]);

    // Filters
    const [selectedDept, setSelectedDept] = useState<string>('');
    const [showBatchModal, setShowBatchModal] = useState(false);

    // Unified Batch Form State
    const [batchForm, setBatchForm] = useState({
        targetType: 'DEPARTMENT',
        deptId: '',
        empId: '',
        shiftId: '',
        startDate: '',
        endDate: ''
    });

    const [currentDate, setCurrentDate] = useState(new Date()); // Start of view

    // Helper: Get Week Range (Mon-Sun)
    const getWeekRange = (date: Date) => {
        const start = new Date(date);
        const day = start.getDay() || 7; // 1-7 (Mon-Sun)
        if (day !== 1) start.setHours(-24 * (day - 1));

        const end = new Date(start);
        end.setDate(end.getDate() + 6);
        return { start, end };
    };

    const { start: weekStart, end: weekEnd } = getWeekRange(currentDate);

    useEffect(() => {
        loadData();
    }, [currentDate, selectedDept]);

    const loadData = async () => {
        const deptId = selectedDept ? parseInt(selectedDept) : undefined;
        const [emps, dynShifts, depts] = await Promise.all([
            getEmployees(0, 1000), // Fetch all (or paginated, but for matrix all is better)
            getShifts(),
            getDepartments()
        ]);

        // Filter employees if dept selected (client side if API doesn't support yet, or pass param)
        // API getEmployees doesn't filter by dept yet, so filter here:
        const filteredEmps = deptId ? emps.filter(e => e.department_id === deptId) : emps;
        setEmployees(filteredEmps);
        setShifts(dynShifts);
        setDepartments(depts);

        // Fetch Assignments for range
        const data = await getAssignments(weekStart.toISOString().split('T')[0], weekEnd.toISOString().split('T')[0], deptId);
        setAssignments(data);
    };

    const handlePrevWeek = () => {
        const newDate = new Date(currentDate);
        newDate.setDate(newDate.getDate() - 7);
        setCurrentDate(newDate);
    };

    const handleNextWeek = () => {
        const newDate = new Date(currentDate);
        newDate.setDate(newDate.getDate() + 7);
        setCurrentDate(newDate);
    };

    const getDayAssignment = (emp: Employee, date: Date) => {
        const dateStr = date.toISOString().split('T')[0];
        return assignments.find(a =>
            (
                (a.employee_id === emp.id) ||
                (a.scope === 'DEPARTMENT' && a.department_id === emp.department_id)
            ) &&
            a.start_date <= dateStr &&
            (!a.end_date || a.end_date >= dateStr)
        );
    };

    const [selectedCell, setSelectedCell] = useState<{ empId: number, date: Date } | null>(null);

    const handleCellClick = (empId: number, date: Date) => {
        setSelectedCell({ empId, date });
    };

    const handleAssign = async (shiftId: number) => {
        if (!selectedCell) return;
        try {
            await assignShift({
                employee_id: selectedCell.empId,
                shift_id: shiftId,
                start_date: selectedCell.date.toISOString().split('T')[0],
                // indefinite end
            });
            loadData();
            setSelectedCell(null);
        } catch (e) {
            alert("Failed to assign shift");
        }
    };

    // Unified Batch Assign Logic
    const handleBatchAssign = async () => {
        if (!batchForm.shiftId || !batchForm.startDate) return alert("Complete los campos requeridos");

        if (batchForm.targetType === 'DEPARTMENT' && !batchForm.deptId) return alert("Seleccione un Departamento");
        if (batchForm.targetType === 'EMPLOYEE' && !batchForm.empId) return alert("Seleccione un Empleado");

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
                payload.employee_id = parseInt(batchForm.empId);
            }

            await assignShift(payload);
            setShowBatchModal(false);
            loadData();
            alert("Asignación completada");
        } catch (e) {
            console.error(e);
            alert("Error al asignar");
        }
    };

    // Generate days for header
    const days: Date[] = [];
    for (let i = 0; i < 7; i++) {
        const d = new Date(weekStart);
        d.setDate(d.getDate() + i);
        days.push(d);
    }

    return (
        <div style={{ width: '100%' }}>
            <PageToolbar
                title="Programación"
                subtitle="Asignación de turnos a empleados"
                actions={
                    <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                        <button className="primary" onClick={() => setShowBatchModal(true)} style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                            <Users size={16} /> Asignar Turno Múltiple
                        </button>
                        <select
                            className="form-control"
                            value={selectedDept}
                            onChange={e => setSelectedDept(e.target.value)}
                            style={{ height: '36px', minWidth: '200px' }}
                        >
                            <option value="">Todos los Departamentos</option>
                            {departments.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
                        </select>
                        <div className="flex-row gap-2" style={{ background: 'white', padding: '4px', borderRadius: '4px', border: '1px solid #ddd' }}>
                            <button className="icon-btn" onClick={handlePrevWeek}><ChevronLeft size={16} /></button>
                            <span style={{ minWidth: '150px', textAlign: 'center', fontWeight: 500, fontSize: '14px' }}>
                                {weekStart.toLocaleDateString()} - {weekEnd.toLocaleDateString()}
                            </span>
                            <button className="icon-btn" onClick={handleNextWeek}><ChevronRight size={16} /></button>
                        </div>
                    </div>
                }
            />

            <div className="schedule-table-wrapper">
                <table className="schedule-table">
                    <thead>
                        <tr>
                            <th>Empleado</th>
                            {days.map(d => (
                                <th key={d.toISOString()} className="schedule-day-header">
                                    <div className="schedule-day-header-day">{d.toLocaleDateString(undefined, { weekday: 'short' })}</div>
                                    <div className="schedule-day-header-date">{d.getDate()}</div>
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {employees.map(emp => (
                            <tr key={emp.id}>
                                <td className="schedule-employee-cell">
                                    <div className="schedule-employee-name">{emp.name}</div>
                                    <div className="schedule-employee-id">{emp.user_id}</div>
                                </td>
                                {days.map(d => {
                                    const assign = getDayAssignment(emp, d);
                                    return (
                                        <td
                                            key={d.toISOString()}
                                            className="schedule-data-cell"
                                            onClick={() => handleCellClick(emp.id!, d)}
                                        >
                                            {assign ? (
                                                <div className="schedule-cell-assigned" title={assign.shift_name}>
                                                    {assign.shift_name}
                                                </div>
                                            ) : (
                                                <span className="schedule-cell-empty">+</span>
                                            )}
                                        </td>
                                    );
                                })}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {selectedCell && (
                <div className="shift-assignment-modal" onClick={() => setSelectedCell(null)}>
                    <div className="shift-assignment-modal-content" onClick={e => e.stopPropagation()}>
                        <h4 style={{ marginTop: 0 }}>Asignar Turno</h4>
                        <p className="shift-assignment-modal-date">
                            {selectedCell?.date.toLocaleDateString()}
                        </p>
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
                        <button className="secondary" style={{ marginTop: '10px', width: '100%' }} onClick={() => setSelectedCell(null)}>
                            Cancelar
                        </button>
                    </div>
                </div>
            )}

            {showBatchModal && (
                <div className="batch-assignment-modal" onClick={() => setShowBatchModal(false)}>
                    <div className="batch-assignment-modal-content" onClick={e => e.stopPropagation()}>
                        <div className="batch-assignment-modal-header">
                            <h3 style={{ margin: 0 }}>Asignación Masiva</h3>
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
                            <div className="form-group" style={{ marginBottom: '15px' }}>
                                <label style={{ display: 'block', marginBottom: '5px' }}>Departamento</label>
                                <select
                                    className="form-control"
                                    style={{ width: '100%', padding: '8px' }}
                                    value={batchForm.deptId}
                                    onChange={e => setBatchForm({ ...batchForm, deptId: e.target.value })}
                                >
                                    <option value="">Seleccionar Departamento</option>
                                    {departments.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
                                </select>
                            </div>
                        ) : (
                            <div className="form-group" style={{ marginBottom: '15px' }}>
                                <label style={{ display: 'block', marginBottom: '5px' }}>Empleado</label>
                                <select
                                    className="form-control"
                                    style={{ width: '100%', padding: '8px' }}
                                    value={batchForm.empId}
                                    onChange={e => setBatchForm({ ...batchForm, empId: e.target.value })}
                                >
                                    <option value="">Seleccionar Empleado</option>
                                    {employees.map(e => <option key={e.id} value={e.id}>{e.name} ({e.user_id})</option>)}
                                </select>
                            </div>
                        )}

                        <div className="form-group" style={{ marginBottom: '15px' }}>
                            <label style={{ display: 'block', marginBottom: '5px' }}>Turno</label>
                            <select
                                className="form-control"
                                style={{ width: '100%', padding: '8px' }}
                                value={batchForm.shiftId}
                                onChange={e => setBatchForm({ ...batchForm, shiftId: e.target.value })}
                            >
                                <option value="">Seleccionar Turno</option>
                                {shifts.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                            </select>
                        </div>

                        <div className="form-group" style={{ marginBottom: '15px' }}>
                            <label style={{ display: 'block', marginBottom: '5px' }}>Fecha Inicio</label>
                            <input
                                type="date"
                                className="form-control"
                                style={{ width: '100%', padding: '8px' }}
                                value={batchForm.startDate}
                                onChange={e => setBatchForm({ ...batchForm, startDate: e.target.value })}
                            />
                        </div>

                        <div className="form-group" style={{ marginBottom: '20px' }}>
                            <label style={{ display: 'block', marginBottom: '5px' }}>Fecha Fin (Opcional)</label>
                            <input
                                type="date"
                                className="form-control"
                                style={{ width: '100%', padding: '8px' }}
                                value={batchForm.endDate}
                                onChange={e => setBatchForm({ ...batchForm, endDate: e.target.value })}
                            />
                            <small className="text-muted">Dejar vacio para indefinido</small>
                        </div>

                        <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                            <button className="secondary" onClick={() => setShowBatchModal(false)}>Cancelar</button>
                            <button className="primary" onClick={handleBatchAssign}>Confirmar Asignación</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
