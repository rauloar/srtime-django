import React, { useEffect, useState } from 'react';
import { Folder, Plus, Edit2, Trash2, ChevronRight } from 'lucide-react';
import { getDepartments, createDepartment, updateDepartment, deleteDepartment, getCompanies, getEmployees, getShifts, getAssignments, assignShift, type Department, type Employee, type Shift, type ShiftAssignment, type Company } from '../../api';
import { EMPLOYEE_PAGE_SIZE } from '../../config/paging';
import { DataGrid, type Column } from '../../components/ui/DataGrid';
import { PageToolbar } from '../../components/ui/PageToolbar';
import { ConfirmDialog } from '../../components/ui/ConfirmDialog';
import { sortDepartmentsTree, type DepartmentNode } from '../../utils/treeUtils';
import { useToast } from '../../hooks/useToast';

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
    const { error: showError } = useToast();

    // Confirm Dialog State
    const [confirmOpen, setConfirmOpen] = useState(false);
    const [deptToDelete, setDeptToDelete] = useState<number | null>(null);

    // Load companies for selector in DepartmentModal
    const [companies, setCompanies] = useState<Company[]>([]);

    const fetchData = async () => {
        setLoading(true);
        try {
            const today = new Date().toISOString().split('T')[0];
            const [depts, emps, shiftsList, assignments, companiesList] = await Promise.all([
                getDepartments(),
                getEmployees(0, EMPLOYEE_PAGE_SIZE),
                getShifts(),
                getAssignments(today, today),
                getCompanies()
            ]);
            setOriginalDepts(depts);
            setDepartments(sortDepartmentsTree(depts));
            setEmployees(emps);
            setShifts(shiftsList);
            setCompanies(companiesList);
            setDeptAssignments(assignments.filter(a => a.scope === 'DEPARTMENT'));
        } catch (error) {
            showError('No se pudieron cargar datos');
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
                <div className="flex-row gap-2" style={{ paddingLeft: `${dept.level * 20}px` }}>
                    {dept.level > 0 && <ChevronRight size={14} color="#aaa" />}
                    <Folder size={16} color="var(--primary)" />
                    <span className="font-medium">{dept.name}</span>
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
            field: 'company',
            header: 'Empresa',
            width: '180px',
            render: (dept) => (
                <span className="text-sm">
                    {dept.company_name || <span className="text-muted">Sin empresa</span>}
                </span>
            )
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
                    <span className="shift-badge">
                        {shiftName}
                    </span>
                ) : (
                    <span className="text-muted text-xs">Sin turno</span>
                );
            }
        },
        {
            field: 'actions',
            header: 'Acciones',
            align: 'right',
            width: '100px',
            render: (dept) => (
                <div className="flex-row gap-2 flex-end">
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
        <div className="w-full">
            <PageToolbar
                title="Departamentos"
                subtitle="Estructura organizativa de la empresa"
                onSearch={setSearchTerm}
                searchPlaceholder="Buscar por nombre o código..."
                actions={
                    <button className="primary flex-row gap-2" onClick={() => {
                        setEditingDept(null);
                        setIsModalOpen(true);
                    }}>
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
                    companies={companies}
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
                            showError('No se pudo asignar el turno');
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
    companies: Company[],
    shifts: Shift[],
    currentAssignment?: ShiftAssignment,
    onShiftAssign: (deptId: number, shiftId: number) => Promise<void>
}> = ({ department, onClose, onSave, departments, companies, shifts, currentAssignment, onShiftAssign }) => {
    const [name, setName] = useState(department?.name || '');
    const [code, setCode] = useState(department?.code || '');
    const [companyId, setCompanyId] = useState<number | undefined>(department?.company);
    const [parentId, setParentId] = useState<number | undefined>(department?.parent_id);
    const [selectedShiftId, setSelectedShiftId] = useState<number | undefined>(currentAssignment?.shift_id);
    const [saving, setSaving] = useState(false);

    return (
        <div className="modal-overlay">
            <div className="card modal-dialog">
                <h3>{department ? 'Editar Departamento' : 'Nuevo Departamento'}</h3>

                <div className="flex-col gap-4">
                    <div className="flex-col gap-2">
                        <label className="form-label">Nombre</label>
                        <input value={name} onChange={e => setName(e.target.value)} placeholder="Ej: Recursos Humanos" />
                    </div>

                    <div className="flex-col gap-2">
                        <label className="form-label">Código</label>
                        <input value={code} onChange={e => setCode(e.target.value)} placeholder="Ej: HR-001" />
                    </div>

                    <div className="flex-col gap-2">
                        <label className="form-label">Empresa</label>
                        <select
                            value={companyId || ''}
                            onChange={e => setCompanyId(e.target.value ? Number(e.target.value) : undefined)}
                        >
                            <option value="">-- Sin empresa --</option>
                            {companies.map(c => (
                                <option key={c.id} value={c.id}>{c.name}</option>
                            ))}
                        </select>
                    </div>

                    <div className="flex-col gap-2">
                        <label className="form-label">Departamento Superior</label>
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
                        <div className="flex-col gap-2 border-t pt-4">
                            <label className="form-label font-semibold">⏰ Turno Asignado</label>
                            <select
                                value={selectedShiftId || ''}
                                onChange={e => setSelectedShiftId(e.target.value ? Number(e.target.value) : undefined)}
                            >
                                <option value="">-- Sin turno --</option>
                                {shifts.map(s => (
                                    <option key={s.id} value={s.id}>{s.name}</option>
                                ))}
                            </select>
                            <small className="text-muted text-xxs">
                                Este turno se aplicará automáticamente a todos los empleados del departamento que no tengan una asignación individual.
                            </small>
                        </div>
                    )}

                    <div className="flex-row gap-2 mt-3 flex-end">
                        <button onClick={onClose} disabled={saving}>Cancelar</button>
                        <button className="primary" disabled={saving} onClick={async () => {
                            setSaving(true);
                            try {
                                await onSave({ id: department?.id, name, code, company: companyId, parent_id: parentId });
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
