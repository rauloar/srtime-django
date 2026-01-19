import React, { useState } from 'react';
import { Modal } from '../ui/Modal';
import { createDevice, checkDeviceOnline } from '../../api';
import { useToast } from '../../hooks/useToast';

interface DeviceFormModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
}

export const DeviceFormModal: React.FC<DeviceFormModalProps> = ({ isOpen, onClose, onSuccess }) => {
    const toast = useToast();
    const [formData, setFormData] = useState({
        name: '',
        ip: '',
        port: 4370,
        password: 0,
        zone: '',
        location: '',
        device_name: ''
    });
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        
        if (!formData.name.trim()) {
            toast.error('El nombre del dispositivo es requerido');
            return;
        }
        if (!formData.ip.trim()) {
            toast.error('La dirección IP es requerida');
            return;
        }
        if (!formData.port || formData.port < 1 || formData.port > 65535) {
            toast.error('El puerto debe estar entre 1 y 65535');
            return;
        }

        setLoading(true);

        try {
            // First, test the connection to verify device is reachable
            toast.info('Verificando conexión con el dispositivo...');
            
            // Create a temporary device object to test
            const tempDeviceData = {
                ...formData,
                enabled: true
            };
            
            // Create the device first
            const createdDevice = await createDevice(tempDeviceData);

            // Now test the connection (solo si hay ID válido)
            if (!createdDevice.id && createdDevice.id !== 0) {
                toast.warning('⚠️ Dispositivo creado, pero no se recibió ID para verificar la conexión');
            } else {
                const testResult = await checkDeviceOnline(createdDevice.id as number);
                if (!testResult.online) {
                    toast.warning(`⚠️ Dispositivo creado pero NO se pudo verificar conexión. Verifica IP ${formData.ip}:${formData.port}`);
                } else {
                    toast.success(`✅ Dispositivo "${formData.name}" creado y verificado correctamente`);
                }
            }
            
            onSuccess();
            onClose();
            // Reset form
            setFormData({
                name: '',
                ip: '',
                port: 4370,
                password: 0,
                zone: '',
                location: '',
                device_name: ''
            });
        } catch (err: any) {
            toast.error(err.response?.data?.detail || 'Error al crear dispositivo');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Nuevo Dispositivo">
            <form onSubmit={handleSubmit} className="flex-col gap-4">
                <div className="form-group">
                    <label>Nombre</label>
                    <input
                        type="text"
                        required
                        value={formData.name}
                        onChange={e => setFormData({ ...formData, name: e.target.value })}
                        placeholder="Ej. Puerta Principal"
                        disabled={loading}
                    />
                </div>

                <div className="flex-row gap-4">
                    <div className="form-group" style={{ flex: 2 }}>
                        <label>Dirección IP</label>
                        <input
                            type="text"
                            required
                            pattern="^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
                            value={formData.ip}
                            onChange={e => setFormData({ ...formData, ip: e.target.value })}
                            placeholder="192.168.1.201"
                            disabled={loading}
                        />
                    </div>
                    <div className="form-group" style={{ flex: 1 }}>
                        <label>Puerto</label>
                        <input
                            type="number"
                            required
                            value={formData.port}
                            onChange={e => setFormData({ ...formData, port: parseInt(e.target.value) })}
                            disabled={loading}
                        />
                    </div>
                </div>

                <div className="form-group">
                    <label>Zona</label>
                    <input
                        type="text"
                        value={formData.zone}
                        onChange={e => setFormData({ ...formData, zone: e.target.value })}
                        placeholder="Ej. Planta Baja"
                        disabled={loading}
                    />
                </div>

                <div className="flex-row gap-2 mt-4" style={{ justifyContent: 'flex-end' }}>
                    <button type="button" onClick={onClose} disabled={loading} style={{ background: 'transparent', border: '1px solid var(--border-color)' }}>
                        Cancelar
                    </button>
                    <button type="submit" className="primary" disabled={loading}>
                        {loading ? 'Guardando...' : 'Guardar Dispositivo'}
                    </button>
                </div>
            </form>
        </Modal>
    );
};
