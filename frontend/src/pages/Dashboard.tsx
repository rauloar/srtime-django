import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Building2, Users, Monitor,
    CalendarClock, CalendarDays,
    FileBarChart, CheckCircle, AlertCircle
} from 'lucide-react';
import { getDepartments, getEmployees, getTimetables, getShifts, getDevices } from '../api';

export const Dashboard: React.FC = () => {
    const navigate = useNavigate();
    const [stats, setStats] = useState({
        depts: 0,
        emps: 0,
        devices: 0,
        timetables: 0,
        shifts: 0
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            try {
                const [d, e, dev, t, s] = await Promise.all([
                    getDepartments(),
                    getEmployees(0, 1),
                    getDevices(),
                    getTimetables(),
                    getShifts()
                ]);
                setStats({
                    depts: d.length,
                    emps: e.length, // approximation or add count endpoint
                    devices: dev.length,
                    timetables: t.length,
                    shifts: s.length
                });
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, []);

    const ChecklistItem = ({ label, done, path }: { label: string, done: boolean, path: string }) => (
        <div
            onClick={() => navigate(path)}
            style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '12px', borderBottom: '1px solid var(--border-color)', cursor: 'pointer'
            }}
            className="hover-bg"
        >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                {done ? <CheckCircle size={20} color="var(--status-ok)" /> : <AlertCircle size={20} color="var(--text-muted)" />}
                <span style={{ color: done ? 'var(--text-main)' : 'var(--text-secondary)', fontWeight: done ? 500 : 400 }}>{label}</span>
            </div>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{done ? 'Configurado' : 'Pendiente'}</span>
        </div>
    );

    const StatCard = ({ label, value, icon: Icon, color }: any) => (
        <div className="card-stat">
            <div className="card-stat-icon" style={{ background: `${color}20`, color: color }}>
                <Icon size={28} />
            </div>
            <div className="card-stat-content">
                <div className="card-stat-value">{loading ? '-' : value}</div>
                <div className="card-stat-label">{label}</div>
            </div>
        </div>
    );

    return (
        <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <h2 style={{ marginBottom: '0px', fontSize: '24px', fontWeight: 700 }}>Tablero General</h2>

            {/* Stats Row */}
            <div className="stats-grid">
                <StatCard label="Dispositivos" value={stats.devices} icon={Monitor} color="#0288d1" />
                <StatCard label="Empleados" value={stats.emps} icon={Users} color="#7b1fa2" />
                <StatCard label="Departamentos" value={stats.depts} icon={Building2} color="#ed6c02" />
                <StatCard label="Horarios" value={stats.timetables} icon={CalendarClock} color="#2e7d32" />
            </div>

            <div className="dashboard-grid">

                {/* Setup Wizard */}
                <div className="card" style={{ padding: '0', overflow: 'hidden', height: 'fit-content', width: '100%' }}>
                    <div style={{ padding: '15px 20px', background: 'var(--sidebar-bg)', borderBottom: '1px solid var(--border-color)', fontWeight: 600 }}>
                        Estado del Sistema
                    </div>
                    <ChecklistItem label="Crear Departamentos" done={stats.depts > 0} path="/personnel/departments" />
                    <ChecklistItem label="Cargar Empleados" done={stats.emps > 0} path="/personnel/employees" />
                    <ChecklistItem label="Definir Horarios" done={stats.timetables > 0} path="/attendance/timetables" />
                    <ChecklistItem label="Crear Turnos" done={stats.shifts > 0} path="/attendance/shifts" />
                    <ChecklistItem label="Conectar Dispositivos" done={stats.devices > 0} path="/devices" />
                </div>

                {/* Quick Access Workflow */}
                <div className="card" style={{ padding: '20px', width: '100%' }}>
                    <h3 style={{ marginTop: 0 }}>Flujo de Trabajo</h3>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-around', flexWrap: 'wrap', marginTop: '20px', gap: '20px' }}>

                        <div className="flex-col align-center gap-2" style={{ cursor: 'pointer' }} onClick={() => navigate('/devices')}>
                            <div className="circle-icon" style={{ background: '#e3f2fd', color: '#1976d2' }}><Monitor /></div>
                            <span style={{ fontSize: '12px', fontWeight: 500 }}>1. Dispositivos</span>
                        </div>

                        <div style={{ width: '40px', height: '1px', background: '#ddd' }}></div>

                        <div className="flex-col align-center gap-2" style={{ cursor: 'pointer' }} onClick={() => navigate('/personnel/employees')}>
                            <div className="circle-icon" style={{ background: '#f3e5f5', color: '#7b1fa2' }}><Users /></div>
                            <span style={{ fontSize: '12px', fontWeight: 500 }}>2. Personal</span>
                        </div>

                        <div style={{ width: '40px', height: '1px', background: '#ddd' }}></div>

                        <div className="flex-col align-center gap-2" style={{ cursor: 'pointer' }} onClick={() => navigate('/attendance/schedule')}>
                            <div className="circle-icon" style={{ background: '#e8f5e9', color: '#2e7d32' }}><CalendarDays /></div>
                            <span style={{ fontSize: '12px', fontWeight: 500 }}>3. Programación</span>
                        </div>

                        <div style={{ width: '40px', height: '1px', background: '#ddd' }}></div>

                        <div className="flex-col align-center gap-2" style={{ cursor: 'pointer' }} onClick={() => navigate('/attendance/reports')}>
                            <div className="circle-icon" style={{ background: '#fff3e0', color: '#ed6c02' }}><FileBarChart /></div>
                            <span style={{ fontSize: '12px', fontWeight: 500 }}>4. Reportes</span>
                        </div>

                    </div>

                    <div style={{ marginTop: '40px', padding: '15px', background: 'var(--bg-main)', borderRadius: '8px' }}>
                        <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '10px' }}>Accesos Rápidos</div>
                        <div className="flex-row gap-4">
                            <button className="secondary small" onClick={() => navigate('/attendance/calculation')}>Calcular Asistencia</button>
                            <button className="secondary small" onClick={() => navigate('/attendance/absences')}>Registrar Ausencia</button>
                        </div>
                    </div>
                </div>
            </div>

            <style>{`
                .hover-bg:hover { background-color: var(--sidebar-hover-bg); }
                .circle-icon { width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 5px; }
            `}</style>
        </div>
    );
};
