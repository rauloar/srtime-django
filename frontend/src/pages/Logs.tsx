import { useEffect, useState } from 'react';
import { getAttendanceLogs, getDevices } from '../api';
import type { Device, AttendanceLog } from '../api';
import { DataGrid, type Column } from '../components/ui/DataGrid';

export function Logs() {
    const [logs, setLogs] = useState<AttendanceLog[]>([]);
    const [loading, setLoading] = useState(false);
    const [devices, setDevices] = useState<Device[]>([]);
    const [filters, setFilters] = useState({
        device_id: '',
        user_id: '',
        name: '',
        from_date: '',
        to_date: ''
    });

    const getDeviceName = (deviceId: number) => devices.find(d => d.id === deviceId)?.name || deviceId;

    useEffect(() => {
        getDevices().then(setDevices);
        loadLogs();
    }, []);

    const loadLogs = async () => {
        try {
            setLoading(true);
            const params: any = {};
            if (filters.device_id) params.device_id = parseInt(filters.device_id);
            if (filters.user_id) params.user_id = filters.user_id;
            if (filters.from_date) params.from_date = new Date(filters.from_date).toISOString();
            if (filters.to_date) params.to_date = new Date(filters.to_date).toISOString();

            let data = await getAttendanceLogs(params);

            // Client-side filtering for Name (since backend doesn't support it yet)
            if (filters.name) {
                const search = filters.name.toLowerCase();
                data = data.filter(log => (log.user_name || '').toLowerCase().includes(search));
            }
            setLogs(data);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const handleFilterChange = (key: string, value: string) => {
        setFilters(prev => ({ ...prev, [key]: value }));
    };

    const getStatusLabel = (status: number) => {
        switch (status) {
            case 0: return 'Entrada';
            case 1: return 'Salida';
            case 2: return 'Inicio Descanso';
            case 3: return 'Fin Descanso';
            case 4: return 'Inicio Horas Extras';
            case 5: return 'Fin Horas Extras';
            default: return `Estado ${status}`;
        }
    };

    const getVerifyModeLabel = (mode?: number) => {
        if (mode === undefined || mode === null) return '-';
        switch (mode) {
            case 1: return 'Huella';
            case 3: return 'Contraseña';
            case 4: return 'Tarjeta';
            case 15: return 'Rostro';
            case 25: return 'Palma'; // Common generic code
            default: return `Modo ${mode}`;
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
        const headers = ['ID', 'Dispositivo', 'Usuario', 'Nombre', 'Fecha', 'Hora', 'Estado', 'Origen', 'Verificación'];
        const rows = logs.map(log => [
            log.id,
            getDeviceName(log.device_id),
            log.user_id,
            log.user_name || '-',
            formatDate(log.timestamp),
            formatTime(log.timestamp),
            getStatusLabel(log.status),
            log.punch_source || 'Terminal',
            getVerifyModeLabel(log.verify_mode)
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
        const headers = ['ID', 'Dispositivo', 'Usuario', 'Nombre', 'Fecha', 'Hora', 'Estado', 'Origen', 'Verificación'];
        const rows = logs.map(log => [
            log.id,
            getDeviceName(log.device_id),
            log.user_id,
            log.user_name || '-',
            formatDate(log.timestamp),
            formatTime(log.timestamp),
            getStatusLabel(log.status),
            log.punch_source || 'Terminal',
            getVerifyModeLabel(log.verify_mode)
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
        const headers = ['ID', 'Dispositivo', 'Usuario', 'Nombre', 'Fecha', 'Hora', 'Estado', 'Origen', 'Verificación'];
        const rowsHtml = logs.map(log => `
            <tr>
                <td>${escapeHtml(String(log.id ?? ''))}</td>
                <td>${escapeHtml(String(getDeviceName(log.device_id)))}</td>
                <td>${escapeHtml(String(log.user_id ?? ''))}</td>
                <td>${escapeHtml(String(log.user_name || '-'))}</td>
                <td>${escapeHtml(formatDate(log.timestamp))}</td>
                <td>${escapeHtml(formatTime(log.timestamp))}</td>
                <td>${escapeHtml(getStatusLabel(log.status))}</td>
                <td>${escapeHtml(String(log.punch_source || 'Terminal'))}</td>
                <td>${escapeHtml(getVerifyModeLabel(log.verify_mode))}</td>
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
        { field: 'user_id', header: 'Usuario', width: '120px' },
        { field: 'user_name', header: 'Nombre', render: log => log.user_name || '-' },
        { field: 'timestamp', header: 'Fecha', width: '120px', render: log => formatDate(log.timestamp) },
        { field: 'timestamp', header: 'Hora', width: '100px', render: log => formatTime(log.timestamp) },
        { field: 'status', header: 'Estado', render: log => getStatusLabel(log.status) },
        { field: 'punch_source', header: 'Origen', render: log => log.punch_source || 'Terminal' },
        { field: 'verify_mode', header: 'Verificación', render: log => getVerifyModeLabel(log.verify_mode) }
    ];

    return (
        <div>
            <h1>Registros de Asistencia</h1>

            <div className="card" style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'end' }}>
                <div>
                    <label style={{ display: 'block', marginBottom: '5px' }}>Dispositivo</label>
                    <select value={filters.device_id} onChange={e => handleFilterChange('device_id', e.target.value)}>
                        <option value="">Todos</option>
                        {devices.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
                    </select>
                </div>
                <div>
                    <label style={{ display: 'block', marginBottom: '5px' }}>User ID</label>
                    <input type="text" value={filters.user_id} onChange={e => handleFilterChange('user_id', e.target.value)} style={{ width: '100px' }} />
                </div>
                <div>
                    <label style={{ display: 'block', marginBottom: '5px' }}>Nombre</label>
                    <input type="text" value={filters.name} onChange={e => handleFilterChange('name', e.target.value)} placeholder="Buscar..." />
                </div>
                <div>
                    <label style={{ display: 'block', marginBottom: '5px' }}>Desde</label>
                    <input type="date" value={filters.from_date} onChange={e => handleFilterChange('from_date', e.target.value)} />
                </div>
                <div>
                    <label style={{ display: 'block', marginBottom: '5px' }}>Hasta</label>
                    <input type="date" value={filters.to_date} onChange={e => handleFilterChange('to_date', e.target.value)} />
                </div>
                <button className="primary" onClick={loadLogs}>Filtrar</button>
                <div style={{ marginLeft: 'auto', display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
                    <button onClick={exportCsv}>Exportar CSV</button>
                    <button onClick={exportExcel}>Exportar Excel</button>
                    <button onClick={printLogs}>Imprimir</button>
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
        </div>
    );
}
