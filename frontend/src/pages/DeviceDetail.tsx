import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
    getDevice,
    getDeviceInfo,
    getDeviceUsers,
    importAttendance,
    downloadUsers,
    syncUsers,
    restartDevice,
    poweroffDevice,
    syncTime,
    testVoice,
    getMemoryInfo,
    clearAllData,
    clearAttendance,
    getRecentAttendance,
    getDeviceTemplates
} from '../api';
import { Download, RefreshCw, Cpu, Users, Fingerprint, Activity, FileText, Clock, Smile, CreditCard, Key, Power, Volume2, Trash2, AlertTriangle, Upload } from 'lucide-react';
import type { Device, TestResponse, JobResponse, DeviceUser, MemoryInfo, RecentAttendanceRecord } from '../api';
import { JobProgressModal } from '../components/ui/JobProgressModal';
import { ConfirmationModal } from '../components/ui/ConfirmationModal';
import { useToast } from '../hooks/useToast';
import { CommandCard, MemoryCard, RecentLogsCard, TemplatesCard } from '../components/device/FunctionCards';

export function DeviceDetail() {
    const { id } = useParams<{ id: string }>();
    const deviceId = parseInt(id || '0');
    const toast = useToast();

    const [device, setDevice] = useState<Device | null>(null);
    const [info, setInfo] = useState<TestResponse | null>(null);
    const [users, setUsers] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [importing, setImporting] = useState(false);
    const [downloadingUsers, setDownloadingUsers] = useState(false);
    const [uploadingUsers, setUploadingUsers] = useState(false);
    const [activeTab, setActiveTab] = useState<'info' | 'users' | 'funciones'>('info');

    // Additional Functions States
    const [memoryInfo, setMemoryInfo] = useState<MemoryInfo | null>(null);
    const [loadingMemory, setLoadingMemory] = useState(false);
    const [recentLogs, setRecentLogs] = useState<RecentAttendanceRecord[]>([]);
    const [loadingRecentLogs, setLoadingRecentLogs] = useState(false);
    const [templates, setTemplates] = useState<any | null>(null);
    const [loadingTemplates, setLoadingTemplates] = useState(false);
    const [processingCommand, setProcessingCommand] = useState(false);

    // Progress Modal State
    const [activeJobId, setActiveJobId] = useState<string>('');
    const [isProgressOpen, setIsProgressOpen] = useState(false);

    // Confirmation Modal State
    const [confirmationModal, setConfirmationModal] = useState<{
        isOpen: boolean;
        title: string;
        message: string;
        variant: 'danger' | 'warning';
        onConfirm: () => void;
    }>({ isOpen: false, title: '', message: '', variant: 'warning', onConfirm: () => { } });

    useEffect(() => {
        if (deviceId) {
            loadData();
        }
    }, [deviceId]);

    const loadData = async () => {
        try {
            const d = await getDevice(deviceId);
            setDevice(d);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const handleRefreshInfo = async () => {
        setRefreshing(true);
        try {
            const res = await getDeviceInfo(deviceId);
            setInfo(res);
            // Wait a moment for DB update if backend is async, then reload
            await new Promise(r => setTimeout(r, 500));
            await loadData();
        } catch (e) {
            toast.warning('⚠️ No se pudo conectar al dispositivo. Intentar conectar más tarde');
        } finally {
            setRefreshing(false);
        }
    };

    const handleImport = async () => {
        setImporting(true);
        try {
            const res: JobResponse = await importAttendance(deviceId);
            if (res.job_id) {
                setActiveJobId(res.job_id);
                setIsProgressOpen(true);
            }
        } catch (e) {
            alert('No se pudo iniciar la importación');
        } finally {
            setImporting(false);
        }
    };

    const handleDownloadUsers = async () => {
        setDownloadingUsers(true);
        try {
            const res: JobResponse = await downloadUsers(deviceId);
            if (res.job_id) {
                setActiveJobId(res.job_id);
                setIsProgressOpen(true);
            }
        } catch (e) {
            alert('No se pudo iniciar la descarga de usuarios');
        } finally {
            setDownloadingUsers(false);
        }
    };

    const handleSyncUsers = async () => {
        setUploadingUsers(true);
        try {
            const res: JobResponse = await syncUsers(deviceId);
            if (res.job_id) {
                setActiveJobId(res.job_id);
                setIsProgressOpen(true);
            }
        } catch (e) {
            alert('No se pudo iniciar la sincronización de usuarios');
        } finally {
            setUploadingUsers(false);
        }
    };

    const loadUsers = async () => {
        try {
            const u = await getDeviceUsers(deviceId);
            setUsers(u);
        } catch (e) {
            alert('Error al cargar usuarios');
        }
    };

    // ========== ADDITIONAL FUNCTION HANDLERS ==========

    const handleRestart = async () => {
        setProcessingCommand(true);
        try {
            const res = await restartDevice(deviceId);
            if (res.success) {
                toast.success('Dispositivo reiniciado correctamente');
            } else {
                toast.warning('⚠️ No se pudo conectar al dispositivo. Intentar conectar más tarde');
            }
        } catch (e) {
            toast.warning('⚠️ No se pudo conectar al dispositivo. Intentar conectar más tarde');
        } finally {
            setProcessingCommand(false);
        }
    };

    const handlePoweroff = async () => {
        setProcessingCommand(true);
        try {
            const res = await poweroffDevice(deviceId);
            if (res.success) {
                toast.success('Dispositivo apagado correctamente');
            } else {
                toast.warning('⚠️ No se pudo conectar al dispositivo. Intentar conectar más tarde');
            }
        } catch (e) {
            toast.warning('⚠️ No se pudo conectar al dispositivo. Intentar conectar más tarde');
        } finally {
            setProcessingCommand(false);
        }
    };

    const handleSyncTime = async () => {
        setProcessingCommand(true);
        try {
            const res = await syncTime(deviceId);
            if (res.success) {
                toast.success('Hora sincronizada correctamente');
            } else {
                toast.warning('⚠️ No se pudo conectar al dispositivo. Intentar conectar más tarde');
            }
        } catch (e) {
            toast.warning('⚠️ No se pudo conectar al dispositivo. Intentar conectar más tarde');
        } finally {
            setProcessingCommand(false);
        }
    };

    const handleTestVoice = async (voiceIndex: number = 0) => {
        setProcessingCommand(true);
        try {
            const res = await testVoice(deviceId, voiceIndex);
            if (res.success) {
                toast.success('Prueba de voz enviada');
            } else {
                toast.warning('⚠️ No se pudo conectar al dispositivo. Intentar conectar más tarde');
            }
        } catch (e) {
            toast.warning('⚠️ No se pudo conectar al dispositivo. Intentar conectar más tarde');
        } finally {
            setProcessingCommand(false);
        }
    };

    const handleLoadMemory = async () => {
        setLoadingMemory(true);
        try {
            const res = await getMemoryInfo(deviceId);
            if (res.success) {
                setMemoryInfo(res);
            } else {
                toast.warning('⚠️ No se pudo conectar al dispositivo. Intentar conectar más tarde');
            }
        } catch (e) {
            toast.warning('⚠️ No se pudo conectar al dispositivo. Intentar conectar más tarde');
        } finally {
            setLoadingMemory(false);
        }
    };

    const handleClearAttendance = async () => {
        try {
            const res: JobResponse = await clearAttendance(deviceId);
            if (res.job_id) {
                setActiveJobId(res.job_id);
                setIsProgressOpen(true);
            }
        } catch (e) {
            toast.error('Error al iniciar limpieza');
        }
    };

    const handleClearAllData = async () => {
        const confirmed = window.confirm(
            '⚠️ PELIGRO CRÍTICO: Esta acción borrará TODO:\n\n' +
            '- Todos los usuarios\n' +
            '- Todas las huellas\n' +
            '- Todos los registros\n\n' +
            '¿Estás COMPLETAMENTE seguro?'
        );
        if (!confirmed) return;

        const doubleCheck = prompt('Escribe "BORRAR TODO" para confirmar (SIN comillas):');
        if (doubleCheck !== 'BORRAR TODO') {
            toast.warning('Acción cancelada');
            return;
        }

        try {
            const res: JobResponse = await clearAllData(deviceId);
            if (res.job_id) {
                setActiveJobId(res.job_id);
                setIsProgressOpen(true);
            }
        } catch (e) {
            toast.error('Error al iniciar limpieza');
        }
    };

    const handleLoadRecentLogs = async () => {
        setLoadingRecentLogs(true);
        try {
            const res = await getRecentAttendance(deviceId, 50);
            if (res.success) {
                setRecentLogs(res.records);
            } else {
                toast.error(res.message);
            }
        } catch (e) {
            toast.error('Error al cargar registros recientes');
        } finally {
            setLoadingRecentLogs(false);
        }
    };

    const handleLoadTemplates = async () => {
        setLoadingTemplates(true);
        try {
            const res = await getDeviceTemplates(deviceId);
            if (res.success) {
                setTemplates(res); // Save full response with saved/skipped/errors
                toast.success(res.message);
            } else {
                toast.warning('⚠️ No se pudo conectar al dispositivo. Intentar conectar más tarde');
            }
        } catch (e) {
            toast.warning('⚠️ No se pudo conectar al dispositivo. Intentar conectar más tarde');
        } finally {
            setLoadingTemplates(false);
        }
    };

    useEffect(() => {
        if (activeTab === 'users' && users.length === 0) {
            loadUsers();
        }
    }, [activeTab]);

    if (loading || !device) return <p style={{ padding: '20px' }}>Cargando dispositivo...</p>;

    // Merge DB info with Live info if available, preferring Live
    const displayDevice = {
        ...device, ...(info?.success ? {
            firmware_version: info.firmware_version,
            serialnumber: info.serial_number,
            platform: info.platform,
            device_name: info.device_name,
            mac: info.mac,
            user_count: info.users_count,
            fp_count: info.fingers_count,
            records_count: info.records_count
        } : {})
    };

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
                <div>
                    <h1 style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        {device.name}
                        {device.enabled ?
                            <span style={{ fontSize: '12px', background: '#2ea043', color: 'white', padding: '2px 8px', borderRadius: '12px' }}>Habilitado</span> :
                            <span style={{ fontSize: '12px', background: '#8b949e', color: 'white', padding: '2px 8px', borderRadius: '12px' }}>Deshabilitado</span>
                        }
                    </h1>
                    <p style={{ color: '#8b949e' }}>{device.ip}:{device.port}</p>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                    <button onClick={handleRefreshInfo} disabled={refreshing}>
                        <RefreshCw size={16} style={{ marginRight: '8px' }} className={refreshing ? 'spin' : ''} />
                        {refreshing ? 'Refrescando...' : 'Refrescar Info'}
                    </button>
                    <button onClick={handleDownloadUsers} disabled={downloadingUsers}>
                        <Users size={16} style={{ marginRight: '8px' }} />
                        {downloadingUsers ? 'Iniciando...' : 'Bajar Usuarios'}
                    </button>
                    <button onClick={handleSyncUsers} disabled={uploadingUsers}>
                        <Upload size={16} style={{ marginRight: '8px' }} />
                        {uploadingUsers ? 'Iniciando...' : 'Subir Usuarios'}
                    </button>
                    <button className="primary" onClick={handleImport} disabled={importing}>
                        <Download size={16} style={{ marginRight: '8px' }} />
                        {importing ? 'Iniciando...' : 'Bajar Fichadas'}
                    </button>
                </div>
            </div>

            {/* Connection Status Panel (Live) */}
            {info && (
                <div className={`card ${info.success ? 'status-ok' : 'status-error'}`} style={{ marginBottom: '20px', border: '1px solid', background: info.success ? 'rgba(46, 160, 67, 0.1)' : 'rgba(218, 54, 51, 0.1)' }}>
                    <h3>Estado Conexión: {info.success ? 'Conectado (Online)' : 'Desconectado (Offline)'}</h3>
                    <p>{info.message}</p>
                    {info.success && <small>La terminal está respondiendo correctamente.</small>}
                </div>
            )}

            <div style={{ borderBottom: '1px solid var(--border)', marginBottom: '20px' }}>
                <button
                    style={{ background: 'transparent', border: 'none', borderBottom: activeTab === 'info' ? '2px solid var(--accent)' : 'none', borderRadius: 0, padding: '10px 20px', cursor: 'pointer', color: activeTab === 'info' ? 'var(--primary)' : 'inherit' }}
                    onClick={() => setActiveTab('info')}
                >
                    Información Terminal
                </button>
                <button
                    style={{ background: 'transparent', border: 'none', borderBottom: activeTab === 'users' ? '2px solid var(--accent)' : 'none', borderRadius: 0, padding: '10px 20px', cursor: 'pointer', color: activeTab === 'users' ? 'var(--primary)' : 'inherit' }}
                    onClick={() => setActiveTab('users')}
                >
                    Usuarios ({users.length || displayDevice.user_count || '?'})
                </button>
                <button
                    style={{ background: 'transparent', border: 'none', borderBottom: activeTab === 'funciones' ? '2px solid var(--accent)' : 'none', borderRadius: 0, padding: '10px 20px', cursor: 'pointer', color: activeTab === 'funciones' ? 'var(--primary)' : 'inherit' }}
                    onClick={() => setActiveTab('funciones')}
                >
                    Funciones Adicionales
                </button>
            </div>

            {activeTab === 'info' && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>

                    {/* Identity Card */}
                    <div className="card">
                        <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Cpu size={18} /> Identidad</h3>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '14px' }}>
                            <div style={{ color: '#8b949e' }}>Nombre Disp.:</div>
                            <div>{displayDevice.device_name || '-'}</div>

                            <div style={{ color: '#8b949e' }}>Nro. Serie:</div>
                            <div>{displayDevice.serialnumber || '-'}</div>

                            <div style={{ color: '#8b949e' }}>Firmware:</div>
                            <div>{displayDevice.firmware_version || '-'}</div>

                            <div style={{ color: '#8b949e' }}>Plataforma:</div>
                            <div>{displayDevice.platform || '-'}</div>

                            <div style={{ color: '#8b949e' }}>MAC:</div>
                            <div>{displayDevice.mac || '-'}</div>
                        </div>
                    </div>

                    {/* Stats Card */}
                    <div className="card">
                        <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Activity size={18} /> Capacidad y Estadísticas</h3>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '14px', alignItems: 'center' }}>
                            <div style={{ color: '#8b949e' }}>Usuarios:</div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}><Users size={14} /> {displayDevice.user_count}</div>

                            <div style={{ color: '#8b949e' }}>Huellas:</div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}><Fingerprint size={14} /> {displayDevice.fp_count}</div>

                            <div style={{ color: '#8b949e' }}>Rostros:</div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}><Smile size={14} /> {displayDevice.face_count}</div>

                            <div style={{ color: '#8b949e' }}>Registros:</div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}><FileText size={14} /> {displayDevice.transaction_count}</div>

                            <div style={{ color: '#8b949e' }}>Visto:</div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}><Clock size={14} /> {displayDevice.last_seen ? new Date(displayDevice.last_seen).toLocaleString() : 'Nunca'}</div>
                        </div>
                    </div>
                </div>
            )}

            {activeTab === 'users' && (
                <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }} className="zk-table">
                        <thead>
                            <tr>
                                <th>UID</th>
                                <th>User ID</th>
                                <th>Nombre</th>
                                <th>Rol</th>
                                <th>Tarjeta</th>
                                <th>Biometría</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map((u: DeviceUser, i) => (
                                <tr key={i}>
                                    <td>{u.uid}</td>
                                    <td>{u.user_id}</td>
                                    <td>{u.name}</td>
                                    <td>{u.privilege}</td>
                                    <td>{u.card}</td>
                                    <td>
                                        <div style={{ display: 'flex', gap: '8px' }}>
                                            {u.finger_count && u.finger_count > 0 ? (
                                                <div title={`${u.finger_count} Huellas`} style={{ color: '#2ea043', display: 'flex', alignItems: 'center', gap: '2px' }}>
                                                    <Fingerprint size={16} /> <span style={{ fontSize: '0.8em' }}>{u.finger_count}</span>
                                                </div>
                                            ) : <Fingerprint size={16} color="#ddd" />}

                                            {u.face_count && u.face_count > 0 ? (
                                                <div title={`${u.face_count} Rostros`} style={{ color: '#2ea043', display: 'flex', alignItems: 'center', gap: '2px' }}>
                                                    <Smile size={16} /> <span style={{ fontSize: '0.8em' }}>{u.face_count}</span>
                                                </div>
                                            ) : <Smile size={16} color="#ddd" />}

                                            {u.card ? (
                                                <div title={`Tarjeta: ${u.card}`} style={{ color: '#2ea043' }}><CreditCard size={16} /></div>
                                            ) : <CreditCard size={16} color="#ddd" />}

                                            {u.password ? (
                                                <div title="Contraseña establecida" style={{ color: '#2ea043' }}><Key size={16} /></div>
                                            ) : <Key size={16} color="#ddd" />}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                            {users.length === 0 && (
                                <tr><td colSpan={6} style={{ padding: '20px', textAlign: 'center', color: '#8b949e' }}>No se han cargado usuarios.</td></tr>
                            )}
                        </tbody>
                    </table>
                </div>
            )}

            {activeTab === 'funciones' && (
                <>
                    {/* Device Status Info */}
                    <div className="card" style={{ marginBottom: '20px', padding: '16px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <Cpu size={20} />
                            <div style={{ flex: 1 }}>
                                <div style={{ fontWeight: 600, fontSize: '16px' }}>📱 {device?.name}</div>
                                <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                                    <span>IP: {device?.ip}:{device?.port}</span>
                                    <span style={{ margin: '0 12px' }}>•</span>
                                    <span>S/N: {device?.serialnumber || 'N/A'}</span>
                                </div>
                            </div>
                            {/* Si el dispositivo existe en BD, está activo */}
                            <span className="status-badge status-ok">
                                ✅ Activo
                            </span>
                        </div>
                    </div>

                    {/* Functions always available if device exists */}
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
                        gap: '20px',
                        marginBottom: '20px'
                    }}>
                        {/* ========== GRUPO 1: COMANDOS BÁSICOS ========== */}
                        <CommandCard
                            icon={<RefreshCw size={32} />}
                            title="Reiniciar Dispositivo"
                            description="Reinicia la terminal remotamente"
                            action={handleRestart}
                            variant="primary"
                            loading={processingCommand}
                        />

                        <CommandCard
                            icon={<Power size={32} />}
                            title="Apagar Dispositivo"
                            description="Apaga la terminal (requiere encendido manual)"
                            action={() => {
                                setConfirmationModal({
                                    isOpen: true,
                                    title: 'Apagar Dispositivo',
                                    message: 'El dispositivo se apagará y deberás encenderlo manualmente. ¿Deseas continuar?',
                                    variant: 'danger',
                                    onConfirm: handlePoweroff
                                });
                            }}
                            variant="danger"
                            loading={processingCommand}
                        />

                        <CommandCard
                            icon={<Clock size={32} />}
                            title="Sincronizar Hora"
                            description="Sincroniza el reloj con el servidor"
                            action={handleSyncTime}
                            variant="primary"
                            loading={processingCommand}
                        />

                        <CommandCard
                            icon={<Volume2 size={32} />}
                            title="Test de Voz"
                            description="Reproduce un mensaje de prueba"
                            action={() => handleTestVoice(0)}
                            variant="primary"
                            loading={processingCommand}
                        />

                        {/* ========== GRUPO 2: MEMORIA ========== */}
                        <MemoryCard
                            memoryInfo={memoryInfo}
                            onLoad={handleLoadMemory}
                            loading={loadingMemory}
                        />

                        {/* ========== GRUPO 3: LIMPIEZA ========== */}
                        <CommandCard
                            icon={<Trash2 size={32} />}
                            title="Limpiar Logs"
                            description="Elimina solo registros de asistencia"
                            action={() => {
                                setConfirmationModal({
                                    isOpen: true,
                                    title: 'Limpiar Logs de Asistencia',
                                    message: 'Se eliminarán todos los registros de asistencia del dispositivo. Los usuarios y huellas se mantendrán intactos.',
                                    variant: 'warning',
                                    onConfirm: handleClearAttendance
                                });
                            }}
                            variant="warning"
                            warning="Operación sensible - Afecta datos históricos"
                        />

                        <CommandCard
                            icon={<AlertTriangle size={32} />}
                            title="Borrar Todo"
                            description="Borra usuarios, huellas y logs"
                            action={() => {
                                setConfirmationModal({
                                    isOpen: true,
                                    title: '⚠️ PELIGRO CRÍTICO',
                                    message: 'Esta acción borrará TODO del dispositivo: \n\n• Todos los usuarios\n• Todas las huellas\n• Todos los registros\n\nEsta operación es irreversible. ¿Estás COMPLETAMENTE seguro?',
                                    variant: 'danger',
                                    onConfirm: handleClearAllData
                                });
                            }}
                            variant="danger"
                            warning="Crítico - Operación irreversible. Se borrará TODO"
                        />

                        {/* ========== GRUPO 4: MONITOREO ========== */}
                        <RecentLogsCard
                            logs={recentLogs}
                            onLoad={handleLoadRecentLogs}
                            loading={loadingRecentLogs}
                        />

                        <TemplatesCard
                            templates={templates}
                            onLoad={handleLoadTemplates}
                            loading={loadingTemplates}
                        />
                    </div>
                </>
            )}

            <ConfirmationModal
                isOpen={confirmationModal.isOpen}
                title={confirmationModal.title}
                message={confirmationModal.message}
                variant={confirmationModal.variant}
                onConfirm={confirmationModal.onConfirm}
                onCancel={() => setConfirmationModal({ ...confirmationModal, isOpen: false })}
            />

            <JobProgressModal
                jobId={activeJobId}
                isOpen={isProgressOpen}
                onClose={() => setIsProgressOpen(false)}
                title="Procesando Terminal"
            />
        </div>
    );
}
