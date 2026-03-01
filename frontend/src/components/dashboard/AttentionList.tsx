import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getDailyReportsV2, type DailyAttendanceV2 } from '../../api';
import { ChevronRight, Clock, XCircle, AlertTriangle } from 'lucide-react';

interface AttentionListProps {
    dateRange?: { from: string; to: string };
    limit?: number;
}

interface AttentionItem {
    employee_id: number;
    user_id: string;
    employee_name: string;
    date: string;
    status: string;
    late_minutes?: number;
    problem_summary: string;
    severity: number; // 1=low, 2=medium, 3=high
}

export const AttentionList: React.FC<AttentionListProps> = ({
    dateRange,
    limit = 10
}) => {
    const navigate = useNavigate();
    const [items, setItems] = useState<AttentionItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadAttentionItems = async () => {
            try {
                setLoading(true);
                setError(null);

                // Use dateRange or default to today
                const today = new Date().toISOString().split('T')[0];
                const from = dateRange?.from || today;
                const to = dateRange?.to || today;

                // Fetch daily reports
                const data = await getDailyReportsV2(from, to);

                const problematic = data.filter((d: DailyAttendanceV2) => d.status.code !== 'NORMAL');

                // Transform to AttentionItem format
                const attentionItems: AttentionItem[] = problematic.map((d: DailyAttendanceV2) => ({
                    employee_id: d.employee.id,
                    user_id: d.employee.user_id,
                    employee_name: d.employee.name || 'Sin nombre',
                    date: d.identity.date,
                    status: d.status.code,
                    late_minutes: d.metrics.late_minutes,
                    problem_summary: generateProblemSummary(d),
                    severity: calculateSeverity(d)
                }));

                // Sort by severity (high to low), then by late_minutes
                attentionItems.sort((a, b) => {
                    if (a.severity !== b.severity) {
                        return b.severity - a.severity;
                    }
                    return (b.late_minutes || 0) - (a.late_minutes || 0);
                });

                // Limit results
                setItems(attentionItems.slice(0, limit));
            } catch (err) {
                setError('No se pudo cargar la lista de atención');
            } finally {
                setLoading(false);
            }
        };

        loadAttentionItems();
    }, [dateRange, limit]);

    const generateProblemSummary = (d: DailyAttendanceV2): string => {
        switch (d.status.code) {
            case 'ABSENT':
                return 'Ausente sin justificar';
            case 'LATE':
                if (d.metrics.late_minutes > 0) {
                    const hours = Math.floor(d.metrics.late_minutes / 60);
                    const mins = d.metrics.late_minutes % 60;
                    if (hours > 0) {
                        return `Llegó tarde ${hours}h ${mins}m`;
                    }
                    return `Llegó tarde ${mins} min`;
                }
                return 'Llegó tarde';
            case 'EARLY':
                return 'Salió temprano';
            case 'PARTIAL':
                return 'Asistencia parcial';
            default:
                return d.status.label || 'Requiere revisión';
        }
    };

    const calculateSeverity = (d: DailyAttendanceV2): number => {
        // 3 = high (absent), 2 = medium (late >30min), 1 = low (other)
        if (d.status.code === 'ABSENT') return 3;
        if (d.status.code === 'LATE' && d.metrics.late_minutes > 30) return 2;
        return 1;
    };

    const formatDate = (dateStr: string): string => {
        const date = new Date(dateStr + 'T00:00:00');
        const days = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
        const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];

        const dayName = days[date.getDay()];
        const day = date.getDate();
        const month = months[date.getMonth()];

        return `${dayName} ${day} ${month}`;
    };

    const getSeverityIcon = (severity: number) => {
        switch (severity) {
            case 3:
                return <XCircle size={20} color="var(--status-error)" />;
            case 2:
                return <Clock size={20} color="var(--status-warning)" />;
            default:
                return <AlertTriangle size={20} color="var(--status-info)" />;
        }
    };

    const handleItemClick = (item: AttentionItem) => {
        navigate(`/asistencia/empleado/${item.employee_id}/dia/${item.date}`);
    };

    if (loading) {
        return (
            <div className="card" style={{ padding: '20px' }}>
                <h3 style={{ marginTop: 0 }}>Requiere Atención</h3>
                <div style={{ color: 'var(--text-muted)' }}>Cargando...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="card" style={{ padding: '20px', background: 'var(--bg-card)', color: 'var(--status-error)' }}>
                ⚠️ {error}
            </div>
        );
    }

    if (items.length === 0) {
        return (
            <div className="card" style={{ padding: '20px' }}>
                <h3 style={{ marginTop: 0 }}>Requiere Atención</h3>
                <div style={{
                    padding: '40px 20px',
                    textAlign: 'center',
                    color: 'var(--text-muted)'
                }}>
                    ✅ No hay días que requieran atención
                </div>
            </div>
        );
    }

    return (
        <div className="card" style={{ padding: '0', overflow: 'hidden' }}>
            <div style={{
                padding: '15px 20px',
                background: 'var(--sidebar-bg)',
                borderBottom: '1px solid var(--border-color)',
                fontWeight: 600,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <span>Requiere Atención</span>
                <span style={{
                    fontSize: '13px',
                    fontWeight: 400,
                    color: 'var(--text-muted)'
                }}>
                    {items.length} {items.length === 1 ? 'día' : 'días'}
                </span>
            </div>

            <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
                {items.map((item, index) => (
                    <div
                        key={`${item.employee_id}-${item.date}`}
                        onClick={() => handleItemClick(item)}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px',
                            padding: '12px 20px',
                            borderBottom: index < items.length - 1 ? '1px solid var(--border-color)' : 'none',
                            cursor: 'pointer',
                            transition: 'background 0.2s'
                        }}
                        className="hover-bg"
                    >
                        {/* Icon */}
                        <div style={{ flexShrink: 0 }}>
                            {getSeverityIcon(item.severity)}
                        </div>

                        {/* Content */}
                        <div style={{ flex: 1, minWidth: 0 }}>
                            <div style={{
                                fontWeight: 500,
                                marginBottom: '4px',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap'
                            }}>
                                {item.employee_name}
                            </div>
                            <div style={{
                                fontSize: '13px',
                                color: 'var(--text-muted)',
                                display: 'flex',
                                gap: '8px',
                                alignItems: 'center'
                            }}>
                                <span>{formatDate(item.date)}</span>
                                <span>•</span>
                                <span>{item.problem_summary}</span>
                            </div>
                        </div>

                        {/* Arrow */}
                        <div style={{ flexShrink: 0 }}>
                            <ChevronRight size={20} color="var(--text-muted)" />
                        </div>
                    </div>
                ))}
            </div>

            <style>{`
                .hover-bg:hover {
                    background-color: var(--sidebar-hover-bg);
                }
            `}</style>
        </div>
    );
};
