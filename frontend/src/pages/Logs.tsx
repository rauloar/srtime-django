import { useEffect, useState } from 'react';
import { getAttendanceLogs, getDevices, updateAttendanceLog } from '../api';
import type { Device, AttendanceLog } from '../api';
import { DataGrid, type Column } from '../components/ui/DataGrid';
import { Edit2, RefreshCw } from 'lucide-react';
import { useToast } from '../hooks/useToast';

export function Logs() {
    const [logs, setLogs] = useState<AttendanceLog[]>([]);
    const [loading, setLoading] = useState(false);
    const [devices, setDevices] = useState<Device[]>([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalCount, setTotalCount] = useState(0);
    const pageSize = 50;
    const totalPages = Math.ceil(totalCount / pageSize);
    
    // Edit Modal State
    const [editingLog, setEditingLog] = useState<AttendanceLog | null>(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editFormData, setEditFormData] = useState<Partial<AttendanceLog>>({});
    const [isSaving, setIsSaving] = useState(false);
    const [editError, setEditError] = useState<string | null>(null);
    const { error: showError } = useToast();
    
    const [filters, setFilters] = useState({
        device_id: '',
        employee_id: '',
        name: '',
        from_date: '',
        to_date: ''
    });

    const getDeviceName = (deviceId: number) => devices.find(d => d.id === deviceId)?.name || deviceId;

    useEffect(() => {
        getDevices().then(setDevices);
        loadLogs(1);
    }, []);

    const loadLogs = async (page: number = 1) => {
        try {
            setLoading(true);
            setCurrentPage(page);
            const params: any = { page, page_size: pageSize };
            if (filters.device_id) params.device_id = parseInt(filters.device_id);
            if (filters.employee_id) params.employee_id = parseInt(filters.employee_id);
            if (filters.from_date) params.from_date = new Date(filters.from_date).toISOString();
            if (filters.to_date) params.to_date = new Date(filters.to_date).toISOString();
            // Use search param for name (handled by backend via search_fields)
            if (filters.name) params.search = filters.name;

            const response = await getAttendanceLogs(params);
            setTotalCount(response.count);

            const data = response.results || [];
            // Backend now handles all filtering - no client-side filtering needed
            setLogs(data);
        } catch (e) {
            showError('No se pudieron cargar los registros');
        } finally {
            setLoading(false);
        }
    };

    const handleFilterChange = (key: string, value: string) => {
        setFilters(prev => ({ ...prev, [key]: value }));
    };

    const handleFilter = () => {
        setCurrentPage(1); // Reset to first page when filtering
        loadLogs(1);
    };

    const handleOpenEditModal = (log: AttendanceLog) => {
        setEditingLog(log);
        setEditFormData({
            timestamp: log.timestamp,
            punch: log.punch,
        });
        setEditError(null);
        setIsModalOpen(true);
    };

    const handleCloseModal = () => {
        setIsModalOpen(false);
        setEditingLog(null);
        setEditFormData({});
        setEditError(null);
    };

    const handleEditFormChange = (key: string, value: any) => {
        setEditFormData(prev => ({ ...prev, [key]: value }));
    };

    const handleSaveEdit = async () => {
        if (!editingLog) return;
        
        setIsSaving(true);
        setEditError(null);
        try {
            await updateAttendanceLog(editingLog.id, editFormData);
            // Refresh logs after update
            await loadLogs(currentPage);
            handleCloseModal();
        } catch (e: any) {
            setEditError(e.response?.data?.detail || "Error al guardar los cambios");
        } finally {
            setIsSaving(false);
        }
    };

    // Format Helpers
    const formatDate = (dateString: string) => {
        const d = new Date(dateString);
        // DD/MM/YY
        return d.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: '2-digit' });
    };

    const formatTime = (dateString: string) => {
        const d = new Date(dateString);
        // HH:MM
        return d.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', hour12: false });
    };

    const escapeHtml = (value: string) => value
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    const exportCsv = () => {
        const headers = ['ID', 'Dispositivo', 'Empleado', 'Fecha', 'Hora', 'Estado', 'Origen', 'Verificación'];
        const rows = logs.map(log => [
            log.id,
            getDeviceName(log.device_id),
            `${log.employee || '-'} | ${log.user_id} - ${log.user_name || '-'}`,
            formatDate(log.timestamp),
            formatTime(log.timestamp),
            log.status_label || `Estado ${log.status}`,
            log.punch_source || 'Terminal',
            log.verify_mode_label || '-'
        ]);

        const csvContent = [headers, ...rows]
            .map(row => row.map(value => '"' + String(value ?? '').replace(/"/g, '""') + '"').join(','))
            .join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `registros_asistencia_${new Date().toISOString().slice(0, 10)}.csv`;
        link.click();
        URL.revokeObjectURL(url);
    };

    const exportExcel = async () => {
        const XLSX = await import('xlsx');
        const headers = ['ID', 'Dispositivo', 'Empleado', 'Fecha', 'Hora', 'Estado', 'Origen', 'Verificación'];
        const rows = logs.map(log => [
            log.id,
            getDeviceName(log.device_id),
            `${log.employee || '-'} | ${log.user_id} - ${log.user_name || '-'}`,
            formatDate(log.timestamp),
            formatTime(log.timestamp),
            log.status_label || `Estado ${log.status}`,
            log.punch_source || 'Terminal',
            log.verify_mode_label || '-'
        ]);

        const worksheet = XLSX.utils.aoa_to_sheet([headers, ...rows]);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Registros');
        const buffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
        const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `registros_asistencia_${new Date().toISOString().slice(0, 10)}.xlsx`;
        link.click();
        URL.revokeObjectURL(url);
    };

    const printLogs = () => {
        const headers = ['ID', 'Dispositivo', 'Empleado', 'Fecha', 'Hora', 'Estado', 'Origen', 'Verificación'];
        const rowsHtml = logs.map(log => `
            <tr>
                <td>${escapeHtml(String(log.id ?? ''))}</td>
                <td>${escapeHtml(String(getDeviceName(log.device_id)))}</td>
                <td>${escapeHtml(`${String(log.employee ?? '-')} | ${String(log.user_id ?? '')} - ${String(log.user_name || '-')}`)}</td>
                <td>${escapeHtml(formatDate(log.timestamp))}</td>
                <td>${escapeHtml(formatTime(log.timestamp))}</td>
                <td>${escapeHtml(log.status_label || `Estado ${log.status}`)}</td>
                <td>${escapeHtml(String(log.punch_source || 'Terminal'))}</td>
                <td>${escapeHtml(log.verify_mode_label || '-')}</td>
            </tr>
        `).join('');

        const printWindow = window.open('', '_blank');
        if (!printWindow) return;

        printWindow.document.write(`<!DOCTYPE html>
            <html>
            <head>
                <title>Registros de Asistencia</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 16px; }
                    h2 { margin-top: 0; }
                    table { width: 100%; border-collapse: collapse; }
                    th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
                    th { background: #f5f5f5; }
                </style>
            </head>
            <body>
                <h2>Registros de Asistencia</h2>
                <table>
                    <thead>
                        <tr>${headers.map(h => `<th>${escapeHtml(h)}</th>`).join('')}</tr>
                    </thead>
                    <tbody>
                        ${rowsHtml || `<tr><td colspan="${headers.length}" style="text-align:center;">No hay registros</td></tr>`}
                    </tbody>
                </table>
            </body>
            </html>`);

        printWindow.document.close();
        printWindow.focus();
        printWindow.print();
        printWindow.close();
    };

    const columns: Column<AttendanceLog>[] = [
        { field: 'id', header: 'ID', width: '90px' },
        { field: 'device_id', header: 'Dispositivo', render: log => getDeviceName(log.device_id) },
        { 
            field: 'employee',
            header: 'Empleado',
            width: '180px',
            render: log => (
                <div style={{ fontSize: '14px' }}>
                    <div style={{ fontWeight: 500 }}>#{log.employee ?? '-'} · {log.user_id}</div>
                    <small style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{log.user_name || '-'}</small>
                </div>
            )
        },
        { field: 'timestamp', header: 'Fecha', width: '120px', render: log => formatDate(log.timestamp) },
        { field: 'timestamp', header: 'Hora', width: '100px', render: log => formatTime(log.timestamp) },
        { field: 'status', header: 'Estado', render: log => log.status_label || `Estado ${log.status}` },
        { field: 'punch_source', header: 'Origen', render: log => log.punch_source || 'Terminal' },
        { field: 'verify_mode', header: 'Verificación', render: log => log.verify_mode_label || '-' },
        { 
            field: 'actions', 
            header: 'Acciones', 
            width: '80px', 
            render: log => (
                <button 
                    className="primary" 
                    style={{ padding: '4px 8px', fontSize: '12px' }}
                    onClick={() => handleOpenEditModal(log)}
                    title="Editar registro"
                >
                    <Edit2 size={14} />
                </button>
            )
        }
    ];

    return (
        <div>
            <h1>Registros de Asistencia</h1>

            {/* Filters - Row 1: Main filters */}
            <div className="card" style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'end' }}>
                <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: '500' }}>Dispositivo</label>
                    <select value={filters.device_id} onChange={e => handleFilterChange('device_id', e.target.value)}>
                        <option value="">Todos</option>
                        {devices.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
                    </select>
                </div>
                <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: '500' }}>Employee ID</label>
                    <input 
                        type="text" 
                        value={filters.employee_id} 
                        onChange={e => handleFilterChange('employee_id', e.target.value)} 
                        placeholder="ej: 123"
                        style={{ width: '120px' }} 
                    />
                </div>
                <div style={{ flex: 1, minWidth: '180px' }}>
                    <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: '500' }}>Nombre/Búsqueda</label>
                    <input 
                        type="text" 
                        value={filters.name} 
                        onChange={e => handleFilterChange('name', e.target.value)} 
                        placeholder="Buscar por nombre..." 
                    />
                </div>
                <button className="primary" onClick={handleFilter}>Filtrar</button>
                <button onClick={() => {
                    setFilters({ device_id: '', employee_id: '', name: '', from_date: '', to_date: '' });
                    loadLogs(1);
                }}>Limpiar</button>
            </div>

            {/* Filters - Row 2: Date range filters */}
            <div className="card" style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'end', backgroundColor: 'var(--bg-card)' }}>
                <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: '500' }}>Fecha Desde</label>
                    <input 
                        type="date" 
                        value={filters.from_date} 
                        onChange={e => handleFilterChange('from_date', e.target.value)} 
                    />
                </div>
                <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: '500' }}>Fecha Hasta</label>
                    <input 
                        type="date" 
                        value={filters.to_date} 
                        onChange={e => handleFilterChange('to_date', e.target.value)} 
                    />
                </div>
                <button className="primary" onClick={handleFilter}>Aplicar Rango</button>
                <div style={{ marginLeft: 'auto', display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
                    <button onClick={() => loadLogs(currentPage)} disabled={loading} title="Recargar registros">
                        <RefreshCw size={16} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
                    </button>
                    <button onClick={exportCsv}>📥 Exportar CSV</button>
                    <button onClick={exportExcel}>📊 Exportar Excel</button>
                    <button onClick={printLogs}>🖨️ Imprimir</button>
                </div>
            </div>

            <div className="card" style={{ padding: 0 }}>
                <DataGrid
                    columns={columns}
                    data={logs}
                    loading={loading}
                    placeholder="No hay registros. (Verifique filtros)"
                />
            </div>

            {/* Pagination Controls */}
            <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    Página <strong>{currentPage}</strong> de <strong>{totalPages || 1}</strong> | Total: <strong>{totalCount}</strong> registros
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                    <button 
                        onClick={() => loadLogs(1)} 
                        disabled={currentPage === 1 || loading}
                    >
                        Primera
                    </button>
                    <button 
                        onClick={() => loadLogs(currentPage - 1)} 
                        disabled={currentPage === 1 || loading}
                    >
                        Anterior
                    </button>
                    <button 
                        onClick={() => loadLogs(currentPage + 1)} 
                        disabled={currentPage >= totalPages || loading}
                    >
                        Siguiente
                    </button>
                    <button 
                        onClick={() => loadLogs(totalPages)} 
                        disabled={currentPage >= totalPages || loading}
                    >
                        Última
                    </button>
                </div>
            </div>

            {/* Edit Modal */}
            {isModalOpen && editingLog && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'rgba(0, 0, 0, 0.5)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 1000
                }}>
                    <div className="card" style={{ maxWidth: '500px', width: '90%', maxHeight: '80vh', overflow: 'auto' }}>
                        <h3>Editar Registro (ID: {editingLog.id})</h3>
                        
                        <div style={{ display: 'grid', gap: '15px', marginTop: '15px' }}>
                            {/* Read-only info */}
                            <div>
                                <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>Dispositivo</label>
                                <input 
                                    type="text" 
                                    value={getDeviceName(editingLog.device_id)} 
                                    disabled 
                                    className="form-control"
                                    style={{ opacity: 0.6 }}
                                />
                            </div>

                            <div>
                                <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>Usuario</label>
                                <input 
                                    type="text" 
                                    value={`${editingLog.user_id} - ${editingLog.user_name || 'N/A'}`} 
                                    disabled 
                                    className="form-control"
                                    style={{ opacity: 0.6 }}
                                />
                            </div>

                            {/* Editable fields */}
                            <div>
                                <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>Fecha y Hora</label>
                                <input 
                                    type="datetime-local" 
                                    value={editFormData.timestamp ? new Date(editFormData.timestamp).toISOString().slice(0, 16) : ''}
                                    onChange={e => {
                                        const dt = new Date(e.target.value);
                                        handleEditFormChange('timestamp', dt.toISOString());
                                    }}
                                    className="form-control"
                                />
                            </div>

                            <div>
                                <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>Tipo (Punch)</label>
                                <select 
                                    value={editFormData.punch || 0}
                                    onChange={e => handleEditFormChange('punch', parseInt(e.target.value))}
                                    className="form-control"
                                >
                                    <option value={0}>Entrada/Salida (Auto)</option>
                                    <option value={1}>Entrada</option>
                                    <option value={2}>Salida</option>
                                </select>
                            </div>

                            {editError && (
                                <div style={{ 
                                    background: '#ffebee', 
                                    color: '#c62828', 
                                    padding: '10px', 
                                    borderRadius: '4px', 
                                    fontSize: '14px' 
                                }}>
                                    <strong>Error:</strong> {editError}
                                </div>
                            )}

                            {/* Buttons */}
                            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '10px' }}>
                                <button 
                                    onClick={handleCloseModal}
                                    disabled={isSaving}
                                >
                                    Cancelar
                                </button>
                                <button 
                                    className="primary"
                                    onClick={handleSaveEdit}
                                    disabled={isSaving}
                                >
                                    {isSaving ? 'Guardando...' : 'Guardar'}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
