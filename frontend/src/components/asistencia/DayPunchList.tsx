import React, { useEffect, useState } from 'react';
import { getAttendanceLogs } from '../../api';

interface DayPunchListProps {
    employeeId: string;
    date: string;
}

interface Punch {
    id: number;
    timestamp: string;
    status: number;
    verify_mode?: number;
    punch_source?: string;
}

export const DayPunchList: React.FC<DayPunchListProps> = ({ employeeId, date }) => {
    const [punches, setPunches] = useState<Punch[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchPunches = async () => {
            try {
                setLoading(true);
                const result = await getAttendanceLogs({
                    user_id: employeeId,
                    from_date: new Date(date).toISOString(),
                    to_date: new Date(date).toISOString(),
                });
                setPunches(result);
                setError(null);
            } catch (err: any) {
                console.error('Error loading punches:', err);
                setError('No se pudieron cargar las fichadas');
            } finally {
                setLoading(false);
            }
        };

        fetchPunches();
    }, [employeeId, date]);

    const getStatusLabel = (status: number) => {
        const labels: { [key: number]: string } = {
            0: 'Entrada',
            1: 'Salida',
            2: 'Inicio Descanso',
            3: 'Fin Descanso',
            4: 'Inicio Horas Extras',
            5: 'Fin Horas Extras',
        };
        return labels[status] || `Estado ${status}`;
    };

    const getStatusIcon = (status: number) => {
        return status === 0 ? '🔵' : status === 1 ? '🔴' : '⚪';
    };

    const formatTime = (timestamp: string) => {
        const date = new Date(timestamp);
        return date.toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        });
    };

    if (loading) {
        return (
            <div className="card" style={{ padding: '20px' }}>
                <h3 style={{ margin: '0 0 16px 0' }}>Fichadas Registradas</h3>
                <div style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
                    Cargando fichadas...
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="card" style={{ padding: '20px' }}>
                <h3 style={{ margin: '0 0 16px 0' }}>Fichadas Registradas</h3>
                <div style={{ textAlign: 'center', color: '#c62828', padding: '20px' }}>
                    {error}
                </div>
            </div>
        );
    }

    if (punches.length === 0) {
        return (
            <div className="card" style={{ padding: '20px' }}>
                <h3 style={{ margin: '0 0 16px 0' }}>Fichadas Registradas</h3>
                <div style={{
                    textAlign: 'center',
                    padding: '40px',
                    background: '#fff3e0',
                    borderRadius: '8px'
                }}>
                    <div style={{ fontSize: '48px', marginBottom: '16px' }}>⚠️</div>
                    <div style={{ color: '#ed6c02', fontWeight: 500 }}>
                        Sin fichadas registradas para este día
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="card" style={{ padding: '20px' }}>
            <h3 style={{ margin: '0 0 16px 0' }}>
                Fichadas Registradas ({punches.length})
            </h3>

            <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '8px'
            }}>
                {punches.map((punch, index) => (
                    <div key={punch.id} style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '16px',
                        padding: '12px 16px',
                        background: index % 2 === 0 ? 'var(--bg-secondary)' : 'transparent',
                        borderRadius: '4px'
                    }}>
                        <div style={{ fontSize: '24px' }}>
                            {getStatusIcon(punch.status)}
                        </div>

                        <div style={{ flex: 1 }}>
                            <div style={{
                                fontWeight: 600,
                                fontSize: '15px',
                                color: '#212121',
                                marginBottom: '4px'
                            }}>
                                {getStatusLabel(punch.status)}
                            </div>
                            <div style={{ fontSize: '13px', color: '#666' }}>
                                {punch.punch_source || 'Terminal'}
                            </div>
                        </div>

                        <div style={{
                            fontFamily: 'monospace',
                            fontSize: '18px',
                            fontWeight: 600,
                            color: '#212121',
                            minWidth: '70px',
                            textAlign: 'right'
                        }}>
                            {formatTime(punch.timestamp)}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
