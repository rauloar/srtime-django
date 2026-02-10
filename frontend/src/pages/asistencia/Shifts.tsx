
import React, { useEffect, useState } from 'react';
import { Plus, Calendar, Settings, Trash2 } from 'lucide-react';
import { getShifts, createShift, deleteShift, getTimetables, configureShiftCycle, getShiftCycle, type Shift, type Timetable } from '../../api';
import { DataGrid, type Column } from '../../components/ui/DataGrid';
import { PageToolbar } from '../../components/ui/PageToolbar';
import { ConfirmDialog } from '../../components/ui/ConfirmDialog';

export const Shifts: React.FC = () => {
    const [shifts, setShifts] = useState<Shift[]>([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isCycleModalOpen, setIsCycleModalOpen] = useState(false);
    const [selectedShift, setSelectedShift] = useState<Shift | null>(null);
    const [searchTerm, setSearchTerm] = useState('');

    // Confirm Dialog
    const [confirmOpen, setConfirmOpen] = useState(false);
    const [shiftToDelete, setShiftToDelete] = useState<number | null>(null);

    const fetchData = async () => {
        setLoading(true);
        try {
            const data = await getShifts();
            setShifts(data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleCreate = async (name: string) => {
        try {
            await createShift({ name });
            setIsModalOpen(false);
            fetchData();
        } catch (error) {
            alert('Error creating shift');
        }
    };

    const confirmDelete = (id: number) => {
        setShiftToDelete(id);
        setConfirmOpen(true);
    };

    const executeDelete = async () => {
        if (!shiftToDelete) return;
        try {
            await deleteShift(shiftToDelete);
            setConfirmOpen(false);
            fetchData();
        } catch (error) {
            alert('Error deleting shift');
        }
    };

    const openCycleConfig = (shift: Shift) => {
        setSelectedShift(shift);
        setIsCycleModalOpen(true);
    };

    const filteredShifts = shifts.filter(s =>
        s.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const columns: Column<Shift>[] = [
        {
            field: 'name',
            header: 'Nombre del Turno',
            render: (shift) => (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Calendar size={16} color="var(--primary)" />
                    <span style={{ fontWeight: 500 }}>{shift.name}</span>
                </div>
            )
        },
        {
            field: 'actions',
            header: 'Acciones',
            align: 'right',
            width: '100px',
            render: (shift) => (
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '5px' }}>
                    <button
                        className="icon-btn"
                        title="Configurar Ciclo"
                        onClick={(e) => { e.stopPropagation(); openCycleConfig(shift); }}
                    >
                        <Settings size={18} />
                    </button>
                    <button
                        className="icon-btn danger"
                        title="Eliminar"
                        onClick={(e) => { e.stopPropagation(); shift.id && confirmDelete(shift.id); }}
                    >
                        <Trash2 size={18} />
                    </button>
                </div>
            )
        }
    ];

    return (
        <div style={{ width: '100%' }}>
            <PageToolbar
                title="Turnos"
                subtitle="Agrupación de horarios por ciclos"
                onSearch={setSearchTerm}
                searchPlaceholder="Buscar turno..."
                actions={
                    <button className="primary flex-row gap-2" onClick={() => setIsModalOpen(true)}>
                        <Plus size={16} /> Agregar
                    </button>
                }
            />

            <div className="page-card">
                <DataGrid
                    columns={columns}
                    data={filteredShifts}
                    loading={loading}
                    placeholder="No hay turnos definidos"
                />
            </div>

            {isModalOpen && (
                <ShiftModal
                    onClose={() => setIsModalOpen(false)}
                    onSave={handleCreate}
                />
            )}

            {isCycleModalOpen && selectedShift && (
                <CycleModal
                    shift={selectedShift}
                    onClose={() => setIsCycleModalOpen(false)}
                />
            )}

            <ConfirmDialog
                isOpen={confirmOpen}
                title="Eliminar Turno"
                message="¿Eliminar este turno? Eliminará también el ciclo configurado."
                onConfirm={executeDelete}
                onCancel={() => setConfirmOpen(false)}
                type="danger"
            />
        </div>
    );
};

const ShiftModal: React.FC<{
    onClose: () => void,
    onSave: (name: string) => void
}> = ({ onClose, onSave }) => {
    const [name, setName] = useState('');

    return (
        <div className="modal-desktop">
            <div className="card modal-content-desktop" style={{ maxWidth: '500px' }}>
                <h3>Nuevo Turno</h3>
                <div className="flex-col gap-4">
                    <div className="flex-col gap-2">
                        <label className="text-muted" style={{ fontSize: '12px' }}>Nombre del Turno</label>
                        <input value={name} onChange={e => setName(e.target.value)} placeholder="Ej: General de Lunes a Viernes" autoFocus />
                    </div>

                    <div className="flex-row gap-2" style={{ marginTop: '20px', justifyContent: 'flex-end' }}>
                        <button onClick={onClose}>Cancelar</button>
                        <button className="primary" onClick={() => onSave(name)}>Guardar</button>
                    </div>
                </div>
            </div>
        </div>
    );
};

const CycleModal: React.FC<{
    shift: Shift,
    onClose: () => void
}> = ({ shift, onClose }) => {
    const [timetables, setTimetables] = useState<Timetable[]>([]);
    // 0=Mon, 6=Sun. We'll store timetable_id for each index.
    const [cycle, setCycle] = useState<(number | "")[]>(Array(7).fill(""));
    const [loading, setLoading] = useState(true);

    const days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];

    useEffect(() => {
        const load = async () => {
            try {
                const [tts, existingCycle] = await Promise.all([
                    getTimetables(),
                    getShiftCycle(shift.id!)
                ]);
                setTimetables(tts);

                // Map existing cycle
                const newCycle = Array(7).fill("");
                existingCycle.forEach(item => {
                    if (item.day_index >= 0 && item.day_index < 7) {
                        newCycle[item.day_index] = item.timetable_id;
                    }
                });
                setCycle(newCycle);

            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [shift.id]);

    const handleSave = async () => {
        const items = cycle.map((tid, idx) => {
            if (tid !== "") return { timetable_id: tid as number, day_index: idx };
            return null;
        }).filter(x => x !== null) as { timetable_id: number; day_index: number }[];

        try {
            await configureShiftCycle(shift.id!, items);
            onClose();
        } catch (e) {
            alert("Error saving cycle");
        }
    };

    const handleApplyAll = () => {
        if (cycle[0] !== "") {
            setCycle(Array(7).fill(cycle[0]));
        }
    };

    const handleApplyWorkWeek = () => {
        if (cycle[0] !== "") {
            const newCycle = [...cycle];
            for (let i = 0; i < 5; i++) newCycle[i] = cycle[0];
            setCycle(newCycle);
        }
    };

    return (
        <div className="modal-desktop">
            <div className="card modal-content-desktop" style={{ maxWidth: '600px' }}>
                <h3>Configurar Ciclo: {shift.name}</h3>

                {loading ? <p>Cargando...</p> : (
                    <div className="flex-col gap-4">
                        <div className="flex-row gap-2" style={{ marginBottom: '10px' }}>
                            <button className="secondary small" onClick={handleApplyAll}>Aplicar Lunes a Todos</button>
                            <button className="secondary small" onClick={handleApplyWorkWeek}>Aplicar Lunes a Vie</button>
                        </div>

                        <div className="modal-days-grid">
                            {days.map((day, idx) => (
                                <React.Fragment key={idx}>
                                    <label style={{ fontWeight: 500 }}>{day}</label>
                                    <select
                                        value={cycle[idx]}
                                        onChange={e => {
                                            const val = e.target.value ? parseInt(e.target.value) : "";
                                            const newCycle = [...cycle];
                                            newCycle[idx] = val;
                                            setCycle(newCycle);
                                        }}
                                        className="form-control"
                                    >
                                        <option value="">- Descanso -</option>
                                        {timetables.map(t => {
                                            const timeDisplay = t.is_flexible 
                                                ? `(Flexible - ${t.required_minutes}min)` 
                                                : `(${t.on_duty_time} - ${t.off_duty_time})`;
                                            return (
                                                <option key={t.id} value={t.id}>{t.name} {timeDisplay}</option>
                                            );
                                        })}
                                    </select>
                                </React.Fragment>
                            ))}
                        </div>

                        <div className="flex-row gap-2" style={{ marginTop: '20px', justifyContent: 'flex-end' }}>
                            <button onClick={onClose}>Cancelar</button>
                            <button className="primary" onClick={handleSave}>Guardar Ciclo</button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
