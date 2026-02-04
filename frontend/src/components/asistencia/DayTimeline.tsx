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
                <h3 style={{ margin: '0 0 16px 0' }}>⏱️ Distribución Temporal</h3>
                <div style={{ textAlign: 'center', color: '#666', padding: '40px' }}>
                    Cargando distribución temporal...
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="card" style={{ padding: '20px' }}>
                <h3 style={{ margin: '0 0 16px 0' }}>⏱️ Distribución Temporal</h3>
                <div style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
                    {error}
                </div>
            </div>
        );
    }

    if (blocks.length === 0) {
        return (
            <div className="card" style={{ padding: '20px' }}>
                <h3 style={{ margin: '0 0 16px 0' }}>⏱️ Distribución Temporal</h3>
                <div style={{ textAlign: 'center', color: '#666', padding: '40px' }}>
                    No hay bloques de tiempo para mostrar
                </div>
            </div>
        );
    }

    // Non-evaluative block labels - describe what was registered, not what it means
    const getBlockStyle = (type: string) => {
        const styles: { [key: string]: { bg: string; color: string; label: string } } = {
            'WORK': { bg: '#4caf50', color: 'white', label: 'Presencia Registrada' },
            'BREAK': { bg: '#2196f3', color: 'white', label: 'Pausa Corta' },
            'GAP_ANOMALY': { bg: '#ff9800', color: 'white', label: 'Ausencia Prolongada' },
            'GAP_UNCLASSIFIED': { bg: '#9e9e9e', color: 'white', label: 'Sin Clasificar' },
            'SCHEDULE_BLOCK': { bg: '#e0e0e0', color: '#212121', label: 'Bloque de Horario' },
        };
        return styles[type] || { bg: '#bdbdbd', color: '#212121', label: 'Otro' };
    };

    const formatTime = (timeStr: string) => {
        // timeStr format: "HH:MM:SS" or "YYYY-MM-DD HH:MM:SS"
        if (timeStr.includes(' ')) {
            return timeStr.split(' ')[1].substring(0, 5);
        }
        return timeStr.substring(0, 5);
    };

    const formatDuration = (minutes: number): string => {
        if (minutes < 60) {
            return `${minutes}min`;
        }
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return mins > 0 ? `${hours}h ${mins}min` : `${hours}h`;
    };

    return (
        <div className="card" style={{ padding: '20px' }}>
            <h3 style={{ margin: '0 0 16px 0' }}>⏱️ Distribución Temporal</h3>

            <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '8px'
            }}>
                {blocks.map((block, index) => {
                    const blockStyle = getBlockStyle(block.type);

                    return (
                        <div key={index} style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px',
                            padding: '10px 14px',
                            background: 'var(--bg-secondary)',
                            borderRadius: '6px',
                            borderLeft: `4px solid ${blockStyle.bg}`
                        }}>
                            {/* Time range */}
                            <div style={{
                                minWidth: '110px',
                                fontFamily: 'monospace',
                                fontSize: '13px',
                                fontWeight: 600,
                                color: '#212121',
                                letterSpacing: '0.3px'
                            }}>
                                {formatTime(block.start_time)} - {formatTime(block.end_time)}
                            </div>

                            {/* Visual block bar */}
                            <div style={{
                                flex: 1,
                                display: 'flex',
                                alignItems: 'center',
                                gap: '10px'
                            }}>
                                <div style={{
                                    height: '28px',
                                    flex: 1,
                                    background: blockStyle.bg,
                                    borderRadius: '4px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    color: blockStyle.color,
                                    fontSize: '12px',
                                    fontWeight: 500,
                                    padding: '0 12px'
                                }}>
                                    {blockStyle.label}
                                </div>

                                {/* Duration */}
                                <div style={{
                                    minWidth: '70px',
                                    fontSize: '12px',
                                    color: '#666',
                                    textAlign: 'right',
                                    fontWeight: 500
                                }}>
                                    {formatDuration(block.duration_minutes)}
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
                color: '#666',
                lineHeight: '1.5'
            }}>
                <strong>Nota:</strong> Esta visualización muestra la distribución temporal de los eventos registrados.
                Las clasificaciones son automáticas y deben ser interpretadas por RRHH considerando el contexto laboral.
            </div>
        </div>
    );
};
