import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getDailyReports, type DailyAttendance } from '../../api';
import { ChevronRight, Clock, XCircle, AlertTriangle } from 'lucide-react';

interface AttentionListProps {
    dateRange?: { from: string; to: string };
    limit?: number;
}

interface AttentionItem {
    employee_id: number;
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
                const data = await getDailyReports(from, to);

                // Filter problematic days (status !== 'Normal')
                const problematic = data.filter(d => d.status !== 'Normal' && d.status !== '');

                // Transform to AttentionItem format
                const attentionItems: AttentionItem[] = problematic.map(d => {
                    const item: AttentionItem = {
                        employee_id: d.employee_id!,
                        employee_name: d.employee_name || 'Sin nombre',
                        date: d.date!,
                        status: d.status,
                        late_minutes: d.late_minutes,
                        problem_summary: generateProblemSummary(d),
                        severity: calculateSeverity(d)
                    };
                    return item;
                });

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
                console.error('Error loading attention list:', err);
                setError('No se pudo cargar la lista de atención');
            } finally {
                setLoading(false);
            }
        };

        loadAttentionItems();
    }, [dateRange, limit]);

    const generateProblemSummary = (d: DailyAttendance): string => {
        switch (d.status) {
            case 'Absent':
                return 'Ausente sin justificar';
            case 'Late':
                if (d.late_minutes && d.late_minutes > 0) {
                    const hours = Math.floor(d.late_minutes / 60);
                    const mins = d.late_minutes % 60;
                    if (hours > 0) {
                        return `Llegó tarde ${hours}h ${mins}m`;
                    }
                    return `Llegó tarde ${mins} min`;
                }
                return 'Llegó tarde';
            case 'Early':
                return 'Salió temprano';
            case 'Partial':
                return 'Asistencia parcial';
            default:
                return 'Requiere revisión';
        }
    };

    const calculateSeverity = (d: DailyAttendance): number => {
        // 3 = high (absent), 2 = medium (late >30min), 1 = low (other)
        if (d.status === 'Absent') return 3;
        if (d.status === 'Late' && d.late_minutes && d.late_minutes > 30) return 2;
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
                return <XCircle size={20} color="#d32f2f" />;
            case 2:
                return <Clock size={20} color="#ed6c02" />;
            default:
                return <AlertTriangle size={20} color="#f57c00" />;
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
            <div className="card" style={{ padding: '20px', background: 'rgba(198, 40, 40, 0.1)', color: 'var(--att-absent)' }}>
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
