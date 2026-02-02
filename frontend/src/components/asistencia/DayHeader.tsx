import React, { useEffect, useState } from 'react';
import { getDailyReports, type DailyAttendance } from '../../api';

interface DayHeaderProps {
    employeeId: string;
    date: string;
}

export const DayHeader: React.FC<DayHeaderProps> = ({ employeeId, date }) => {
    const [data, setData] = useState<DailyAttendance | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                // Use existing daily reports endpoint
                const results = await getDailyReports(date, date);
                // Find the record for this specific employee
                const employeeData = results.find(r => r.employee_id?.toString() === employeeId);

                if (employeeData) {
                    setData(employeeData);
                    setError(null);
                } else {
                    setError(`No se encontraron datos para el empleado ${employeeId} en esta fecha`);
                }
            } catch (err: any) {
                console.error('Error loading day data:', err);
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
                <div style={{ textAlign: 'center', color: '#666' }}>
                    Cargando información del día...
                </div>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="card" style={{ padding: '20px', background: '#fff3e0' }}>
                <div style={{ color: '#ed6c02' }}>
                    ❌ {error || 'No se pudo cargar la información del día'}
                </div>
            </div>
        );
    }

    // Status colors and labels
    const getStatusDisplay = (status: string) => {
        const statusMap: { [key: string]: { label: string; color: string; bg: string } } = {
            'Normal': { label: '✅ PRESENTE', color: '#2e7d32', bg: '#e8f5e9' },
            'Late': { label: '⚠️ LLEGÓ TARDE', color: '#ed6c02', bg: '#fff3e0' },
            'Absent': { label: '❌ AUSENTE', color: '#c62828', bg: '#ffebee' },
            'Early': { label: '⚠️ SALIÓ TEMPRANO', color: '#f9a825', bg: '#fff9e6' },
            'Partial': { label: '⚠️ ASISTENCIA PARCIAL', color: '#9c27b0', bg: '#f3e5f5' },
            'Rest Day': { label: 'ℹ️ DÍA DE DESCANSO', color: '#1565c0', bg: '#e3f2fd' },
        };

        return statusMap[status] || { label: status, color: '#666', bg: '#f5f5f5' };
    };

    const statusDisplay = getStatusDisplay(data.status);
    const formattedDate = new Date(date).toLocaleDateString('es-ES', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    // Calculate expected minutes (8 hours default if not specified)
    const expectedMinutes = data.on_duty && data.off_duty
        ? (() => {
            const onDuty = new Date(`1970-01-01T${data.on_duty}`);
            const offDuty = new Date(`1970-01-01T${data.off_duty}`);
            return Math.floor((offDuty.getTime() - onDuty.getTime()) / 60000);
        })()
        : 480; // 8 hours default

    const employeeName = data.employee?.name || `Empleado ${employeeId}`;

    return (
        <div className="card" style={{ padding: '0', overflow: 'hidden' }}>
            <div style={{
                padding: '24px',
                background: statusDisplay.bg,
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
                            color: '#212121'
                        }}>
                            {employeeName}
                        </h2>
                        <div style={{
                            fontSize: '14px',
                            color: '#666',
                            textTransform: 'capitalize'
                        }}>
                            {formattedDate}
                        </div>
                    </div>

                    <div style={{
                        padding: '12px 24px',
                        background: statusDisplay.color,
                        color: 'white',
                        borderRadius: '8px',
                        fontSize: '18px',
                        fontWeight: 600,
                        textAlign: 'center'
                    }}>
                        {statusDisplay.label}
                    </div>
                </div>
            </div>

            <div style={{
                padding: '20px 24px',
                display: 'flex',
                gap: '32px',
                flexWrap: 'wrap',
                background: 'var(--bg-card)'
            }}>
                <div>
                    <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
                        Horas Trabajadas
                    </div>
                    <div style={{ fontSize: '20px', fontWeight: 600, color: '#212121' }}>
                        {Math.floor(data.worked_minutes / 60)}h {data.worked_minutes % 60}m
                    </div>
                </div>

                <div>
                    <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
                        Horas Esperadas
                    </div>
                    <div style={{ fontSize: '20px', fontWeight: 600, color: '#666' }}>
                        {Math.floor(expectedMinutes / 60)}h {expectedMinutes % 60}m
                    </div>
                </div>

                {data.worked_minutes !== expectedMinutes && (
                    <div>
                        <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
                            Diferencia
                        </div>
                        <div style={{
                            fontSize: '20px',
                            fontWeight: 600,
                            color: data.worked_minutes < expectedMinutes ? '#c62828' : '#2e7d32'
                        }}>
                            {data.worked_minutes > expectedMinutes ? '+' : ''}
                            {Math.floor((data.worked_minutes - expectedMinutes) / 60)}h{' '}
                            {Math.abs((data.worked_minutes - expectedMinutes) % 60)}m
                        </div>
                    </div>
                )}

                {data.late_minutes > 0 && (
                    <div>
                        <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
                            Llegada Tarde
                        </div>
                        <div style={{ fontSize: '20px', fontWeight: 600, color: '#ed6c02' }}>
                            {data.late_minutes}m
                        </div>
                    </div>
                )}

                {data.overtime_minutes > 0 && (
                    <div>
                        <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
                            Horas Extras
                        </div>
                        <div style={{ fontSize: '20px', fontWeight: 600, color: '#1565c0' }}>
                            {Math.floor(data.overtime_minutes / 60)}h {data.overtime_minutes % 60}m
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
