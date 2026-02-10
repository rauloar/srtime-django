import React, { useEffect, useState } from 'react';
import { Plus, Edit2, Trash2, Download } from 'lucide-react';
import { getEmployees, createEmployee, updateEmployee, deleteEmployee, getDepartments, type Employee } from '../../api';
import { sortDepartmentsTree, type DepartmentNode } from '../../utils/treeUtils';
import * as XLSX from 'xlsx';
import { DataGrid, type Column } from '../../components/ui/DataGrid';
import { PageToolbar } from '../../components/ui/PageToolbar';
import { ConfirmDialog } from '../../components/ui/ConfirmDialog';

export const Employees: React.FC = () => {
    const [employees, setEmployees] = useState<Employee[]>([]);
    const [departments, setDepartments] = useState<DepartmentNode[]>([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingEmp, setEditingEmp] = useState<Employee | null>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedDepartment, setSelectedDepartment] = useState<number | null>(null);
    // const fileInputRef = useRef<HTMLInputElement>(null);  // Removed: import functionality disabled

    // Confirm Dialog
    const [confirmOpen, setConfirmOpen] = useState(false);
    const [empToDelete, setEmpToDelete] = useState<number | null>(null);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [empData, deptData] = await Promise.all([getEmployees(0, 2000), getDepartments()]);
            setEmployees(empData);
            setDepartments(sortDepartmentsTree(deptData));
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleSave = async (emp: Employee) => {
        try {
            if (emp.id) await updateEmployee(emp.id, emp);
            else await createEmployee(emp);
            setIsModalOpen(false);
            fetchData();
        } catch (error: any) {
            alert('Error saving employee: ' + (error.response?.data?.detail || error.message));
        }
    };

    const confirmDelete = (id: number) => {
        setEmpToDelete(id);
        setConfirmOpen(true);
    };

    const executeDelete = async () => {
        if (!empToDelete) return;
        try {
            await deleteEmployee(empToDelete);
            setConfirmOpen(false);
            fetchData();
        } catch (error) {
            alert('Error deleting employee');
        }
    };

    const getExportData = () => {
        const headers = [
            "ID", "Nombre", "Departamento", "Tarjeta", "Privilegio",
            "Email", "Teléfono", "Celular", "Dirección", "Ciudad", "País",
            "DNI", "Fecha Nacimiento", "Género"
        ];

        const rows = employees.map(e => [
            e.user_id,
            e.name || "",
            e.department_name || getDeptName(e.department_id),
            e.card || "",
            e.privilege === 14 ? "Admin" : "User",
            e.email || "",
            e.phone || "",
            e.mobile_phone || "",
            e.address || "",
            e.city || "",
            e.country || "",
            e.ssn || "",
            e.birthday || "",
            e.gender || ""
        ]);

        return { headers, rows };
    };

    const handleExportCSV = () => {
        const { headers, rows } = getExportData();
        const csvContent = "data:text/csv;charset=utf-8,"
            + headers.join(",") + "\n"
            + rows.map(e => e.join(",")).join("\n");

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "empleados.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const handleExportExcel = () => {
        const { headers, rows } = getExportData();
        const worksheet = XLSX.utils.aoa_to_sheet([headers, ...rows]);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, "Empleados");
        XLSX.writeFile(workbook, "empleados.xlsx");
    };

    // Import functionality disabled in DEV mode

    const getDeptName = (id?: number) => {
        const d = departments.find(d => d.id === id);
        return d ? d.name : '-';
    };

    // Filter employees by search term and department
    const filteredEmployees = employees.filter(e => {
        const matchesSearch = e.user_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
            (e.name && e.name.toLowerCase().includes(searchTerm.toLowerCase()));
        
        const matchesDepartment = selectedDepartment === null || e.department_id === selectedDepartment;
        
        return matchesSearch && matchesDepartment;
    });

    const columns: Column<Employee>[] = [
        {
            field: 'user_id',
            header: 'ID Usuario',
            width: '100px',
            render: (emp) => <span style={{ fontWeight: 500 }}>{emp.user_id}</span>
        },
        {
            field: 'name',
            header: 'Nombre',
            render: (emp) => emp.name || '-'
        },
        {
            field: 'department_name',
            header: 'Departamento',
            render: (emp) => emp.department_name || '-'
        },
        {
            field: 'actions',
            header: 'Acciones',
            align: 'right',
            width: '80px',
            render: (emp) => (
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '5px' }}>
                    <button
                        className="icon-btn"
                        onClick={(e) => { e.stopPropagation(); setEditingEmp(emp); setIsModalOpen(true); }}
                        title="Editar"
                    >
                        <Edit2 size={16} />
                    </button>
                    <button
                        className="icon-btn danger"
                        onClick={(e) => { e.stopPropagation(); emp.id && confirmDelete(emp.id); }}
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
                title="Empleados"
                subtitle="Gestión de personal y accesos"
                onSearch={setSearchTerm}
                searchPlaceholder="Buscar por ID o Nombre..."
                actions={
                    <>
                        <select
                            value={selectedDepartment ?? ''}
                            onChange={(e) => setSelectedDepartment(e.target.value ? parseInt(e.target.value) : null)}
                            className="form-control"
                            style={{ minWidth: '200px', height: '36px' }}
                        >
                            <option value="">Todos los Departamentos</option>
                            {departments.map(d => (
                                <option key={d.id} value={d.id}>{d.name}</option>
                            ))}
                        </select>
                        <button className="secondary flex-row gap-2" onClick={handleExportCSV}>
                            <Download size={16} /> CSV
                        </button>
                        <button className="secondary flex-row gap-2" onClick={handleExportExcel}>
                            <Download size={16} /> Excel
                        </button>
                        <button className="primary flex-row gap-2" onClick={() => { setEditingEmp(null); setIsModalOpen(true); }}>
                            <Plus size={16} /> Nuevo
                        </button>
                    </>
                }
            />

            <div className="page-card">
                <DataGrid
                    columns={columns}
                    data={filteredEmployees}
                    loading={loading}
                    placeholder="No hay empleados registrados"
                />
            </div>

            {isModalOpen && (
                <EmployeeModal
                    employee={editingEmp}
                    departments={departments}
                    onClose={() => setIsModalOpen(false)}
                    onSave={handleSave}
                />
            )}

            <ConfirmDialog
                isOpen={confirmOpen}
                title="Eliminar Empleado"
                message="¿Está seguro de que desea eliminar este empleado?"
                onConfirm={executeDelete}
                onCancel={() => setConfirmOpen(false)}
                type="danger"
            />
        </div>
    );
};

const EmployeeModal: React.FC<{
    employee: Employee | null,
    departments: DepartmentNode[],
    onClose: () => void,
    onSave: (e: Employee) => void
}> = ({ employee, departments, onClose, onSave }) => {
    const [activeTab, setActiveTab] = useState<'basic' | 'contact' | 'personal'>('basic');

    // Datos Básicos
    const [userId, setUserId] = useState(employee?.user_id || '');
    const [name, setName] = useState(employee?.name || '');
    const [card, setCard] = useState(employee?.card || '');
    const [deptId, setDeptId] = useState<number | undefined>(employee?.department_id);
    const [privilege, setPrivilege] = useState(employee?.privilege || 0);

    // Datos de Contacto
    const [email, setEmail] = useState(employee?.email || '');
    const [phone, setPhone] = useState(employee?.phone || '');
    const [mobilePhone, setMobilePhone] = useState(employee?.mobile_phone || '');
    const [address, setAddress] = useState(employee?.address || '');
    const [city, setCity] = useState(employee?.city || '');
    const [country, setCountry] = useState(employee?.country || '');

    // Datos Personales
    const [gender, setGender] = useState(employee?.gender || '');
    const [birthday, setBirthday] = useState(employee?.birthday || '');
    const [ssn, setSsn] = useState(employee?.ssn || '');

    const handleSaveClick = () => {
        onSave({
            ...employee,
            user_id: userId,
            name,
            card,
            department_id: deptId,
            privilege,
            email,
            phone,
            mobile_phone: mobilePhone,
            address,
            city,
            country,
            gender,
            birthday: birthday || undefined,
            ssn
        });
    };

    return (
        <div className="modal-desktop">
            <div className="card modal-content-desktop" style={{ maxWidth: '700px' }}>
                <h3>{employee ? 'Editar Empleado' : 'Nuevo Empleado'}</h3>

                {/* Tabs */}
                <div style={{ display: 'flex', gap: '10px', borderBottom: '1px solid var(--border)', marginBottom: '20px' }}>
                    <button
                        onClick={() => setActiveTab('basic')}
                        style={{
                            padding: '10px 20px',
                            background: 'transparent',
                            border: 'none',
                            borderBottom: activeTab === 'basic' ? '2px solid var(--primary)' : '2px solid transparent',
                            color: activeTab === 'basic' ? 'var(--primary)' : 'var(--text-secondary)',
                            cursor: 'pointer',
                            fontWeight: activeTab === 'basic' ? 600 : 400
                        }}
                    >
                        Datos Básicos
                    </button>
                    <button
                        onClick={() => setActiveTab('contact')}
                        style={{
                            padding: '10px 20px',
                            background: 'transparent',
                            border: 'none',
                            borderBottom: activeTab === 'contact' ? '2px solid var(--primary)' : '2px solid transparent',
                            color: activeTab === 'contact' ? 'var(--primary)' : 'var(--text-secondary)',
                            cursor: 'pointer',
                            fontWeight: activeTab === 'contact' ? 600 : 400
                        }}
                    >
                        Datos de Contacto
                    </button>
                    <button
                        onClick={() => setActiveTab('personal')}
                        style={{
                            padding: '10px 20px',
                            background: 'transparent',
                            border: 'none',
                            borderBottom: activeTab === 'personal' ? '2px solid var(--primary)' : '2px solid transparent',
                            color: activeTab === 'personal' ? 'var(--primary)' : 'var(--text-secondary)',
                            cursor: 'pointer',
                            fontWeight: activeTab === 'personal' ? 600 : 400
                        }}
                    >
                        Datos Personales
                    </button>
                </div>

                {/* Tab Content: Datos Básicos */}
                {activeTab === 'basic' && (
                    <div className="modal-form-grid">
                        <div className="flex-col gap-2">
                            <label className="text-muted" style={{ fontSize: '12px' }}>ID Usuario (Requerido)</label>
                            <input value={userId} onChange={e => setUserId(e.target.value)} disabled={!!employee} placeholder="Ej: 1001" />
                        </div>

                        <div className="flex-col gap-2">
                            <label className="text-muted" style={{ fontSize: '12px' }}>Nombre</label>
                            <input value={name} onChange={e => setName(e.target.value)} placeholder="Ej: Juan Perez" />
                        </div>

                        <div className="flex-col gap-2">
                            <label className="text-muted" style={{ fontSize: '12px' }}>Departamento</label>
                            <select value={deptId || ''} onChange={e => setDeptId(e.target.value ? Number(e.target.value) : undefined)}>
                                <option value="">-- Seleccionar --</option>
                                {departments.map(d => (
                                    <option key={d.id} value={d.id}>
                                        {'\u00A0\u00A0'.repeat(d.level) + d.name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className="flex-col gap-2">
                            <label className="text-muted" style={{ fontSize: '12px' }}>Número Tarjeta</label>
                            <input value={card} onChange={e => setCard(e.target.value)} placeholder="" />
                        </div>

                        <div className="flex-col gap-2">
                            <label className="text-muted" style={{ fontSize: '12px' }}>Privilegio</label>
                            <select value={privilege} onChange={e => setPrivilege(Number(e.target.value))}>
                                <option value={0}>Usuario Normal</option>
                                <option value={14}>Administrador</option>
                            </select>
                        </div>
                    </div>
                )}

                {/* Tab Content: Datos de Contacto */}
                {activeTab === 'contact' && (
                    <div className="modal-form-grid">
                        <div className="flex-col gap-2">
                            <label className="text-muted" style={{ fontSize: '12px' }}>Email</label>
                            <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="ejemplo@correo.com" />
                        </div>

                        <div className="flex-col gap-2">
                            <label className="text-muted" style={{ fontSize: '12px' }}>Teléfono</label>
                            <input value={phone} onChange={e => setPhone(e.target.value)} placeholder="+507 123-4567" />
                        </div>

                        <div className="flex-col gap-2">
                            <label className="text-muted" style={{ fontSize: '12px' }}>Teléfono Celular</label>
                            <input value={mobilePhone} onChange={e => setMobilePhone(e.target.value)} placeholder="+507 6000-0000" />
                        </div>

                        <div className="flex-col gap-2" style={{ gridColumn: '1 / -1' }}>
                            <label className="text-muted" style={{ fontSize: '12px' }}>Dirección</label>
                            <input value={address} onChange={e => setAddress(e.target.value)} placeholder="Calle, Avenida, etc." />
                        </div>

                        <div className="flex-col gap-2">
                            <label className="text-muted" style={{ fontSize: '12px' }}>Ciudad</label>
                            <input value={city} onChange={e => setCity(e.target.value)} placeholder="Ciudad" />
                        </div>

                        <div className="flex-col gap-2">
                            <label className="text-muted" style={{ fontSize: '12px' }}>País</label>
                            <input value={country} onChange={e => setCountry(e.target.value)} placeholder="País" />
                        </div>
                    </div>
                )}

                {/* Tab Content: Datos Personales */}
                {activeTab === 'personal' && (
                    <div className="modal-form-grid">
                        <div className="flex-col gap-2">
                            <label className="text-muted" style={{ fontSize: '12px' }}>DNI / Documento</label>
                            <input value={ssn} onChange={e => setSsn(e.target.value)} placeholder="8-123-456" />
                        </div>

                        <div className="flex-col gap-2">
                            <label className="text-muted" style={{ fontSize: '12px' }}>Fecha de Nacimiento</label>
                            <input type="date" value={birthday} onChange={e => setBirthday(e.target.value)} />
                        </div>

                        <div className="flex-col gap-2">
                            <label className="text-muted" style={{ fontSize: '12px' }}>Género</label>
                            <select value={gender} onChange={e => setGender(e.target.value)}>
                                <option value="">-- Seleccionar --</option>
                                <option value="M">Masculino</option>
                                <option value="F">Femenino</option>
                            </select>
                        </div>
                    </div>
                )}

                <div className="flex-row gap-2" style={{ marginTop: '20px', justifyContent: 'flex-end' }}>
                    <button onClick={onClose}>Cancelar</button>
                    <button className="primary" onClick={handleSaveClick}>Guardar</button>
                </div>
            </div>
        </div>
    );
};
