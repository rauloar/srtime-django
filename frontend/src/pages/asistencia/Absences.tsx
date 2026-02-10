import React, { useEffect, useState } from 'react';
import { Plus, Trash2, CalendarOff } from 'lucide-react';
import { getAbsences, createAbsence, deleteAbsence, getEmployees, type Absence, type Employee } from '../../api';
import { DataGrid, type Column } from '../../components/ui/DataGrid';
import { PageToolbar } from '../../components/ui/PageToolbar';
import { ConfirmDialog } from '../../components/ui/ConfirmDialog';

export const Absences: React.FC = () => {
    const [absences, setAbsences] = useState<Absence[]>([]);
    const [employees, setEmployees] = useState<Employee[]>([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');

    // Confirm Dialog
    const [confirmOpen, setConfirmOpen] = useState(false);
    const [absToDelete, setAbsToDelete] = useState<number | null>(null);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [absData, empData] = await Promise.all([
                getAbsences(),
                getEmployees(0, 1000)
            ]);
            setAbsences(absData);
            setEmployees(empData);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const confirmDelete = (id: number) => {
        setAbsToDelete(id);
        setConfirmOpen(true);
    };

    const executeDelete = async () => {
        if (!absToDelete) return;
        try {
            await deleteAbsence(absToDelete);
            setConfirmOpen(false);
            fetchData();
        } catch (error) {
            alert('Error deleting absence');
        }
    };

    const handleCreate = async (abs: Absence) => {
        try {
            await createAbsence(abs);
            setIsModalOpen(false);
            fetchData();
        } catch (error) {
            alert('Error creating absence (Endpoint might not exist)');
        }
    };

    const getEmployeeName = (id: number) => {
        const emp = employees.find(e => e.id === id);
        return emp?.name || String(id);
    };

    const filteredAbsences = absences.filter(a =>
        a.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (a.employee_name && a.employee_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (a.employee_user_id && a.employee_user_id.toLowerCase().includes(searchTerm.toLowerCase())) ||
        getEmployeeName(a.employee_id).toLowerCase().includes(searchTerm.toLowerCase())
    );

    const columns: Column<Absence>[] = [
        {
            field: 'employee_id',
            header: 'Empleado',
            render: (a) => (
                <div>
                    <div style={{ fontWeight: 600, fontSize: '14px' }}>{a.employee_user_id || getEmployeeName(a.employee_id)}</div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{a.employee_name || getEmployeeName(a.employee_id)}</div>
                </div>
            )
        },
        {
            field: 'source',
            header: 'Origen',
            render: (a) => (
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    {a.source === 'Detected' ? (
                        <span style={{ 
                            padding: '2px 8px', 
                            borderRadius: '4px', 
                            backgroundColor: 'var(--status-warning-bg)', 
                            color: 'var(--status-warning)',
                            fontSize: '11px',
                            fontWeight: 600
                        }}>AUTO</span>
                    ) : (
                        <span style={{ 
                            padding: '2px 8px', 
                            borderRadius: '4px', 
                            backgroundColor: 'var(--status-info-bg)', 
                            color: 'var(--status-info)',
                            fontSize: '11px',
                            fontWeight: 600
                        }}>MANUAL</span>
                    )}
                </div>
            )
        },
        {
            field: 'type',
            header: 'Tipo',
            render: (a) => (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CalendarOff size={16} color="var(--status-error)" />
                    <span>{a.type}</span>
                </div>
            )
        },
        {
            field: 'start_date',
            header: 'Desde',
            render: (a) => a.start_date
        },
        {
            field: 'end_date',
            header: 'Hasta',
            render: (a) => a.end_date
        },
        {
            field: 'reason',
            header: 'Motivo',
            render: (a) => a.reason || '-'
        },
        {
            field: 'actions',
            header: 'Acciones',
            align: 'right',
            width: '80px',
            render: (a) => (
                a.source !== 'Detected' ? (
                    <button
                        className="icon-btn danger"
                        onClick={(e) => { e.stopPropagation(); a.id && confirmDelete(Number(a.id)); }}
                        title="Eliminar"
                    >
                        <Trash2 size={16} />
                    </button>
                ) : (
                    <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Auto</span>
                )
            )
        }
    ];

    return (
        <div style={{ width: '100%' }}>
            <PageToolbar
                title="Ausencias"
                subtitle="Registro de vacaciones, licencias y permisos"
                onSearch={setSearchTerm}
                searchPlaceholder="Buscar por empleado o tipo..."
                actions={
                    <button className="primary flex-row gap-2" onClick={() => setIsModalOpen(true)}>
                        <Plus size={16} /> Agregar
                    </button>
                }
            />

            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                <DataGrid
                    columns={columns}
                    data={filteredAbsences}
                    loading={loading}
                    placeholder="No hay ausencias registradas"
                />
            </div>

            {isModalOpen && (
                <AbsenceModal
                    employees={employees}
                    onClose={() => setIsModalOpen(false)}
                    onSave={handleCreate}
                />
            )}

            <ConfirmDialog
                isOpen={confirmOpen}
                title="Eliminar Ausencia"
                message="¿Está seguro de que desea eliminar este registro?"
                onConfirm={executeDelete}
                onCancel={() => setConfirmOpen(false)}
                type="danger"
            />
        </div>
    );
};

const AbsenceModal: React.FC<{
    employees: Employee[],
    onClose: () => void,
    onSave: (abs: Absence) => void
}> = ({ employees, onClose, onSave }) => {
    const [empId, setEmpId] = useState<number | ''>('');
    const [type, setType] = useState('Vacaciones');
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [reason, setReason] = useState('');

    return (
        <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: 'var(--modal-overlay)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
        }}>
            <div className="card" style={{ width: '500px', padding: '20px' }}>
                <h3>Registrar Ausencia</h3>

                <div className="flex-col gap-4">
                    <div className="flex-col gap-2">
                        <label className="text-muted" style={{ fontSize: '12px' }}>Empleado</label>
                        <select className="form-control" value={empId} onChange={e => setEmpId(Number(e.target.value))}>
                            <option value="">-- Seleccionar --</option>
                            {employees.map(e => (
                                <option key={e.id} value={e.id}>{e.name} ({e.user_id})</option>
                            ))}
                        </select>
                    </div>

                    <div className="flex-col gap-2">
                        <label className="text-muted" style={{ fontSize: '12px' }}>Tipo</label>
                        <select className="form-control" value={type} onChange={e => setType(e.target.value)}>
                            <option value="Vacaciones">Vacaciones</option>
                            <option value="Enfermedad">Enfermedad</option>
                            <option value="Permiso Personal">Permiso Personal</option>
                            <option value="Otro">Otro</option>
                        </select>
                    </div>

                    <div className="flex-row gap-4">
                        <div className="flex-col gap-2" style={{ flex: 1 }}>
                            <label className="text-muted" style={{ fontSize: '12px' }}>Desde</label>
                            <input type="date" className="form-control" value={startDate} onChange={e => setStartDate(e.target.value)} />
                        </div>
                        <div className="flex-col gap-2" style={{ flex: 1 }}>
                            <label className="text-muted" style={{ fontSize: '12px' }}>Hasta</label>
                            <input type="date" className="form-control" value={endDate} onChange={e => setEndDate(e.target.value)} />
                        </div>
                    </div>

                    <div className="flex-col gap-2">
                        <label className="text-muted" style={{ fontSize: '12px' }}>Motivo / Detalles</label>
                        <textarea className="form-control" rows={3} value={reason} onChange={e => setReason(e.target.value)} />
                    </div>

                    <div className="flex-row gap-2" style={{ marginTop: '20px', justifyContent: 'flex-end' }}>
                        <button onClick={onClose} className="secondary">Cancelar</button>
                        <button
                            className="primary"
                            disabled={!empId || !startDate || !endDate}
                            onClick={() => onSave({
                                employee_id: Number(empId),
                                type,
                                start_date: startDate,
                                end_date: endDate,
                                reason
                            })}
                        >
                            Guardar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};
