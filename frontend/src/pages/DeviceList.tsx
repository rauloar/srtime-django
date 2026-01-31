import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { RefreshCw, Plus, Search } from 'lucide-react';
import { getDevices, getAllDevicesConnectionStatus, type Device, type DeviceConnectionStatus } from '../api';
import { DeviceFormModal } from '../components/devices/DeviceFormModal';
import { DataGrid, type Column } from '../components/ui/DataGrid';
import { useToast } from '../hooks/useToast';
import './DeviceList.css';

export const DeviceList: React.FC = () => {
    const navigate = useNavigate();
    const toast = useToast();
    const [devices, setDevices] = useState<Device[]>([]);
    const [connectionStatus, setConnectionStatus] = useState<Record<number, DeviceConnectionStatus>>({});
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [checkingConnections, setCheckingConnections] = useState(false);

    const fetchDevices = async () => {
        setLoading(true);
        try {
            const data = await getDevices();
            setDevices(data || []);
            // Clear connection status when fetching devices (on demand only)
            setConnectionStatus({});
        } catch (error) {
            console.error("Failed to fetch devices", error);
            toast.error('Error al cargar dispositivos');
        } finally {
            setLoading(false);
        }
    };

    const checkDevicesConnection = async () => {
        setCheckingConnections(true);
        try {
            const statusData = await getAllDevicesConnectionStatus();
            const statusMap: Record<number, DeviceConnectionStatus> = {};
            statusData.devices.forEach(status => {
                statusMap[status.device_id] = status;
            });
            setConnectionStatus(statusMap);
        } catch (error) {
            console.error("Failed to check device connections", error);
            // Don't show error toast - this is background check
        } finally {
            setCheckingConnections(false);
        }
    };

    useEffect(() => {
        fetchDevices();
    }, []);

    const handleModalSuccess = () => {
        setIsModalOpen(false);
        toast.success('Dispositivo creado exitosamente');
        fetchDevices();
    };

    const filteredDevices = devices.filter(d =>
        d.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        d.ip.includes(searchTerm) ||
        (d.serialnumber && d.serialnumber.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    const columns: Column<Device>[] = [
        {
            field: 'name',
            header: 'Nombre Dispositivo',
            render: (dev) => (
                <div>
                    <div style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{dev.name}</div>
                    <div style={{ fontSize: '11px', color: '#888' }}>{dev.serialnumber || '-'}</div>
                </div>
            )
        },
        {
            field: 'ip',
            header: 'Dirección IP',
            width: '150px',
            render: (dev) => <span style={{ fontFamily: 'monospace' }}>{dev.ip}:{dev.port}</span>
        },
        {
            field: 'status',
            header: 'Estado',
            width: '180px',
            align: 'center',
            render: (dev) => {
                const deviceId = dev.id;
                const connStatus = deviceId !== undefined ? connectionStatus[deviceId] : undefined;
                return (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', alignItems: 'center' }}>
                        {/* Estado Activo/Inactivo (persistente) */}
                        <span className={`status-badge ${dev.enabled ? 'status-ok' : 'status-offline'}`}>
                            {dev.enabled ? '✓ ACTIVO' : '✗ INACTIVO'}
                        </span>
                        {/* Estado Conectada/Desconectada (on demand) */}
                        {connStatus ? (
                            <span className={`status-badge ${connStatus.connected ? 'status-ok' : 'status-offline'}`} style={{ fontSize: '11px' }}>
                                {connStatus.connected ? '🟢 CONECTADA' : '🔴 DESCONECTADA'}
                            </span>
                        ) : (
                            <span className="status-badge" style={{ fontSize: '11px', opacity: 0.5, backgroundColor: 'var(--status-offline)' }}>
                                ○ NO VERIFICADA
                            </span>
                        )}
                    </div>
                );
            }
        },
        {
            field: 'user_count',
            header: 'Usuarios',
            width: '100px',
            align: 'center'
        },
        {
            field: 'transaction_count',
            header: 'Registros',
            width: '100px',
            align: 'center'
        },
        {
            field: 'last_seen',
            header: 'Última Conexión',
            width: '180px',
            render: (dev) => (
                <span style={{ fontSize: '12px', color: '#666' }}>
                    {dev.last_seen ? new Date(dev.last_seen).toLocaleString() : '-'}
                </span>
            )
        }
    ];

    return (
        <div className="container-desktop">
            <div className="flex-col gap-4">
                <div className="page-toolbar-desktop">
                    <div className="flex-col">
                        <h2 style={{ margin: 0, fontSize: '22px', fontWeight: 600, color: '#333' }}>Dispositivos</h2>
                        <span style={{ fontSize: '13px', color: '#888' }}>Gestión de terminales de asistencia</span>
                    </div>
                    <div className="page-toolbar-actions">
                        <button
                            className="flex-row gap-2"
                            onClick={fetchDevices}
                            style={{ height: '36px' }}
                            disabled={loading}
                        >
                            <RefreshCw size={14} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
                            Refrescar Lista
                        </button>
                        <button
                            className="flex-row gap-2"
                            onClick={checkDevicesConnection}
                            style={{ height: '36px' }}
                            disabled={checkingConnections || devices.length === 0}
                        >
                            <RefreshCw size={14} style={{ animation: checkingConnections ? 'spin 1s linear infinite' : 'none' }} />
                            {checkingConnections ? 'Verificando...' : 'Verificar Conexión'}
                        </button>
                        <button
                            className="primary flex-row gap-2"
                            onClick={() => setIsModalOpen(true)}
                            style={{ height: '36px' }}
                            disabled={loading}
                        >
                            <Plus size={14} /> Agregar Terminal
                        </button>
                    </div>
                </div>

                <div className="card" style={{ padding: '0', border: 'none', boxShadow: 'none', background: 'transparent' }}>
                    {/* Search Bar stylized like ZK */}
                    <div style={{
                        background: '#fff',
                        padding: '15px',
                        border: '1px solid var(--border-color)',
                        borderBottom: 'none',
                        borderRadius: '2px 2px 0 0',
                        display: 'flex',
                        justifyContent: 'space-between'
                    }}>
                        <div className="page-toolbar-search">
                            <Search size={16} style={{ position: 'absolute', left: '10px', color: '#999' }} />
                            <input
                                type="text"
                                placeholder="Buscar por nombre, IP o serial..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                style={{ paddingLeft: '32px', width: '100%', height: '34px' }}
                            />
                        </div>
                    </div>

                    <DataGrid
                        columns={columns}
                        data={filteredDevices}
                        loading={loading}
                        onRowClick={(dev) => {
                            if (dev.id === undefined) return;
                            localStorage.setItem('lastSelectedDeviceId', dev.id.toString());
                            navigate(`/devices/${dev.id}`);
                        }}
                        placeholder="No se encontraron dispositivos registrados"
                    />
                </div>

                <DeviceFormModal
                    isOpen={isModalOpen}
                    onClose={() => setIsModalOpen(false)}
                    onSuccess={handleModalSuccess}
                />
            </div>
        </div>
    );
};
