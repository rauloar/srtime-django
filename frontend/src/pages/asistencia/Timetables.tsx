
import React, { useEffect, useState } from 'react';
import { Plus, Trash2, Clock, Settings } from 'lucide-react';
import { getTimetables, createTimetable, deleteTimetable, updateTimetable, type Timetable } from '../../api';
import { DataGrid, type Column } from '../../components/ui/DataGrid';
import { PageToolbar } from '../../components/ui/PageToolbar';
import { ConfirmDialog } from '../../components/ui/ConfirmDialog';

export const Timetables: React.FC = () => {
    const [timetables, setTimetables] = useState<Timetable[]>([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingTimetable, setEditingTimetable] = useState<Timetable | null>(null);
    const [searchTerm, setSearchTerm] = useState('');

    // Confirm Dialog
    const [confirmOpen, setConfirmOpen] = useState(false);
    const [ttToDelete, setTtToDelete] = useState<number | null>(null);

    const fetchData = async () => {
        setLoading(true);
        try {
            const data = await getTimetables();
            setTimetables(data);
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
        setTtToDelete(id);
        setConfirmOpen(true);
    };

    const executeDelete = async () => {
        if (!ttToDelete) return;
        try {
            await deleteTimetable(ttToDelete);
            setConfirmOpen(false);
            fetchData();
        } catch (error) {
            alert('Error deleting timetable');
        }
    };

    const handleCreate = async (tt: Timetable) => {
        try {
            await createTimetable(tt);
            setIsModalOpen(false);
            fetchData();
        } catch (error) {
            alert('Error creating timetable');
        }
    };

    const handleUpdate = async (tt: Timetable) => {
        if (!editingTimetable?.id) return;
        try {
            await updateTimetable(editingTimetable.id, tt);
            setIsModalOpen(false);
            setEditingTimetable(null);
            fetchData();
        } catch (error) {
            alert('Error updating timetable');
        }
    };

    const filteredTimetables = timetables.filter(t =>
        t.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const columns: Column<Timetable>[] = [
        {
            field: 'name',
            header: 'Nombre',
            render: (tt) => (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Clock size={16} color="var(--primary)" />
                    <span style={{ fontWeight: 500 }}>{tt.name}</span>
                </div>
            )
        },
        {
            field: 'on_duty_time',
            header: 'Entrada',
            width: '100px',
            align: 'center',
            render: (tt) => <span style={{ fontFamily: 'monospace' }}>{tt.is_flexible ? '-' : tt.on_duty_time}</span>
        },
        {
            field: 'off_duty_time',
            header: 'Salida',
            width: '100px',
            align: 'center',
            render: (tt) => <span style={{ fontFamily: 'monospace' }}>{tt.is_flexible ? '-' : tt.off_duty_time}</span>
        },
        {
            field: 'late_allow_minutes',
            header: 'Tol. Tardía (min)',
            width: '120px',
            align: 'center',
            render: (tt) => tt.is_flexible ? '-' : (tt.late_allow_minutes || 0)
        },
        {
            field: 'early_leave_allow_minutes',
            header: 'Tol. Temprana (min)',
            width: '140px',
            align: 'center',
            render: (tt) => tt.is_flexible ? '-' : (tt.early_leave_allow_minutes || 0)
        },
        {
            field: 'actions',
            header: 'Acciones',
            align: 'right',
            width: '120px',
            render: (tt) => (
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '6px' }}>
                    <button
                        className="icon-btn"
                        onClick={(e) => { e.stopPropagation(); setEditingTimetable(tt); setIsModalOpen(true); }}
                        title="Editar"
                    >
                        <Settings size={16} />
                    </button>
                    <button
                        className="icon-btn danger"
                        onClick={(e) => { e.stopPropagation(); tt.id && confirmDelete(tt.id); }}
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
                title="Horarios"
                subtitle="Definición de horarios de entrada y salida"
                onSearch={setSearchTerm}
                searchPlaceholder="Buscar horario..."
                actions={
                    <button className="primary flex-row gap-2" onClick={() => { setEditingTimetable(null); setIsModalOpen(true); }} disabled>
                        <Plus size={16} /> Agregar
                    </button>
                }
            />

            <div className="page-card">
                <DataGrid
                    columns={columns}
                    data={filteredTimetables}
                    loading={loading}
                    placeholder="No hay horarios definidos"
                />
            </div>

            {isModalOpen && (
                <TimetableModal
                    onClose={() => { setIsModalOpen(false); setEditingTimetable(null); }}
                    onSave={editingTimetable ? handleUpdate : handleCreate}
                    initialValue={editingTimetable || undefined}
                />
            )}

            <ConfirmDialog
                isOpen={confirmOpen}
                title="Eliminar Horario"
                message="¿Eliminar este horario? Afectará a los turnos que lo utilicen."
                onConfirm={executeDelete}
                onCancel={() => setConfirmOpen(false)}
                type="danger"
            />
        </div>
    );
};

const TimetableModal: React.FC<{
    onClose: () => void,
    onSave: (tt: Timetable) => void,
    initialValue?: Timetable
}> = ({ onClose, onSave, initialValue }) => {
    const [name, setName] = useState(initialValue?.name || '');
    const [onDuty, setOnDuty] = useState(initialValue?.on_duty_time || '09:00');
    const [offDuty, setOffDuty] = useState(initialValue?.off_duty_time || '18:00');
    const [lateAllow, setLateAllow] = useState(initialValue?.late_allow_minutes || 0);
    const [earlyAllow, setEarlyAllow] = useState(initialValue?.early_leave_allow_minutes || 0);

    // Windows
    const [checkInStart, setCheckInStart] = useState(initialValue?.check_in_start || '');
    const [checkInEnd, setCheckInEnd] = useState(initialValue?.check_in_end || '');
    const [checkOutStart, setCheckOutStart] = useState(initialValue?.check_out_start || '');
    const [checkOutEnd, setCheckOutEnd] = useState(initialValue?.check_out_end || '');

    const [breakMin, setBreakMin] = useState(initialValue?.break_minutes ?? 60);
    const [rounding, setRounding] = useState(initialValue?.rounding_rule || 'none');
    const [isFlexible, setIsFlexible] = useState(initialValue?.is_flexible || false);
    const [reqMin, setReqMin] = useState(initialValue?.required_minutes ?? 480);

    return (
        <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: 'var(--modal-overlay)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
        }}>
            <div className="card" style={{ width: '500px', padding: '20px', maxHeight: '90vh', overflowY: 'auto' }}>
                <h3 style={{ marginTop: 0 }}>{initialValue ? 'Editar Horario' : 'Nuevo Horario'}</h3>
                <div className="flex-col gap-4">
                    <div className="flex-col gap-2">
                        <label className="text-muted" style={{ fontSize: '12px' }}>Nombre</label>
                        <input value={name} onChange={e => setName(e.target.value)} placeholder="Ej: Mañana" autoFocus className="form-control" />
                    </div>

                    <div className="flex-row gap-2 align-center">
                        <input type="checkbox" checked={isFlexible} onChange={e => setIsFlexible(e.target.checked)} id="cx_flex" />
                        <label htmlFor="cx_flex" style={{ fontSize: '14px', fontWeight: 500 }}>Horario Flexible</label>
                    </div>

                    {!isFlexible && (
                        <>
                            <div className="flex-row gap-4">
                                <div className="flex-col gap-2" style={{ flex: 1 }}>
                                    <label className="text-muted" style={{ fontSize: '12px' }}>Hora Entrada</label>
                                    <input type="time" value={onDuty} onChange={e => setOnDuty(e.target.value)} className="form-control" />
                                </div>
                                <div className="flex-col gap-2" style={{ flex: 1 }}>
                                    <label className="text-muted" style={{ fontSize: '12px' }}>Hora Salida</label>
                                    <input type="time" value={offDuty} onChange={e => setOffDuty(e.target.value)} className="form-control" />
                                </div>
                            </div>

                            <div className="flex-row gap-4">
                                <div className="flex-col gap-2" style={{ flex: 1 }}>
                                    <label className="text-muted" style={{ fontSize: '12px' }}>Tol. Tardía (min)</label>
                                    <input type="number" value={lateAllow} onChange={e => setLateAllow(Number(e.target.value))} className="form-control" />
                                </div>
                                <div className="flex-col gap-2" style={{ flex: 1 }}>
                                    <label className="text-muted" style={{ fontSize: '12px' }}>Tol. Temprana (min)</label>
                                    <input type="number" value={earlyAllow} onChange={e => setEarlyAllow(Number(e.target.value))} className="form-control" />
                                </div>
                            </div>
                        </>
                    )}

                    {isFlexible && (
                        <>
                            <div className="flex-col gap-2">
                                <label className="text-muted" style={{ fontSize: '12px' }}>Cantidad de tiempo máximo a trabajar por jornada (minutos)</label>
                                <input type="number" value={reqMin} onChange={e => setReqMin(Number(e.target.value))} className="form-control" placeholder="ej: 480" />
                            </div>
                            <div className="flex-col gap-2">
                                <label className="text-muted" style={{ fontSize: '12px' }}>Cantidad de tiempo de descanso (minutos)</label>
                                <input type="number" value={breakMin} onChange={e => setBreakMin(Number(e.target.value))} className="form-control" placeholder="ej: 60" />
                            </div>
                        </>
                    )}

                    {!isFlexible && (
                        <>
                            <div className="flex-row gap-4">
                                <div className="flex-col gap-2" style={{ flex: 1 }}>
                                    <label className="text-muted" style={{ fontSize: '12px' }}>Fichaje Entrada (Inicio)</label>
                                    <input type="time" value={checkInStart} onChange={e => setCheckInStart(e.target.value)} className="form-control" />
                                </div>
                                <div className="flex-col gap-2" style={{ flex: 1 }}>
                                    <label className="text-muted" style={{ fontSize: '12px' }}>Fichaje Entrada (Fin)</label>
                                    <input type="time" value={checkInEnd} onChange={e => setCheckInEnd(e.target.value)} className="form-control" />
                                </div>
                            </div>

                            <div className="flex-row gap-4">
                                <div className="flex-col gap-2" style={{ flex: 1 }}>
                                    <label className="text-muted" style={{ fontSize: '12px' }}>Fichaje Salida (Inicio)</label>
                                    <input type="time" value={checkOutStart} onChange={e => setCheckOutStart(e.target.value)} className="form-control" />
                                </div>
                                <div className="flex-col gap-2" style={{ flex: 1 }}>
                                    <label className="text-muted" style={{ fontSize: '12px' }}>Fichaje Salida (Fin)</label>
                                    <input type="time" value={checkOutEnd} onChange={e => setCheckOutEnd(e.target.value)} className="form-control" />
                                </div>
                            </div>

                            <hr style={{ margin: '10px 0', border: 'none', borderTop: '1px solid var(--border-color)' }} />

                            <div className="flex-row gap-4">
                                <div className="flex-col gap-2" style={{ flex: 1 }}>
                                    <label className="text-muted" style={{ fontSize: '12px' }}>Descanso (min)</label>
                                    <input type="number" value={breakMin} onChange={e => setBreakMin(Number(e.target.value))} className="form-control" />
                                </div>
                                <div className="flex-col gap-2" style={{ flex: 1 }}>
                                    <label className="text-muted" style={{ fontSize: '12px' }}>Redondeo</label>
                                    <select value={rounding} onChange={e => setRounding(e.target.value)} className="form-control">
                                        <option value="none">Ninguno</option>
                                        <option value="5min">5 Minutos</option>
                                        <option value="10min">10 Minutos</option>
                                        <option value="15min">15 Minutos</option>
                                        <option value="30min">30 Minutos</option>
                                    </select>
                                </div>
                            </div>
                        </>
                    )}

                    <div className="flex-row gap-2" style={{ marginTop: '20px', justifyContent: 'flex-end' }}>
                        <button onClick={onClose} className="secondary">Cancelar</button>
                        <button className="primary" onClick={() => {
                            const payload: any = {
                                name,
                                is_flexible: isFlexible,
                                break_minutes: breakMin,
                            };

                            if (isFlexible) {
                                payload.required_minutes = reqMin;
                                payload.check_in_start = checkInStart || undefined;
                                payload.check_in_end = checkInEnd || undefined;
                                payload.check_out_start = checkOutStart || undefined;
                                payload.check_out_end = checkOutEnd || undefined;
                            } else {
                                payload.on_duty_time = onDuty;
                                payload.off_duty_time = offDuty;
                                payload.late_allow_minutes = lateAllow;
                                payload.early_leave_allow_minutes = earlyAllow;
                                payload.check_in_start = checkInStart || undefined;
                                payload.check_in_end = checkInEnd || undefined;
                                payload.check_out_start = checkOutStart || undefined;
                                payload.check_out_end = checkOutEnd || undefined;
                                payload.rounding_rule = rounding;
                            }

                            if (initialValue?.id) payload.id = initialValue.id;
                            if (initialValue?.work_days) payload.work_days = initialValue.work_days;

                            onSave(payload);
                        }}>{initialValue ? 'Actualizar' : 'Guardar'}</button>
                    </div>
                </div>
            </div>
        </div>
    );
};
