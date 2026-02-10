
import React, { useState, useEffect } from 'react';
import { getDailyReports, getDepartments, calculateAttendance, type DailyAttendance, type Department } from '../../api';
import { DataGrid, type Column } from '../../components/ui/DataGrid';
import { Download, Play, CheckCircle, AlertCircle } from 'lucide-react';

// ... imports
import { Building, Clock, UserX, UserCheck } from 'lucide-react';

export const Reports: React.FC = () => {
    // ... state (dates, departments, etc) - Keep existing
    const today = new Date();
    const lastWeek = new Date(today);
    lastWeek.setDate(today.getDate() - 6);

    const [startDate, setStartDate] = useState(lastWeek.toISOString().split('T')[0]);
    const [endDate, setEndDate] = useState(today.toISOString().split('T')[0]);

    const [departmentId, setDepartmentId] = useState<string>("");
    const [departments, setDepartments] = useState<Department[]>([]);

    const [data, setData] = useState<DailyAttendance[]>([]);
    const [loading, setLoading] = useState(false);
    const [userIdFilter, setUserIdFilter] = useState('');
    const [nameFilter, setNameFilter] = useState('');

    // Calculation State
    const [calculating, setCalculating] = useState(false);
    const [calcResult, setCalcResult] = useState<{ count: number; message: string } | null>(null);
    const [calcError, setCalcError] = useState<string | null>(null);

    // Grouping State
    // No explicit state needed if we compute on render, but memo is better

    useEffect(() => {
        getDepartments().then(setDepartments).catch(console.error);
    }, []);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        setLoading(true);
        try {
            // Pass filters directly to backend (no client-side filtering needed)
            const res = await getDailyReports(
                startDate, 
                endDate, 
                departmentId ? parseInt(departmentId) : undefined,
                userIdFilter,
                nameFilter
            );
            // Sort by Department then Date
            res.sort((a, b) => (a.employee?.department_name || '').localeCompare(b.employee?.department_name || '') || a.date.localeCompare(b.date));
            setData(res);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const handleFilter = () => {
        fetchData();
    };

    const handleCalculate = async () => {
        setCalculating(true);
        setCalcResult(null);
        setCalcError(null);
        try {
            const res = await calculateAttendance(
                startDate, 
                endDate, 
                departmentId ? parseInt(departmentId) : undefined
            );
            setCalcResult(res);
            // Refresh data after calculation
            setTimeout(() => fetchData(), 500);
        } catch (e: any) {
            setCalcError(e.response?.data?.detail || "Calculation failed");
        } finally {
            setCalculating(false);
        }
    };

    const handleClear = () => {
        const todayLocal = new Date();
        const lastWeekLocal = new Date(todayLocal);
        lastWeekLocal.setDate(todayLocal.getDate() - 6);
        setStartDate(lastWeekLocal.toISOString().split('T')[0]);
        setEndDate(todayLocal.toISOString().split('T')[0]);
        setDepartmentId('');
        setUserIdFilter('');
        setNameFilter('');
        fetchData();
    };

    // Columns Definition (Generic for all groups)
    const columns: Column<DailyAttendance>[] = [
        { field: 'date', header: 'Fecha', width: '100px' },
        {
            field: 'employee',
            header: 'Empleado',
            render: (r) => (
                <div style={{ fontSize: '14px' }}>
                    <div style={{ fontWeight: 500 }}>{r.employee_user_id || r.employee_id}</div>
                    <small style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{r.employee_name || '-'}</small>
                </div>
            )
        },
        {
            field: 'times',
            header: 'Entrada / Salida',
            render: (r) => {
                const fmt = (d?: string) => d ? new Date(d).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }) : '--:--';
                return (
                    <div style={{ fontSize: '13px' }}>
                        <span style={{ color: r.check_in ? 'inherit' : '#999' }}>In: {fmt(r.check_in)}</span> <br />
                        <span style={{ color: r.check_out ? 'inherit' : '#999' }}>Out: {fmt(r.check_out)}</span>
                    </div>
                );
            }
        },
        {
            field: 'status',
            header: 'Estado',
            render: (r) => {
                // Use backend-provided color info if available, fallback to CSS variables
                const statusInfo = r.status_info;
                let color = 'var(--text-secondary)';
                
                if (statusInfo?.color) {
                    color = statusInfo.color;
                } else {
                    // Fallback to CSS variable mapping for backward compatibility
                    if (r.status === 'Normal') color = 'var(--att-normal)';
                    else if (r.status === 'Absent') color = 'var(--att-absent)';
                    else if (r.status === 'Late') color = 'var(--att-late)';
                    else if (r.status === 'Early') color = 'var(--att-early)';
                    else if (r.status === 'Partial') color = 'var(--att-partial)';
                    else if (r.status === 'Rest Day') color = 'var(--att-rest-day)';
                }

                return (
                    <div className="flex-col gap-1">
                        <span style={{ color: 'white', background: color, padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 500, textAlign: 'center' }}>
                            {r.status}
                        </span>
                        {r.exception_reason && (
                            <span style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '2px' }}>
                                {r.exception_reason}
                            </span>
                        )}
                    </div>
                );
            }
        },
        {
            field: 'stats',
            header: 'Detalle', // Renamed from Minutos to match content
            align: 'right',
            width: '140px',
            render: (r) => (
                <div style={{ fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '2px' }}>
                    {r.worked_minutes > 0 && <span>Work: {Math.floor(r.worked_minutes / 60)}h {r.worked_minutes % 60}m</span>}
                    {r.overtime_minutes > 0 && <span style={{ color: 'var(--att-overtime)' }}>OT: {Math.floor(r.overtime_minutes / 60)}h {r.overtime_minutes % 60}m</span>}
                    {r.late_minutes > 0 && <span style={{ color: 'var(--att-late)' }}>Late: {r.late_minutes}m</span>}
                    {r.early_minutes > 0 && <span style={{ color: 'var(--att-early)' }}>Early: {r.early_minutes}m</span>}
                </div>
            )
        }
    ];

    // Backend now handles all filtering - no client-side filtering needed
    const filteredData = React.useMemo(() => {
        // All filtering is done on backend now, just return data as-is
        return data;
    }, [data]);

    const groups = React.useMemo(() => {
        const g: { [key: string]: DailyAttendance[] } = {};
        filteredData.forEach(item => {
            const deptName = item.employee?.department_name || 'Sin Departamento';
            if (!g[deptName]) g[deptName] = [];
            g[deptName].push(item);
        });
        return g;
    }, [filteredData]);

    return (
        <div className="flex-col gap-4" style={{ height: '100%', overflow: 'hidden' }}>
            <div className="flex-row space-between wrap">
                <h2>Reporte Diario</h2>
                <div className="card" style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'end' }}>
                    <div>
                        <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: 500 }}>Desde</label>
                        <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} className="form-control" />
                    </div>
                    <div>
                        <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: 500 }}>Hasta</label>
                        <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} className="form-control" />
                    </div>
                    <div>
                        <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: 500 }}>Departamento</label>
                        <select className="form-control" value={departmentId} onChange={e => setDepartmentId(e.target.value)}>
                            <option value="">Todos</option>
                            {departments.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
                        </select>
                    </div>
                    <div>
                        <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: 500 }}>User ID</label>
                        <input
                            type="text"
                            placeholder="ej: EMP003"
                            value={userIdFilter}
                            onChange={e => setUserIdFilter(e.target.value)}
                            style={{ width: '120px' }}
                            className="form-control"
                        />
                    </div>
                    <div style={{ flex: '1 1 0%', minWidth: '180px' }}>
                        <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: 500 }}>Nombre/Búsqueda</label>
                        <input
                            type="text"
                            placeholder="Buscar por nombre..."
                            value={nameFilter}
                            onChange={e => setNameFilter(e.target.value)}
                            className="form-control"
                        />
                    </div>
                    <button className="primary" onClick={handleFilter}>Filtrar</button>
                    <button onClick={handleClear}>Limpiar</button>
                    <button className="primary" onClick={handleCalculate} disabled={calculating} title="Procesar marcaciones y generar reportes diarios">
                        {calculating ? "Calculando..." : <><Play size={16} style={{ marginRight: '4px' }} /> Calcular</>}
                    </button>
                    <button className="secondary" title="Exportar (TBD)">
                        <Download size={16} />
                    </button>
                </div>
            </div>

            <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '20px', paddingRight: '5px' }}>
                {calcResult && (
                    <div style={{ background: '#e8f5e9', color: '#2e7d32', padding: '15px', borderRadius: '4px', display: 'flex', gap: '10px', alignItems: 'center' }}>
                        <CheckCircle size={20} />
                        <div>
                            <strong>Cálculo Completado</strong><br />
                            {calcResult.message}
                        </div>
                    </div>
                )}

                {calcError && (
                    <div style={{ background: '#ffebee', color: '#c62828', padding: '15px', borderRadius: '4px', display: 'flex', gap: '10px', alignItems: 'center' }}>
                        <AlertCircle size={20} />
                        <div>
                            <strong>Error</strong><br />
                            {calcError}
                        </div>
                    </div>
                )}

                {loading && <div style={{ padding: '20px', textAlign: 'center' }}>Cargando datos...</div>}

                {!loading && Object.keys(groups).length === 0 && (
                    <div style={{ padding: '40px', textAlign: 'center', color: '#888', background: 'var(--bg-card)', borderRadius: '8px' }}>
                        No hay registros para mostrar en este periodo.
                    </div>
                )}

                {!loading && Object.entries(groups).map(([deptName, items]) => {
                    // Calculate Summaries for this Department
                    const totalAbsent = items.filter(i => i.status === 'Absent').length;
                    const totalPresent = items.filter(i => ['Normal', 'Late', 'Early', 'Partial'].includes(i.status)).length;
                    const totalMinutes = items.reduce((acc, curr) => acc + curr.worked_minutes, 0);
                    const totalHours = (totalMinutes / 60).toFixed(1);

                    return (
                        <div key={deptName} className="card" style={{ padding: '0', overflow: 'hidden', border: '1px solid var(--border-color)' }}>
                            <div style={{
                                padding: '15px 20px',
                                background: 'var(--bg-secondary)',
                                borderBottom: '1px solid var(--border-color)',
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center'
                            }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontWeight: 600, fontSize: '16px' }}>
                                    <Building size={18} />
                                    {deptName}
                                    <span style={{ fontSize: '12px', fontWeight: 'normal', opacity: 0.7 }}>({items.length} regs)</span>
                                </div>
                                <div style={{ display: 'flex', gap: '20px', fontSize: '13px' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--att-normal)' }} title="Presentismo">
                                        <UserCheck size={16} /> Presentes: <b>{totalPresent}</b>
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--att-absent)' }} title="Ausentismo">
                                        <UserX size={16} /> Ausentes: <b>{totalAbsent}</b>
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--att-rest-day)' }} title="Horas Trabajadas">
                                        <Clock size={16} /> Horas: <b>{totalHours}h</b>
                                    </div>
                                </div>
                            </div>

                            <DataGrid
                                columns={columns}
                                data={items}
                                loading={false}
                                placeholder="Sin datos"
                            />
                        </div>
                    );
                })}
            </div>
        </div>
    );
};
