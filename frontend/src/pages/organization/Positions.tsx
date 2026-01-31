import React, { useEffect, useState } from 'react';
import { Plus, Briefcase, Edit2, Trash2, X } from 'lucide-react';
import { getPositions, createPosition, updatePosition, deletePosition, type Position } from '../../api';
import { DataGrid, type Column } from '../../components/ui/DataGrid';
import { PageToolbar } from '../../components/ui/PageToolbar';
import { ConfirmDialog } from '../../components/ui/ConfirmDialog';
import { toast } from 'react-toastify';

export const Positions: React.FC = () => {
    const [positions, setPositions] = useState<Position[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    // Modal State
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingItem, setEditingItem] = useState<Position | null>(null);

    // Delete State
    const [deleteId, setDeleteId] = useState<number | null>(null);

    const fetchData = async () => {
        setLoading(true);
        try {
            const data = await getPositions();
            setPositions(data);
        } catch (error) {
            console.error(error);
            toast.error('Error al cargar cargos');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleSave = async (item: Position) => {
        try {
            if (editingItem?.id) {
                await updatePosition(editingItem.id, item);
                toast.success('Cargo actualizado');
            } else {
                await createPosition(item);
                toast.success('Cargo creado');
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
            await deletePosition(deleteId);
            toast.success('Cargo eliminado');
            setDeleteId(null);
            fetchData();
        } catch (error) {
            console.error(error);
            toast.error('Error al eliminar');
        }
    };

    const filteredData = positions.filter(p =>
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.code?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const columns: Column<Position>[] = [
        {
            field: 'name',
            header: 'Nombre del Cargo',
            render: (row) => (
                <div className="flex items-center gap-2">
                    <Briefcase size={16} className="text-muted" />
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
                title="Cargos"
                subtitle="Gestión de puestos y funciones laborales"
                onSearch={setSearchTerm}
                searchPlaceholder="Buscar cargo..."
                actions={
                    <button
                        className="primary flex items-center gap-2"
                        onClick={() => { setEditingItem(null); setIsModalOpen(true); }}
                    >
                        <Plus size={16} /> Nuevo Cargo
                    </button>
                }
            />

            <div className="card p-0 overflow-hidden mt-4">
                <DataGrid
                    columns={columns}
                    data={filteredData}
                    loading={loading}
                    placeholder="No hay cargos registrados"
                />
            </div>

            {isModalOpen && (
                <PositionModal
                    item={editingItem}
                    onClose={() => setIsModalOpen(false)}
                    onSave={handleSave}
                />
            )}

            <ConfirmDialog
                isOpen={!!deleteId}
                title="Eliminar Cargo"
                message="¿Está seguro de eliminar este cargo? Esta acción no se puede deshacer."
                onConfirm={handleDelete}
                onCancel={() => setDeleteId(null)}
                type="danger"
            />
        </div>
    );
};

const PositionModal: React.FC<{
    item: Position | null;
    onClose: () => void;
    onSave: (item: Position) => void;
}> = ({ item, onClose, onSave }) => {
    const [form, setForm] = useState<Position>(item || { name: '', code: '', description: '' });

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="card w-full max-w-md p-6">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-semibold m-0">
                        {item ? 'Editar Cargo' : 'Nuevo Cargo'}
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
