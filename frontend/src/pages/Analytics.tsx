import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Server, Users, Clock, AlertTriangle, Activity, UserPlus, FileText } from 'lucide-react';
import { getDevices, getAttendanceLogs } from '../api';

export const Analytics: React.FC = () => {
    const [stats, setStats] = useState({
        devicesTotal: 0,
        devicesOnline: 0,
        employeesTotal: 154, // Mock for now
        todayAtt: 0,
        abnormal: 3
    });

    useEffect(() => {
        const fetchData = async () => {
            try {
                const devs = await getDevices();
                const logs = await getAttendanceLogs({}); // Get recent logs

                // Calculate stats
                const today = new Date().toISOString().split('T')[0];
                const todayLogs = logs.filter(l => l.timestamp.startsWith(today));

                setStats(prev => ({
                    ...prev,
                    devicesTotal: devs.length,
                    devicesOnline: devs.filter((d: any) => d.last_seen).length, // simplified logic
                    todayAtt: todayLogs.length
                }));
            } catch (e) {
                console.error(e);
            }
        };
        fetchData();
    }, []);

    return (
        <div className="flex-col gap-4">
            <div className="flex-row space-between">
                <h2 style={{ fontSize: '20px', fontWeight: 600, color: 'var(--text-main)' }}>Tablero General</h2>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                    Última actualización: {new Date().toLocaleTimeString()}
                </div>
            </div>

            {/* Top Stats Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px' }}>
                <StatCard
                    title="Dispositivos"
                    value={stats.devicesTotal}
                    subtext={`${stats.devicesOnline} En Línea`}
                    icon={<Server size={24} />}
                    color="var(--primary)"
                    bg="rgba(65, 144, 247, 0.1)"
                />
                <StatCard
                    title="Empleados"
                    value={stats.employeesTotal}
                    subtext="Activos"
                    icon={<Users size={24} />}
                    color="var(--status-ok)"
                    bg="rgba(76, 202, 187, 0.1)"
                />
                <StatCard
                    title="Asistencias Hoy"
                    value={stats.todayAtt}
                    subtext="Registros en tiempo real"
                    icon={<Clock size={24} />}
                    color="var(--status-warning)"
                    bg="rgba(230, 162, 60, 0.1)"
                />
                <StatCard
                    title="Excepciones"
                    value={stats.abnormal}
                    subtext="Tardanzas / Ausencias"
                    icon={<AlertTriangle size={24} />}
                    color="var(--status-error)"
                    bg="rgba(245, 108, 108, 0.1)"
                />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px', marginTop: '10px' }}>
                {/* Main Chart Area (Mock for now) */}
                <div className="card" style={{ minHeight: '300px' }}>
                    <div className="card-header flex-row space-between">
                        <span><Activity size={16} style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} /> Tendencia de Asistencia</span>
                        <select style={{ fontSize: '12px', padding: '2px 5px' }}>
                            <option>Esta Semana</option>
                            <option>Este Mes</option>
                        </select>
                    </div>
                    <div style={{ height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#ccc' }}>
                        [ Gráfico de Barras: Asistencia vs Ausencia ]
                    </div>
                </div>

                {/* Quick Actions & Shortcuts */}
                <div className="flex-col gap-4">
                    <div className="card">
                        <div className="card-header">Accesos Rápidos</div>
                        <div className="flex-col gap-2">
                            <QuickLink to="/personnel/employees" icon={<UserPlus size={16} />} label="Agregar Empleado" />
                            <QuickLink to="/devices" icon={<Server size={16} />} label="Estado Dispositivos" />
                            <QuickLink to="/attendance/reports" icon={<FileText size={16} />} label="Generar Reporte" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

const StatCard = ({ title, value, subtext, icon, color, bg }: any) => (
    <div className="card" style={{ display: 'flex', alignItems: 'center', padding: '20px', borderLeft: `4px solid ${color}`, gap: '15px' }}>
        <div style={{
            width: '48px', height: '48px', borderRadius: '50%',
            backgroundColor: bg, color: color,
            display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
            {icon}
        </div>
        <div>
            <div style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: 500 }}>{title}</div>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--text-main)', lineHeight: '1.2' }}>{value}</div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{subtext}</div>
        </div>
    </div>
);

const QuickLink = ({ to, icon, label }: any) => (
    <Link to={to} style={{
        display: 'flex', alignItems: 'center', gap: '10px',
        padding: '10px', borderRadius: '4px',
        border: '1px solid var(--border-color)',
        color: 'var(--text-main)',
        transition: 'all 0.2s'
    }}
        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--bg-main)'}
        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
    >
        <span style={{ color: 'var(--primary)' }}>{icon}</span>
        <span style={{ fontSize: '13px', fontWeight: 500 }}>{label}</span>
    </Link>
);
