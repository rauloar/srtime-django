import React, { useEffect, useState } from 'react';
import { getDailyReportsV2, type DailyAttendanceV2 } from '../../api';

interface DayHeaderProps {
    employeeId: string;
    date: string;
}

export const DayHeader: React.FC<DayHeaderProps> = ({ employeeId, date }) => {
    const [data, setData] = useState<DailyAttendanceV2 | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const results = await getDailyReportsV2(date, date);
                const employeeData = results.find((r: DailyAttendanceV2) => r.identity.employee_id.toString() === employeeId);

                if (employeeData) {
                    setData(employeeData);
                    setError(null);
                } else {
                    setError(`No se encontraron datos para el empleado ${employeeId} en esta fecha`);
                }
            } catch (err: any) {
                setError('Error cargando datos del día');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [employeeId, date]);

    if (loading) {
        return (
            <div className="card" style={{ padding: '20px' }}>
                <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                    Cargando información del día...
                </div>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="card" style={{ padding: '20px', background: 'var(--bg-card)' }}>
                <div style={{ color: 'var(--status-warning)' }}>
                    ⚠️ {error || 'No se pudo cargar la información del día'}
                </div>
            </div>
        );
    }

    const statusLabel = data.status.label;
    const statusColor = data.status.color;
    const formattedDate = new Date(date).toLocaleDateString('es-ES', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    const employeeName = data.employee.name || `Empleado ${employeeId}`;

    // Format time display (HH:MM)
    const formatTime = (timeStr: string | null | undefined) => {
        if (!timeStr) return '—';
        const dt = new Date(timeStr);
        return dt.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', hour12: false });
    };

    return (
        <div className="card" style={{ padding: '0', overflow: 'hidden' }}>
            <div style={{
                padding: '24px',
                background: 'var(--bg-card)',
                borderBottom: '1px solid var(--border-color)'
            }}>
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    flexWrap: 'wrap',
                    gap: '16px'
                }}>
                    <div>
                        <h2 style={{
                            margin: '0 0 8px 0',
                            fontSize: '24px',
                            fontWeight: 600,
                            color: 'var(--text-main)'
                        }}>
                            {employeeName}
                        </h2>
                        <div style={{
                            fontSize: '14px',
                            color: 'var(--text-muted)',
                            textTransform: 'capitalize'
                        }}>
                            {formattedDate}
                        </div>
                    </div>

                    <div style={{
                        padding: '12px 24px',
                        background: statusColor,
                        color: 'white',
                        borderRadius: '8px',
                        fontSize: '16px',
                        fontWeight: 600,
                        textAlign: 'center'
                    }}>
                        <div>{statusLabel}</div>
                    </div>
                </div>
            </div>

            <div style={{
                padding: '20px 24px',
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                gap: '24px',
                background: 'var(--bg-card)'
            }}>
                <div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px', fontWeight: 500 }}>
                        ⬇️ Primera Entrada
                    </div>
                    <div style={{ fontSize: '20px', fontWeight: 600, color: 'var(--text-main)' }}>
                        {formatTime(data.schedule.check_in)}
                    </div>
                </div>

                <div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px', fontWeight: 500 }}>
                        ⬆️ Última Salida
                    </div>
                    <div style={{ fontSize: '20px', fontWeight: 600, color: 'var(--text-main)' }}>
                        {formatTime(data.schedule.check_out)}
                    </div>
                </div>

                <div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px', fontWeight: 500 }}>
                        ⏱️ Horas Trabajadas
                    </div>
                    <div style={{ fontSize: '20px', fontWeight: 600, color: 'var(--text-main)' }}>
                        {data.metrics.worked_minutes > 0 
                            ? `${Math.floor(data.metrics.worked_minutes / 60)}h ${data.metrics.worked_minutes % 60}m`
                            : '—'
                        }
                    </div>
                </div>
            </div>
        </div>
    );
};

