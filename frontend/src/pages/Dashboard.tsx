import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';

interface Employee {
    id: number;
    user_id: string;
    name: string;
    department: number | null;
}

interface DayStatus {
    status: string;
    worked_minutes: number;
}

export const Dashboard: React.FC = () => {
    const navigate = useNavigate();
    const today = new Date().toISOString().split('T')[0];
    const [employees, setEmployees] = useState<Employee[]>([]);
    const [statuses, setStatuses] = useState<Record<number, DayStatus>>({});
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                // 1. Get Employees
                const empRes = await api.get('/employees/');
                const empList = empRes.data.results || empRes.data; // Handle pagination or list
                setEmployees(empList);

                // 2. Fetch status for each (Parallel)
                const statusMap: Record<number, DayStatus> = {};
                await Promise.all(empList.map(async (emp: Employee) => {
                    try {
                        const dayRes = await api.get(`/attendance/day/?employee_id=${emp.id}&date=${today}`);
                        statusMap[emp.id] = {
                            status: dayRes.data.status,
                            worked_minutes: dayRes.data.worked_minutes
                        };
                    } catch (e) {
                        statusMap[emp.id] = { status: 'Error', worked_minutes: 0 };
                    }
                }));
                setStatuses(statusMap);
            } catch (error) {
                console.error("Dashboard Error:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, [today]);

    if (loading) return <div style={{ padding: '20px' }}>Cargando Dashboard...</div>;

    return (
        <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '20px' }}>
            <h2 style={{ marginBottom: '20px' }}>Dashboard Operativo ({today})</h2>

            <table style={{ width: '100%', borderCollapse: 'collapse', background: 'white', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                <thead style={{ background: '#f8f9fa', borderBottom: '2px solid #dee2e6' }}>
                    <tr>
                        <th style={{ padding: '12px', textAlign: 'left' }}>Empleado</th>
                        <th style={{ padding: '12px', textAlign: 'left' }}>ID</th>
                        <th style={{ padding: '12px', textAlign: 'center' }}>Estado Hoy</th>
                        <th style={{ padding: '12px', textAlign: 'center' }}>Horas</th>
                        <th style={{ padding: '12px', textAlign: 'right' }}>Acción</th>
                    </tr>
                </thead>
                <tbody>
                    {employees.map(emp => {
                        const st = statuses[emp.id] || { status: 'Pending', worked_minutes: 0 };
                        const hours = Math.floor(st.worked_minutes / 60);
                        const mins = st.worked_minutes % 60;

                        let statusColor = '#6c757d'; // grey
                        if (st.status === 'Normal') statusColor = '#28a745'; // green
                        if (st.status === 'Partial') statusColor = '#ffc107'; // yellow
                        if (st.status === 'Absent') statusColor = '#dc3545'; // red

                        return (
                            <tr key={emp.id} style={{ borderBottom: '1px solid #dee2e6' }}>
                                <td style={{ padding: '12px' }}>{emp.name || 'Sin Nombre'}</td>
                                <td style={{ padding: '12px', color: '#666' }}>{emp.user_id}</td>
                                <td style={{ padding: '12px', textAlign: 'center' }}>
                                    <span style={{
                                        padding: '4px 8px',
                                        borderRadius: '4px',
                                        color: 'white',
                                        backgroundColor: statusColor,
                                        fontSize: '0.9em',
                                        fontWeight: 500
                                    }}>
                                        {st.status}
                                    </span>
                                </td>
                                <td style={{ padding: '12px', textAlign: 'center' }}>
                                    {st.worked_minutes > 0 ? `${hours}h ${mins}m` : '-'}
                                </td>
                                <td style={{ padding: '12px', textAlign: 'right' }}>
                                    <button
                                        onClick={() => navigate(`/asistencia/empleado/${emp.id}/dia/${today}`)}
                                        style={{
                                            padding: '6px 12px',
                                            cursor: 'pointer',
                                            background: '#007bff',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '4px'
                                        }}
                                    >
                                        Ver Detalle
                                    </button>
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
};
