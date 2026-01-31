import React, { useEffect, useState } from 'react';
import { Plus, MapPin, Edit2, Trash2, X } from 'lucide-react';
import { getZones, createZone, updateZone, deleteZone, type Zone } from '../../api';
import { DataGrid, type Column } from '../../components/ui/DataGrid';
import { PageToolbar } from '../../components/ui/PageToolbar';
import { ConfirmDialog } from '../../components/ui/ConfirmDialog';
import { toast } from 'react-toastify';

export const Zones: React.FC = () => {
    const [zones, setZones] = useState<Zone[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    // Modal State
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingItem, setEditingItem] = useState<Zone | null>(null);

    // Delete State
    const [deleteId, setDeleteId] = useState<number | null>(null);

    const fetchData = async () => {
        setLoading(true);
        try {
            const data = await getZones();
            setZones(data);
        } catch (error) {
            console.error(error);
            toast.error('Error al cargar zonas');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleSave = async (item: Zone) => {
        try {
            if (editingItem?.id) {
                await updateZone(editingItem.id, item);
                toast.success('Zona actualizada');
            } else {
                await createZone(item);
                toast.success('Zona creada');
            }
            setIsModalOpen(false);
            setEditingItem(null);
            fetchData();
        } catch (error) {
            console.error(error);
            toast.error('Error al guardar');
        }
    };

    const handleDelete = async () => {
        if (!deleteId) return;
        try {
            await deleteZone(deleteId);
            toast.success('Zona eliminada');
            setDeleteId(null);
            fetchData();
        } catch (error) {
            console.error(error);
            toast.error('Error al eliminar');
        }
    };

    const filteredData = zones.filter(z =>
        z.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        z.code?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const columns: Column<Zone>[] = [
        {
            field: 'name',
            header: 'Nombre de Zona',
            render: (row) => (
                <div className="flex items-center gap-2">
                    <MapPin size={16} className="text-muted" />
                    <span className="font-medium">{row.name}</span>
                </div>
            )
        },
        { field: 'code', header: 'Código', width: '150px' },
        { field: 'description', header: 'Descripción' },
        {
            field: 'actions',
            header: 'Acciones',
            align: 'right',
            width: '120px',
            render: (row) => (
                <div className="flex justify-end gap-2">
                    <button
                        className="icon-btn text-blue-600 hover:bg-blue-50"
                        onClick={(e) => { e.stopPropagation(); setEditingItem(row); setIsModalOpen(true); }}
                        title="Editar"
                    >
                        <Edit2 size={16} />
                    </button>
                    <button
                        className="icon-btn text-red-600 hover:bg-red-50"
                        onClick={(e) => { e.stopPropagation(); setDeleteId(row.id!); }}
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
                title="Zonas"
                subtitle="Ubicaciones geográficas de dispositivos"
                onSearch={setSearchTerm}
                searchPlaceholder="Buscar zona..."
                actions={
                    <button
                        className="primary flex items-center gap-2"
                        onClick={() => { setEditingItem(null); setIsModalOpen(true); }}
                    >
                        <Plus size={16} /> Nueva Zona
                    </button>
                }
            />

            <div className="card p-0 overflow-hidden mt-4">
                <DataGrid
                    columns={columns}
                    data={filteredData}
                    loading={loading}
                    placeholder="No hay zonas registradas"
                />
            </div>

            {isModalOpen && (
                <ZoneModal
                    item={editingItem}
                    onClose={() => setIsModalOpen(false)}
                    onSave={handleSave}
                />
            )}

            <ConfirmDialog
                isOpen={!!deleteId}
                title="Eliminar Zona"
                message="¿Está seguro de eliminar esta zona? Esta acción no se puede deshacer."
                onConfirm={handleDelete}
                onCancel={() => setDeleteId(null)}
                type="danger"
            />
        </div>
    );
};

const ZoneModal: React.FC<{
    item: Zone | null;
    onClose: () => void;
    onSave: (item: Zone) => void;
}> = ({ item, onClose, onSave }) => {
    const [form, setForm] = useState<Zone>(item || { name: '', code: '', description: '' });

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="card w-full max-w-md p-6">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-semibold m-0">
                        {item ? 'Editar Zona' : 'Nueva Zona'}
                    </h3>
                    <button onClick={onClose} className="icon-btn"><X size={20} /></button>
                </div>

                <div className="flex flex-col gap-4">
                    <div className="form-group">
                        <label className="text-sm font-medium mb-1 block">Nombre *</label>
                        <input
                            className="form-control w-full"
                            value={form.name}
                            onChange={e => setForm({ ...form, name: e.target.value })}
                            autoFocus
                        />
                    </div>
                    <div className="form-group">
                        <label className="text-sm font-medium mb-1 block">Código</label>
                        <input
                            className="form-control w-full"
                            value={form.code || ''}
                            onChange={e => setForm({ ...form, code: e.target.value })}
                        />
                    </div>
                    <div className="form-group">
                        <label className="text-sm font-medium mb-1 block">Descripción</label>
                        <textarea
                            className="form-control w-full"
                            rows={3}
                            value={form.description || ''}
                            onChange={e => setForm({ ...form, description: e.target.value })}
                        />
                    </div>
                </div>

                <div className="flex justify-end gap-2 mt-6">
                    <button className="secondary" onClick={onClose}>Cancelar</button>
                    <button
                        className="primary"
                        onClick={() => form.name && onSave(form)}
                        disabled={!form.name}
                    >
                        Guardar
                    </button>
                </div>
            </div>
        </div>
    );
};
