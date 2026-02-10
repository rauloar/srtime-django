import React, { useEffect, useState } from 'react';
import { Folder, Plus, Edit2, Trash2, ChevronRight } from 'lucide-react';
import { getDepartments, createDepartment, updateDepartment, deleteDepartment, getEmployees, getShifts, getAssignments, assignShift, type Department, type Employee, type Shift, type ShiftAssignment } from '../../api';
import { DataGrid, type Column } from '../../components/ui/DataGrid';
import { PageToolbar } from '../../components/ui/PageToolbar';
import { ConfirmDialog } from '../../components/ui/ConfirmDialog';
import { sortDepartmentsTree, type DepartmentNode } from '../../utils/treeUtils';

export const Departments: React.FC = () => {
    const [departments, setDepartments] = useState<DepartmentNode[]>([]);
    const [originalDepts, setOriginalDepts] = useState<Department[]>([]);
    const [employees, setEmployees] = useState<Employee[]>([]);
    const [shifts, setShifts] = useState<Shift[]>([]);
    const [deptAssignments, setDeptAssignments] = useState<ShiftAssignment[]>([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingDept, setEditingDept] = useState<DepartmentNode | null>(null);
    const [searchTerm, setSearchTerm] = useState('');

    // Confirm Dialog State
    const [confirmOpen, setConfirmOpen] = useState(false);
    const [deptToDelete, setDeptToDelete] = useState<number | null>(null);

    const fetchData = async () => {
        setLoading(true);
        try {
            const today = new Date().toISOString().split('T')[0];
            const [depts, emps, shiftsList, assignments] = await Promise.all([
                getDepartments(),
                getEmployees(0, 1000), // Fetch strict list for validation
                getShifts(),
                getAssignments(today, today) // Get all assignments for today
            ]);
            setOriginalDepts(depts);
            setDepartments(sortDepartmentsTree(depts));
            setEmployees(emps);
            setShifts(shiftsList);
            // Filter only DEPARTMENT scope assignments
            setDeptAssignments(assignments.filter(a => a.scope === 'DEPARTMENT'));
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleSave = async (dept: Department) => {
        try {
            if (dept.id) await updateDepartment(dept.id, dept);
            else await createDepartment(dept);
            setIsModalOpen(false);
            fetchData();
        } catch (error: any) {
            alert('Error: ' + error.message);
        }
    };

    const confirmDelete = (id: number) => {
        // Safe Delete Check
        const count = employees.filter(e => e.department_id === id).length;
        if (count > 0) {
            alert(`No se puede eliminar: El departamento tiene ${count} empleados asignados. Transfiéralos primero.`);
            return;
        }
        // Check children
        const hasChildren = departments.some(d => d.parent_id === id);
        if (hasChildren) {
            alert(`No se puede eliminar: El departamento tiene sub-departamentos. Elimínelos o muévalos primero.`);
            return;
        }

        setDeptToDelete(id);
        setConfirmOpen(true);
    };

    const executeDelete = async () => {
        if (!deptToDelete) return;
        try {
            await deleteDepartment(deptToDelete);
            setConfirmOpen(false);
            fetchData();
        } catch (error: any) {
            alert('Error deleting department');
        }
    };

    const getParentName = (id?: number) => {
        if (!id) return '-';
        // Use originalDepts for lookup
        const d = originalDepts.find(d => d.id === id);
        return d ? d.name : id;
    };

    const getDepartmentShift = (deptId?: number) => {
        if (!deptId) return null;
        const assignment = deptAssignments.find(a => a.department_id === deptId);
        return assignment ? assignment.shift_name : null;
    };

    const filteredDepartments = departments.filter(d =>
        d.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (d.code && d.code.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    const columns: Column<DepartmentNode>[] = [
        {
            field: 'name',
            header: 'Nombre Departamento',
            render: (dept) => (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', paddingLeft: `${dept.level * 20}px` }}>
                    {dept.level > 0 && <ChevronRight size={14} color="#aaa" />}
                    <Folder size={16} color="var(--primary)" />
                    <span style={{ fontWeight: 500 }}>{dept.name}</span>
                </div>
            )
        },
        {
            field: 'code',
            header: 'Código',
            width: '150px',
            render: (dept) => dept.code || '-'
        },
        {
            field: 'parent_id',
            header: 'Departamento Superior',
            render: (dept) => getParentName(dept.parent_id)
        },
        {
            field: 'assigned_shift',
            header: 'Turno Asignado',
            width: '200px',
            render: (dept) => {
                const shiftName = getDepartmentShift(dept.id);
                return shiftName ? (
                    <span style={{ 
                        padding: '4px 10px', 
                        background: '#e3f2fd', 
                        color: '#1565c0', 
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: 500
                    }}>
                        {shiftName}
                    </span>
                ) : (
                    <span style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>Sin turno</span>
                );
            }
        },
        {
            field: 'actions',
            header: 'Acciones',
            align: 'right',
            width: '100px',
            render: (dept) => (
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '5px' }}>
                    <button
                        className="icon-btn"
                        onClick={(e) => { e.stopPropagation(); setEditingDept(dept); setIsModalOpen(true); }}
                        title="Editar"
                    >
                        <Edit2 size={16} />
                    </button>
                    <button
                        className="icon-btn danger"
                        onClick={(e) => { e.stopPropagation(); dept.id && confirmDelete(dept.id); }}
                        title="Eliminar"
                    >
                        <Trash2 size={16} />
                    </button>
                </div>
            )
        }
    ];

    return (
        <div style={{ width: '100%' }}>
            <PageToolbar
                title="Departamentos"
                subtitle="Estructura organizativa de la empresa"
                onSearch={setSearchTerm}
                searchPlaceholder="Buscar por nombre o código..."
                actions={
                    <button className="primary flex-row gap-2" onClick={() => { setEditingDept(null); setIsModalOpen(true); }} disabled>
                        <Plus size={16} /> Nuevo Departamento
                    </button>
                }
            />

            <div className="page-card">
                <DataGrid
                    columns={columns}
                    data={filteredDepartments}
                    loading={loading}
                    placeholder="No hay departamentos definidos"
                />
            </div>

            {isModalOpen && (
                <DepartmentModal
                    department={editingDept}
                    onClose={() => setIsModalOpen(false)}
                    onSave={handleSave}
                    departments={departments}
                    shifts={shifts}
                    currentAssignment={editingDept ? deptAssignments.find(a => a.department_id === editingDept.id) : undefined}
                    onShiftAssign={async (deptId, shiftId) => {
                        if (!deptId || !shiftId) return;
                        try {
                            await assignShift({
                                department_id: deptId,
                                shift_id: shiftId,
                                scope: 'DEPARTMENT',
                                start_date: new Date().toISOString().split('T')[0]
                            });
                            fetchData();
                        } catch (error) {
                            console.error('Error assigning shift:', error);
                            throw error;
                        }
                    }}
                />
            )}

            <ConfirmDialog
                isOpen={confirmOpen}
                title="Eliminar Departamento"
                message="¿Está seguro de que desea eliminar este departamento? Esta acción no se puede deshacer."
                onConfirm={executeDelete}
                onCancel={() => setConfirmOpen(false)}
                type="danger"
            />
        </div>
    );
};

const DepartmentModal: React.FC<{
    department: DepartmentNode | null,
    onClose: () => void,
    onSave: (d: Department) => void,
    departments: DepartmentNode[],
    shifts: Shift[],
    currentAssignment?: ShiftAssignment,
    onShiftAssign: (deptId: number, shiftId: number) => Promise<void>
}> = ({ department, onClose, onSave, departments, shifts, currentAssignment, onShiftAssign }) => {
    const [name, setName] = useState(department?.name || '');
    const [code, setCode] = useState(department?.code || '');
    const [parentId, setParentId] = useState<number | undefined>(department?.parent_id);
    const [selectedShiftId, setSelectedShiftId] = useState<number | undefined>(currentAssignment?.shift_id);
    const [saving, setSaving] = useState(false);

    return (
        <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: 'var(--modal-overlay)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
        }}>
            <div className="card" style={{ width: '400px', padding: '20px' }}>
                <h3>{department ? 'Editar Departamento' : 'Nuevo Departamento'}</h3>

                <div className="flex-col gap-4">
                    <div className="flex-col gap-2">
                        <label className="text-muted" style={{ fontSize: '12px' }}>Nombre</label>
                        <input value={name} onChange={e => setName(e.target.value)} placeholder="Ej: Recursos Humanos" />
                    </div>

                    <div className="flex-col gap-2">
                        <label className="text-muted" style={{ fontSize: '12px' }}>Código</label>
                        <input value={code} onChange={e => setCode(e.target.value)} placeholder="Ej: HR-001" />
                    </div>

                    <div className="flex-col gap-2">
                        <label className="text-muted" style={{ fontSize: '12px' }}>Departamento Superior</label>
                        <select
                            value={parentId || ''}
                            onChange={e => setParentId(e.target.value ? Number(e.target.value) : undefined)}
                        >
                            <option value="">-- Ninguno (Raíz) --</option>
                            {departments.filter(d => d.id !== department?.id).map(d => (
                                <option key={d.id} value={d.id}>
                                    {/* Show tree hierarchy in select */}
                                    {/* Using non-breaking spaces for indentation in standard select */}
                                    {'\u00A0\u00A0'.repeat(d.level) + d.name}
                                </option>
                            ))}
                        </select>
                    </div>

                    {department && (
                        <div className="flex-col gap-2" style={{ borderTop: '1px solid var(--border)', paddingTop: '15px' }}>
                            <label className="text-muted" style={{ fontSize: '12px', fontWeight: 600 }}>⏰ Turno Asignado</label>
                            <select
                                value={selectedShiftId || ''}
                                onChange={e => setSelectedShiftId(e.target.value ? Number(e.target.value) : undefined)}
                            >
                                <option value="">-- Sin turno --</option>
                                {shifts.map(s => (
                                    <option key={s.id} value={s.id}>{s.name}</option>
                                ))}
                            </select>
                            <small className="text-muted" style={{ fontSize: '11px', lineHeight: '1.4' }}>
                                Este turno se aplicará automáticamente a todos los empleados del departamento que no tengan una asignación individual.
                            </small>
                        </div>
                    )}

                    <div className="flex-row gap-2" style={{ marginTop: '10px', justifyContent: 'flex-end' }}>
                        <button onClick={onClose} disabled={saving}>Cancelar</button>
                        <button className="primary" disabled={saving} onClick={async () => {
                            setSaving(true);
                            try {
                                // Save only API fields to avoid sending tree metadata
                                await onSave({ id: department?.id, name, code, parent_id: parentId });
                                // Then save shift assignment if department exists and shift selected
                                if (department?.id && selectedShiftId && selectedShiftId !== currentAssignment?.shift_id) {
                                    await onShiftAssign(department.id, selectedShiftId);
                                }
                            } catch (error) {
                                alert('Error al guardar');
                            } finally {
                                setSaving(false);
                            }
                        }}>{saving ? 'Guardando...' : 'Guardar'}</button>
                    </div>
                </div>
            </div>
        </div>
    );
};
