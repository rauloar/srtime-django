import React, { useEffect, useState } from 'react';
import { Save, Building } from 'lucide-react';
import { getCompany, updateCompany, type Company as CompanyModel } from '../../api';
import { PageToolbar } from '../../components/ui/PageToolbar';
import { toast } from 'react-toastify';

export const Company: React.FC = () => {
    const [company, setCompany] = useState<CompanyModel | null>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            // Note: The backend should return the singleton company (id=1)
            // If it returns a list, take the first one. Adapting based on API response structure.
            const data: any = await getCompany();
            if (Array.isArray(data)) {
                setCompany(data[0] || { id: 1, name: '', address: '' });
            } else {
                setCompany(data);
            }
        } catch (error) {
            console.error(error);
            toast.error('Error cargando información de la empresa');
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        if (!company) return;
        setSaving(true);
        try {
            await updateCompany(company);
            toast.success('Información actualizada correctamente');
        } catch (error) {
            console.error(error);
            toast.error('Error al guardar cambios');
        } finally {
            setSaving(false);
        }
    };

    const handleChange = (field: keyof CompanyModel, value: string) => {
        if (company) {
            setCompany({ ...company, [field]: value });
        }
    };

    if (loading) return <div className="p-4">Cargando...</div>;

    return (
        <div className="w-full">
            <PageToolbar
                title="Información de la Empresa"
                subtitle="Configuración general de la organización"
                actions={
                    <button
                        className="primary flex items-center gap-2"
                        onClick={handleSave}
                        disabled={saving}
                    >
                        <Save size={16} />
                        {saving ? 'Guardando...' : 'Guardar Cambios'}
                    </button>
                }
            />

            <div className="card max-w-2xl mx-auto mt-4">
                <div className="flex items-center gap-3 mb-6 border-b pb-4">
                    <div className="p-3 bg-blue-50 rounded-full text-blue-600">
                        <Building size={24} />
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold m-0">Datos Generales</h3>
                        <p className="text-muted text-sm m-0">Información visible en reportes y encabezados</p>
                    </div>
                </div>

                <div className="flex flex-col gap-4">
                    <div className="form-group">
                        <label className="text-sm font-medium text-gray-700 mb-1 block">Nombre de la Empresa</label>
                        <input
                            type="text"
                            className="form-control w-full"
                            value={company?.name || ''}
                            onChange={(e) => handleChange('name', e.target.value)}
                            placeholder="Ej: Acme Corp"
                        />
                    </div>

                    <div className="form-group">
                        <label className="text-sm font-medium text-gray-700 mb-1 block">Código</label>
                        <input
                            type="text"
                            className="form-control w-full"
                            value={company?.code || ''}
                            onChange={(e) => handleChange('code', e.target.value)}
                            placeholder="Código interno"
                        />
                    </div>

                    <div className="form-group">
                        <label className="text-sm font-medium text-gray-700 mb-1 block">Dirección</label>
                        <input
                            type="text"
                            className="form-control w-full"
                            value={company?.address || ''}
                            onChange={(e) => handleChange('address', e.target.value)}
                            placeholder="Dirección fiscal o comercial"
                        />
                    </div>

                    <div className="form-group">
                        <label className="text-sm font-medium text-gray-700 mb-1 block">Sitio Web</label>
                        <input
                            type="text"
                            className="form-control w-full"
                            value={company?.website || ''}
                            onChange={(e) => handleChange('website', e.target.value)}
                            placeholder="https://..."
                        />
                    </div>

                    <div className="form-group">
                        <label className="text-sm font-medium text-gray-700 mb-1 block">Ruta del Logo</label>
                        <input
                            type="text"
                            className="form-control w-full"
                            value={company?.logo_path || ''}
                            onChange={(e) => handleChange('logo_path', e.target.value)}
                            placeholder="/assets/logo.png"
                        />
                        <p className="text-xs text-muted mt-1">Ruta relativa o URL de la imagen del logo.</p>
                    </div>
                </div>
            </div>
        </div>
    );
};
