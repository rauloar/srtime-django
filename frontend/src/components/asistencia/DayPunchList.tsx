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
    status_label?: string;
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
                setPunches(result.results || []);
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

    const getStatusIcon = (status: number) => {
        // Simple, clear iconography
        return status === 0 ? '↓' : status === 1 ? '↑' : '◦';
    };

    const getStatusColor = (status: number) => {
        return status === 0 ? '#2196f3' : status === 1 ? '#f44336' : '#9e9e9e';
    };

    const formatTimeWithSeconds = (timestamp: string) => {
        const date = new Date(timestamp);
        return date.toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        });
    };

    // Detect close events (< 2 minutes apart)
    const isCloseEvent = (index: number) => {
        if (index === 0) return false;
        const current = new Date(punches[index].timestamp);
        const previous = new Date(punches[index - 1].timestamp);
        const diffMinutes = (current.getTime() - previous.getTime()) / 1000 / 60;
        return Math.abs(diffMinutes) < 2;
    };

    // Detect irregular sequences (same status twice in a row)
    const isIrregularSequence = (index: number) => {
        if (index === 0) return false;
        const current = punches[index].status;
        const previous = punches[index - 1].status;
        // Detect two entries or two exits in a row (only for status 0 and 1)
        if ([0, 1].includes(current) && [0, 1].includes(previous)) {
            return current === previous;
        }
        return false;
    };

    if (loading) {
        return (
            <div className="card" style={{ padding: '20px' }}>
                <h3 style={{ margin: '0 0 16px 0' }}>📋 Detalle de Fichadas</h3>
                <div style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
                    Cargando fichadas...
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="card" style={{ padding: '20px' }}>
                <h3 style={{ margin: '0 0 16px 0' }}>📋 Detalle de Fichadas</h3>
                <div style={{ textAlign: 'center', color: '#c62828', padding: '20px' }}>
                    ⚠️ {error}
                </div>
            </div>
        );
    }

    if (punches.length === 0) {
        return (
            <div className="card" style={{ padding: '20px' }}>
                <h3 style={{ margin: '0 0 16px 0' }}>📋 Detalle de Fichadas</h3>
                <div style={{
                    textAlign: 'center',
                    padding: '40px',
                    background: '#f5f5f5',
                    borderRadius: '8px',
                    border: '1px dashed #ccc'
                }}>
                    <div style={{ fontSize: '48px', marginBottom: '16px', opacity: 0.5 }}>⏸️</div>
                    <div style={{ color: '#666', fontWeight: 500 }}>
                        Sin fichadas registradas para este día
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="card" style={{ padding: '20px' }}>
            <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '16px' 
            }}>
                <h3 style={{ margin: '0' }}>
                    📋 Detalle de Fichadas
                </h3>
                <span style={{ 
                    background: '#e3f2fd', 
                    color: '#1565c0',
                    padding: '4px 12px',
                    borderRadius: '12px',
                    fontSize: '13px',
                    fontWeight: 600
                }}>
                    {punches.length} evento{punches.length !== 1 ? 's' : ''}
                </span>
            </div>

            <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '4px'
            }}>
                {punches.map((punch, index) => {
                    const isClose = isCloseEvent(index);
                    const isIrregular = isIrregularSequence(index);
                    const hasWarning = isClose || isIrregular;

                    return (
                        <div key={punch.id} style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px',
                            padding: '10px 14px',
                            background: hasWarning 
                                ? '#fff3e0' 
                                : (index % 2 === 0 ? 'var(--bg-secondary)' : 'transparent'),
                            borderRadius: '4px',
                            borderLeft: hasWarning ? '3px solid #ff9800' : '3px solid transparent'
                        }}>
                            <div style={{ 
                                fontSize: '28px',
                                color: getStatusColor(punch.status),
                                fontWeight: 'bold',
                                lineHeight: 1,
                                minWidth: '30px',
                                textAlign: 'center'
                            }}>
                                {getStatusIcon(punch.status)}
                            </div>

                            <div style={{ flex: 1 }}>
                                <div style={{
                                    fontWeight: 600,
                                    fontSize: '15px',
                                    color: '#212121',
                                    marginBottom: '2px'
                                }}>
                                    {punch.status_label || `Estado ${punch.status}`}
                                </div>
                                <div style={{ fontSize: '12px', color: '#999' }}>
                                    {punch.punch_source || 'Terminal'}
                                </div>
                            </div>

                            <div style={{
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'flex-end',
                                gap: '4px'
                            }}>
                                <div style={{
                                    fontFamily: 'monospace',
                                    fontSize: '17px',
                                    fontWeight: 600,
                                    color: '#212121',
                                    letterSpacing: '0.5px'
                                }}>
                                    {formatTimeWithSeconds(punch.timestamp)}
                                </div>
                                {hasWarning && (
                                    <div style={{
                                        fontSize: '11px',
                                        color: '#ed6c02',
                                        fontWeight: 500
                                    }}>
                                        {isClose && '⚠️ Evento cercano'}
                                        {isIrregular && '⚠️ Secuencia irregular'}
                                    </div>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>

            <div style={{
                marginTop: '16px',
                padding: '12px',
                background: '#f5f5f5',
                borderRadius: '4px',
                fontSize: '12px',
                color: '#666'
            }}>
                <strong>Nota:</strong> Los eventos cercanos (&lt;2min) o secuencias irregulares se resaltan automáticamente para revisión.
            </div>
        </div>
    );
};
