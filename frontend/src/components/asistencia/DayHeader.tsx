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
                    ⚠️ {error || 'No se pudo cargar la información del día'}
                </div>
            </div>
        );
    }

    // Simple status based on check-in/check-out presence (non-evaluative)
    const getStatusDisplay = () => {
        const hasCheckIn = data.check_in !== null && data.check_in !== undefined;
        const hasCheckOut = data.check_out !== null && data.check_out !== undefined;

        if (!hasCheckIn && !hasCheckOut) {
            return { 
                label: '⏸️ Sin Registros', 
                color: '#757575', 
                bg: '#f5f5f5',
                description: 'No hay fichadas registradas'
            };
        }
        
        if (hasCheckIn && hasCheckOut) {
            return { 
                label: '✅ Jornada Completa', 
                color: '#2e7d32', 
                bg: '#e8f5e9',
                description: 'Entrada y salida registradas'
            };
        }

        return { 
            label: '⚠️ Jornada Incompleta', 
            color: '#ed6c02', 
            bg: '#fff3e0',
            description: hasCheckIn ? 'Falta fichada de salida' : 'Falta fichada de entrada'
        };
    };

    const statusDisplay = getStatusDisplay();
    const formattedDate = new Date(date).toLocaleDateString('es-ES', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    const employeeName = data.employee?.name || `Empleado ${employeeId}`;

    // Format time display (HH:MM)
    const formatTime = (timeStr: string | null | undefined) => {
        if (!timeStr) return '—';
        // timeStr can be "HH:MM:SS" or "YYYY-MM-DD HH:MM:SS"
        const timePart = timeStr.includes(' ') ? timeStr.split(' ')[1] : timeStr;
        return timePart.substring(0, 5); // HH:MM
    };

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
                        fontSize: '16px',
                        fontWeight: 600,
                        textAlign: 'center'
                    }}>
                        <div>{statusDisplay.label}</div>
                        <div style={{ fontSize: '11px', marginTop: '4px', opacity: 0.9 }}>
                            {statusDisplay.description}
                        </div>
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
                    <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px', fontWeight: 500 }}>
                        ⬇️ Primera Entrada
                    </div>
                    <div style={{ fontSize: '20px', fontWeight: 600, color: '#212121' }}>
                        {formatTime(data.check_in)}
                    </div>
                </div>

                <div>
                    <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px', fontWeight: 500 }}>
                        ⬆️ Última Salida
                    </div>
                    <div style={{ fontSize: '20px', fontWeight: 600, color: '#212121' }}>
                        {formatTime(data.check_out)}
                    </div>
                </div>

                <div>
                    <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px', fontWeight: 500 }}>
                        ⏱️ Horas Trabajadas
                    </div>
                    <div style={{ fontSize: '20px', fontWeight: 600, color: '#212121' }}>
                        {data.worked_minutes > 0 
                            ? `${Math.floor(data.worked_minutes / 60)}h ${data.worked_minutes % 60}m`
                            : '—'
                        }
                    </div>
                </div>
            </div>

            {data.exception_reason && (
                <div style={{
                    padding: '16px 24px',
                    background: '#fff9e6',
                    borderTop: '1px solid var(--border-color)',
                    fontSize: '14px',
                    color: '#666'
                }}>
                    <strong>Observación:</strong> {data.exception_reason}
                </div>
            )}
        </div>
    );
};

