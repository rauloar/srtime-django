import React, { useEffect, useState } from 'react';
import { Folder, Plus, Edit2, Trash2 } from 'lucide-react';
import { getDepartments, createDepartment, updateDepartment, deleteDepartment, getEmployees, type Department, type Employee } from '../../api';
import { DataGrid, type Column } from '../../components/ui/DataGrid';
import { PageToolbar } from '../../components/ui/PageToolbar';
import { ConfirmDialog } from '../../components/ui/ConfirmDialog';

export const Departments: React.FC = () => {
    const [departments, setDepartments] = useState<Department[]>([]);
    const [employees, setEmployees] = useState<Employee[]>([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingDept, setEditingDept] = useState<Department | null>(null);
    const [searchTerm, setSearchTerm] = useState('');

    // Confirm Dialog State
    const [confirmOpen, setConfirmOpen] = useState(false);
    const [deptToDelete, setDeptToDelete] = useState<number | null>(null);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [depts, emps] = await Promise.all([
                getDepartments(),
                getEmployees(0, 1000) // Fetch strict list for validation
            ]);
            setDepartments(depts);
            setEmployees(emps);
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
        const d = departments.find(d => d.id === id);
        return d ? d.name : id;
    };

    const filteredDepartments = departments.filter(d =>
        d.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (d.code && d.code.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    const columns: Column<Department>[] = [
        {
            field: 'name',
            header: 'Nombre Departamento',
            render: (dept) => (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
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
                    <button className="primary flex-row gap-2" onClick={() => { setEditingDept(null); setIsModalOpen(true); }}>
                        <Plus size={16} /> Nuevo Departamento
                    </button>
                }
            />

            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
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
    department: Department | null,
    onClose: () => void,
    onSave: (d: Department) => void,
    departments: Department[]
}> = ({ department, onClose, onSave, departments }) => {
    const [name, setName] = useState(department?.name || '');
    const [code, setCode] = useState(department?.code || '');
    const [parentId, setParentId] = useState<number | undefined>(department?.parent_id);

    return (
        <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
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
                                <option key={d.id} value={d.id}>{d.name}</option>
                            ))}
                        </select>
                    </div>

                    <div className="flex-row gap-2" style={{ marginTop: '10px', justifyContent: 'flex-end' }}>
                        <button onClick={onClose}>Cancelar</button>
                        <button className="primary" onClick={() => onSave({ ...department, name, code, parent_id: parentId })}>Guardar</button>
                    </div>
                </div>
            </div>
        </div>
    );
};
