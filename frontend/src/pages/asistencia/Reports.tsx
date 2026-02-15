
import React, { useState, useEffect } from 'react';
import { 
    getDailyReportsV2, getDepartments, calculateAttendance, 
    type DailyAttendanceV2, 
    type Department 
} from '../../api';
import { DataGrid, type Column } from '../../components/ui/DataGrid';
import { Download, Play, CheckCircle, AlertCircle } from 'lucide-react';
import { Building, Clock, UserX, UserCheck } from 'lucide-react';

export const Reports: React.FC = () => {
    // ========================================================================
    // STATE
    // ========================================================================
    
    const today = new Date();
    const lastWeek = new Date(today);
    lastWeek.setDate(today.getDate() - 6);

    const [startDate, setStartDate] = useState(lastWeek.toISOString().split('T')[0]);
    const [endDate, setEndDate] = useState(today.toISOString().split('T')[0]);
    const [departmentId, setDepartmentId] = useState<string>("");
    const [departments, setDepartments] = useState<Department[]>([]);
    const [data, setData] = useState<DailyAttendanceV2[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [userIdFilter, setUserIdFilter] = useState('');
    const [nameFilter, setNameFilter] = useState('');

    // Calculation State
    const [calculating, setCalculating] = useState(false);
    const [calcResult, setCalcResult] = useState<{ count: number; message: string } | null>(null);
    const [calcError, setCalcError] = useState<string | null>(null);

    // ========================================================================
    // LIFECYCLE
    // ========================================================================

    useEffect(() => {
        getDepartments().then(setDepartments).catch(() => setDepartments([]));
    }, []);

    useEffect(() => {
        fetchData();
    }, []);

    // ========================================================================
    // HANDLERS
    // ========================================================================

    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await getDailyReportsV2(
                startDate, 
                endDate, 
                departmentId ? parseInt(departmentId) : undefined,
                userIdFilter,
                nameFilter
            );
            
            if (!Array.isArray(res)) {
                setData([]);
                setError('No se pudieron cargar los reportes');
                return;
            }
            
            // SORT: por departmento luego por fecha
            res.sort((a, b) => 
                (a.employee.department_name || '').localeCompare(b.employee.department_name || '') 
                || a.identity.date.localeCompare(b.identity.date)
            );
            
            setData(res);
        } catch (e) {
            setData([]);
            setError('No se pudieron cargar los reportes');
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
            // Refetch dopo cálculo
            setTimeout(() => fetchData(), 500);
        } catch (e: any) {
            setCalcError(e.response?.data?.detail || "Cálculo fallido");
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

    // ========================================================================
    // COLUMNS - V2 STRUCTURE
    // ========================================================================

    const columns: Column<DailyAttendanceV2>[] = [
        {
            field: 'identity.date',
            header: 'Fecha',
            width: '100px',
            render: (r) => r.identity.date
        },
        {
            field: 'employee',
            header: 'Empleado',
            render: (r) => (
                <div style={{ fontSize: '14px' }}>
                    <div style={{ fontWeight: 500 }}>{r.employee.user_id}</div>
                    <small style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                        {r.employee.name}
                    </small>
                </div>
            )
        },
        {
            field: 'schedule',
            header: 'Entrada / Salida',
            render: (r) => {
                const fmt = (iso?: string | null) => {
                    if (!iso) return '--:--';
                    const dt = new Date(iso);
                    return dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
                };
                return (
                    <div style={{ fontSize: '13px' }}>
                        <span style={{ color: r.schedule.check_in ? 'inherit' : 'var(--text-muted)' }}>
                            In: {fmt(r.schedule.check_in)}
                        </span>{' '}
                        <br/>
                        <span style={{ color: r.schedule.check_out ? 'inherit' : 'var(--text-muted)' }}>
                            Out: {fmt(r.schedule.check_out)}
                        </span>
                    </div>
                );
            }
        },
        {
            field: 'status',
            header: 'Estado',
            render: (r) => (
                <div className="flex-col gap-1">
                    <span 
                        style={{ 
                            color: 'white', 
                            background: r.status.color, 
                            padding: '2px 8px', 
                            borderRadius: '12px', 
                            fontSize: '11px', 
                            fontWeight: 500, 
                            textAlign: 'center' 
                        }}
                    >
                        {r.status.label}
                    </span>
                </div>
            )
        },
        {
            field: 'metrics',
            header: 'Detalle',
            align: 'right',
            width: '140px',
            render: (r) => (
                <div style={{ fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '2px' }}>
                    {/* DOMINIO V2: NO usar ?? defensivas (backend garantiza) */}
                    {r.metrics.worked_minutes > 0 && (
                        <span>
                            Trab: {Math.floor(r.metrics.worked_minutes / 60)}h {r.metrics.worked_minutes % 60}m
                        </span>
                    )}
                    {r.metrics.overtime_minutes > 0 && (
                        <span style={{ color: 'var(--att-overtime)' }}>
                            Extra: {Math.floor(r.metrics.overtime_minutes / 60)}h {r.metrics.overtime_minutes % 60}m
                        </span>
                    )}
                    {r.metrics.late_minutes > 0 && (
                        <span style={{ color: 'var(--att-late)' }}>
                            Tarde: {r.metrics.late_minutes}m
                        </span>
                    )}
                    {r.metrics.early_minutes > 0 && (
                        <span style={{ color: 'var(--att-early)' }}>
                            Salida: {r.metrics.early_minutes}m
                        </span>
                    )}
                </div>
            )
        }
    ];

    // ========================================================================
    // GROUPING - por departamento
    // ========================================================================

    const groups = React.useMemo(() => {
        const g: { [key: string]: DailyAttendanceV2[] } = {};
        data.forEach(item => {
            const deptName = item.employee.department_name || 'Sin Departamento';
            if (!g[deptName]) g[deptName] = [];
            g[deptName].push(item);
        });
        return g;
    }, [data]);

    // ========================================================================
    // RENDER
    // ========================================================================

    return (
        <div className="flex-col gap-4" style={{ height: '100%', overflow: 'hidden' }}>
            {error && (
                <div className="card" style={{ padding: '12px', background: 'var(--bg-card)', color: 'var(--text-secondary)' }}>
                    ⚠️ {error}
                </div>
            )}
            <div className="flex-row space-between wrap">
                <h2>Reporte Diario (V2 - Dominio Fuerte)</h2>
                <div className="card" style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'end' }}>
                    <div>
                        <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: 500 }}>Desde</label>
                        <input 
                            type="date" 
                            value={startDate} 
                            onChange={e => setStartDate(e.target.value)} 
                            className="form-control"
                        />
                    </div>
                    <div>
                        <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: 500 }}>Hasta</label>
                        <input 
                            type="date" 
                            value={endDate} 
                            onChange={e => setEndDate(e.target.value)} 
                            className="form-control"
                        />
                    </div>
                    <div>
                        <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: 500 }}>Departamento</label>
                        <select 
                            className="form-control" 
                            value={departmentId} 
                            onChange={e => setDepartmentId(e.target.value)}
                        >
                            <option value="">Todos</option>
                            {departments.map(d => (
                                <option key={d.id} value={d.id}>{d.name}</option>
                            ))}
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
                        <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: 500 }}>Nombre</label>
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
                    <button 
                        className="primary" 
                        onClick={handleCalculate} 
                        disabled={calculating}
                        title="Procesar marcaciones y generar reportes diarios"
                    >
                        {calculating ? "Calculando..." : <><Play size={16} style={{ marginRight: '4px' }} /> Calcular</>}
                    </button>
                    <button className="secondary" title="Exportar (TBD)">
                        <Download size={16} />
                    </button>
                </div>
            </div>

            {/* CONTENT */}
            <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '20px', paddingRight: '5px' }}>
                {/* Calculation Success */}
                {calcResult && (
                    <div style={{ background: '#e8f5e9', color: '#2e7d32', padding: '15px', borderRadius: '4px', display: 'flex', gap: '10px', alignItems: 'center' }}>
                        <CheckCircle size={20} />
                        <div>
                            <strong>Cálculo Completado</strong><br />
                            {calcResult.message}
                        </div>
                    </div>
                )}

                {/* Calculation Error */}
                {calcError && (
                    <div style={{ background: '#ffebee', color: '#c62828', padding: '15px', borderRadius: '4px', display: 'flex', gap: '10px', alignItems: 'center' }}>
                        <AlertCircle size={20} />
                        <div>
                            <strong>Error</strong><br />
                            {calcError}
                        </div>
                    </div>
                )}

                {/* Loading */}
                {loading && <div style={{ padding: '20px', textAlign: 'center' }}>Cargando datos...</div>}

                {/* Empty State */}
                {!loading && Object.keys(groups).length === 0 && (
                    <div style={{ padding: '40px', textAlign: 'center', color: '#888', background: 'var(--bg-card)', borderRadius: '8px' }}>
                        No hay registros para mostrar en este periodo.
                    </div>
                )}

                {/* Department Groups */}
                {!loading && Object.entries(groups).map(([deptName, items]) => {
                    // AGREGACIONES V2: NO usar ?? defensivas (backend garantiza)
                    const totalAbsent = items.filter(i => i.status.code === 'ABSENT').length;
                    const totalPresent = items.filter(i => 
                        ['NORMAL', 'LATE', 'EARLY', 'PARTIAL'].includes(i.status.code)
                    ).length;
                    
                    // SUMA: directa (sin ??)
                    const totalMinutes = items.reduce((acc, curr) => 
                        acc + curr.metrics.worked_minutes, 0
                    );
                    const totalHours = (totalMinutes / 60).toFixed(1);

                    return (
                        <div 
                            key={deptName} 
                            className="card" 
                            style={{ padding: '0', overflow: 'hidden', border: '1px solid var(--border-color)' }}
                        >
                            {/* Department Header */}
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
                                    <span style={{ fontSize: '12px', fontWeight: 'normal', opacity: 0.7 }}>
                                        ({items.length} regs)
                                    </span>
                                </div>
                                <div style={{ display: 'flex', gap: '20px', fontSize: '13px' }}>
                                    <div 
                                        style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--att-normal)' }} 
                                        title="Presentismo"
                                    >
                                        <UserCheck size={16} /> Presentes: <b>{totalPresent}</b>
                                    </div>
                                    <div 
                                        style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--att-absent)' }} 
                                        title="Ausentismo"
                                    >
                                        <UserX size={16} /> Ausentes: <b>{totalAbsent}</b>
                                    </div>
                                    <div 
                                        style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--att-rest-day)' }} 
                                        title="Horas Trabajadas"
                                    >
                                        <Clock size={16} /> Horas: <b>{totalHours}h</b>
                                    </div>
                                </div>
                            </div>

                            {/* DataGrid */}
                            <DataGrid<DailyAttendanceV2>
                                columns={columns}
                                data={items}
                                loading={false}
                                placeholder="Sin datos"
                                getRowId={(row) => row.identity.id}
                            />
                        </div>
                    );
                })}
            </div>
        </div>
    );
};
