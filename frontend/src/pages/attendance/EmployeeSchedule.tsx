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

            <div className="card" style={{ padding: 0, overflowX: 'auto', border: 'none', background: 'transparent' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '800px', background: 'white', borderRadius: '4px', overflow: 'hidden' }}>
                    <thead>
                        <tr style={{ background: '#f8f9fa', borderBottom: '2px solid #eee' }}>
                            <th style={{ padding: '12px', textAlign: 'left', position: 'sticky', left: 0, background: '#f8f9fa', zIndex: 2 }}>Empleado</th>
                            {days.map(d => (
                                <th key={d.toISOString()} style={{ padding: '12px', textAlign: 'center' }}>
                                    <div style={{ fontWeight: 600 }}>{d.toLocaleDateString(undefined, { weekday: 'short' })}</div>
                                    <div style={{ fontSize: '0.8em', color: '#666' }}>{d.getDate()}</div>
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {employees.map(emp => (
                            <tr key={emp.id} style={{ borderBottom: '1px solid #eee' }}>
                                <td style={{ padding: '10px', position: 'sticky', left: 0, background: 'white', zIndex: 1, borderRight: '1px solid #eee' }}>
                                    <div style={{ fontWeight: 500 }}>{emp.name}</div>
                                    <div style={{ fontSize: '0.75em', color: '#888' }}>{emp.user_id}</div>
                                </td>
                                {days.map(d => {
                                    const assign = getDayAssignment(emp, d);
                                    return (
                                        <td
                                            key={d.toISOString()}
                                            style={{ padding: '8px', textAlign: 'center', cursor: 'pointer', borderLeft: '1px solid #eee' }}
                                            onClick={() => handleCellClick(emp.id!, d)}
                                            className="hover-cell"
                                        >
                                            {assign ? (
                                                <div style={{
                                                    background: '#e3f2fd',
                                                    color: '#1565c0',
                                                    padding: '4px 8px',
                                                    borderRadius: '4px',
                                                    fontSize: '0.85em',
                                                    fontWeight: 500,
                                                    whiteSpace: 'nowrap',
                                                    overflow: 'hidden',
                                                    textOverflow: 'ellipsis',
                                                    maxWidth: '100px'
                                                }} title={assign.shift_name}>
                                                    {assign.shift_name}
                                                </div>
                                            ) : (
                                                <span style={{ color: '#eee', fontSize: '1.2em' }}>+</span>
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
                <div style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                    backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
                }} onClick={() => setSelectedCell(null)}>
                    <div className="card" style={{ width: '300px', padding: '20px' }} onClick={e => e.stopPropagation()}>
                        <h4 style={{ marginTop: 0 }}>Asignar Turno</h4>
                        <p className="text-muted" style={{ fontSize: '0.9em' }}>
                            {selectedCell?.date.toLocaleDateString()}
                        </p>
                        <div className="flex-col gap-2" style={{ maxHeight: '300px', overflowY: 'auto' }}>
                            {shifts.map(s => (
                                <button
                                    key={s.id}
                                    style={{ textAlign: 'left', padding: '10px', border: '1px solid #eee', background: 'white', cursor: 'pointer' }}
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
                <div style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                    backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
                }} onClick={() => setShowBatchModal(false)}>
                    <div className="card" style={{ width: '400px', padding: '20px' }} onClick={e => e.stopPropagation()}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
                            <h3 style={{ margin: 0 }}>Asignación Masiva</h3>
                            <button className="icon-btn" onClick={() => setShowBatchModal(false)}><X size={20} /></button>
                        </div>

                        {/* Tabs */}
                        <div style={{ display: 'flex', marginBottom: '15px', borderBottom: '1px solid #eee' }}>
                            <div
                                style={{ padding: '10px 20px', cursor: 'pointer', borderBottom: batchForm.targetType === 'DEPARTMENT' ? '2px solid #007bff' : 'none', fontWeight: batchForm.targetType === 'DEPARTMENT' ? 600 : 400, color: batchForm.targetType === 'DEPARTMENT' ? '#007bff' : '#666' }}
                                onClick={() => setBatchForm(p => ({ ...p, targetType: 'DEPARTMENT' }))}
                            >
                                Por Departamento
                            </div>
                            <div
                                style={{ padding: '10px 20px', cursor: 'pointer', borderBottom: batchForm.targetType === 'EMPLOYEE' ? '2px solid #007bff' : 'none', fontWeight: batchForm.targetType === 'EMPLOYEE' ? 600 : 400, color: batchForm.targetType === 'EMPLOYEE' ? '#007bff' : '#666' }}
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
