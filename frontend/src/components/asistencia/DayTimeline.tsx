import React, { useEffect, useState } from 'react';
import { getTimeline } from '../../api';

interface DayTimelineProps {
    employeeId: string;
    date: string;
}

interface TimelineBlock {
    type: string;
    start_time: string;
    end_time: string;
    duration_minutes: number;
}

export const DayTimeline: React.FC<DayTimelineProps> = ({ employeeId, date }) => {
    const [blocks, setBlocks] = useState<TimelineBlock[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchTimeline = async () => {
            try {
                setLoading(true);
                const result = await getTimeline(employeeId, date);
                setBlocks(result.blocks || []);
                setError(null);
            } catch (err: any) {
                console.error('Error loading timeline:', err);
                setError('No se pudo cargar la línea de tiempo');
            } finally {
                setLoading(false);
            }
        };

        fetchTimeline();
    }, [employeeId, date]);

    if (loading) {
        return (
            <div className="card" style={{ padding: '20px' }}>
                <h3 style={{ margin: '0 0 16px 0' }}>Línea de Tiempo</h3>
                <div style={{ textAlign: 'center', color: '#666', padding: '40px' }}>
                    Cargando línea de tiempo...
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="card" style={{ padding: '20px' }}>
                <h3 style={{ margin: '0 0 16px 0' }}>Línea de Tiempo</h3>
                <div style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
                    {error}
                </div>
            </div>
        );
    }

    if (blocks.length === 0) {
        return (
            <div className="card" style={{ padding: '20px' }}>
                <h3 style={{ margin: '0 0 16px 0' }}>Línea de Tiempo</h3>
                <div style={{ textAlign: 'center', color: '#666', padding: '40px' }}>
                    No hay bloques de tiempo para mostrar
                </div>
            </div>
        );
    }

    // Block type colors
    const getBlockStyle = (type: string) => {
        const styles: { [key: string]: { bg: string; color: string; label: string } } = {
            'WORK': { bg: '#4caf50', color: 'white', label: 'Trabajo' },
            'BREAK': { bg: '#2196f3', color: 'white', label: 'Descanso' },
            'GAP_ANOMALY': { bg: '#ff9800', color: 'white', label: 'Gap Anómalo' },
            'GAP_UNCLASSIFIED': { bg: '#9e9e9e', color: 'white', label: 'No Clasificado' },
            'SCHEDULE_BLOCK': { bg: '#e0e0e0', color: '#212121', label: 'Horario' },
        };
        return styles[type] || { bg: '#bdbdbd', color: '#212121', label: type };
    };

    const formatTime = (timeStr: string) => {
        // timeStr format: "HH:MM:SS" or "YYYY-MM-DD HH:MM:SS"
        if (timeStr.includes(' ')) {
            return timeStr.split(' ')[1].substring(0, 5);
        }
        return timeStr.substring(0, 5);
    };

    return (
        <div className="card" style={{ padding: '20px' }}>
            <h3 style={{ margin: '0 0 16px 0' }}>Línea de Tiempo</h3>

            <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '12px'
            }}>
                {blocks.map((block, index) => {
                    const blockStyle = getBlockStyle(block.type);
                    const hours = Math.floor(block.duration_minutes / 60);
                    const mins = block.duration_minutes % 60;

                    return (
                        <div key={index} style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '16px',
                            padding: '12px',
                            background: 'var(--bg-secondary)',
                            borderRadius: '8px',
                            borderLeft: `4px solid ${blockStyle.bg}`
                        }}>
                            <div style={{
                                minWidth: '120px',
                                fontFamily: 'monospace',
                                fontSize: '14px',
                                fontWeight: 600,
                                color: '#212121'
                            }}>
                                {formatTime(block.start_time)} - {formatTime(block.end_time)}
                            </div>

                            <div style={{
                                flex: 1,
                                display: 'flex',
                                alignItems: 'center',
                                gap: '12px'
                            }}>
                                <div style={{
                                    height: '32px',
                                    flex: 1,
                                    background: blockStyle.bg,
                                    borderRadius: '4px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    color: blockStyle.color,
                                    fontSize: '13px',
                                    fontWeight: 500
                                }}>
                                    {blockStyle.label}
                                </div>

                                <div style={{
                                    minWidth: '80px',
                                    fontSize: '13px',
                                    color: '#666',
                                    textAlign: 'right'
                                }}>
                                    {hours}h {mins}m
                                </div>
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
                <strong>Leyenda:</strong> Los bloques muestran el uso del tiempo durante la jornada laboral
            </div>
        </div>
    );
};
