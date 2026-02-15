import React, { useEffect, useState } from 'react';
import { getDailyReportsV2, type DailyAttendanceV2 } from '../../api';
import { Users, Clock, XCircle, AlertCircle } from 'lucide-react';

interface TodaySummaryProps {
    date: string; // YYYY-MM-DD
}

interface SummaryStats {
    total: number;
    present: number;
    presentPercent: number;
    late: number;
    absent: number;
    pending: number;
}

export const TodaySummary: React.FC<TodaySummaryProps> = ({ date }) => {
    const [stats, setStats] = useState<SummaryStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadStats = async () => {
            try {
                setLoading(true);
                setError(null);

                // V2 API: estructura jerárquica
                const data = await getDailyReportsV2(date, date);

                // Calculate stats using v2 structure (status.code)
                const total = data.length;
                const present = data.filter((d: DailyAttendanceV2) => d.status.code === 'NORMAL').length;
                const late = data.filter((d: DailyAttendanceV2) => d.status.code === 'LATE').length;
                const absent = data.filter((d: DailyAttendanceV2) => d.status.code === 'ABSENT').length;
                
                // Pending: status no es NORMAL, LATE, ABSENT, EARLY, PARTIAL (menos comunes)
                const pending = data.filter((d: DailyAttendanceV2) => 
                    !['NORMAL', 'LATE', 'ABSENT', 'EARLY', 'PARTIAL'].includes(d.status.code)
                ).length;

                const presentPercent = total > 0 ? Math.round((present / total) * 100) : 0;

                setStats({
                    total,
                    present,
                    presentPercent,
                    late,
                    absent,
                    pending
                });
            } catch (err: any) {
                setError('No se pudo cargar el resumen');
            } finally {
                setLoading(false);
            }
        };

        loadStats();
    }, [date]);

    if (loading) {
        return (
            <div className="stats-grid">
                {[1, 2, 3, 4].map(i => (
                    <div key={i} className="card-stat" style={{ opacity: 0.6 }}>
                        <div className="card-stat-content">
                            <div className="card-stat-value">—</div>
                            <div className="card-stat-label">Cargando...</div>
                        </div>
                    </div>
                ))}
            </div>
        );
    }

    if (error || !stats) {
        return (
            <div className="card" style={{ padding: '20px', background: 'var(--bg-card)', color: 'var(--text-secondary)' }}>
                ⚠️ {error}
            </div>
        );
    }

    const StatCard = ({
        label,
        value,
        icon: Icon,
        color,
        subtitle
    }: {
        label: string;
        value: number | string;
        icon: any;
        color: string;
        subtitle?: string;
    }) => (
        <div className="card-stat">
            <div className="card-stat-icon" style={{ background: 'var(--bg-highlight)', color }}>
                <Icon size={28} />
            </div>
            <div className="card-stat-content">
                <div className="card-stat-value">{value}</div>
                <div className="card-stat-label">{label}</div>
                {subtitle && (
                    <div style={{
                        fontSize: '11px',
                        color: 'var(--text-muted)',
                        marginTop: '4px'
                    }}>
                        {subtitle}
                    </div>
                )}
            </div>
        </div>
    );

    return (
        <div className="stats-grid">
            <StatCard
                label="Presentes"
                value={`${stats.presentPercent}%`}
                subtitle={`${stats.present} de ${stats.total}`}
                icon={Users}
                color="var(--status-ok)"
            />
            <StatCard
                label="Llegadas Tarde"
                value={stats.late}
                subtitle={stats.late > 0 ? 'Requiere atención' : 'Todo en orden'}
                icon={Clock}
                color="var(--status-warning)"
            />
            <StatCard
                label="Ausentes"
                value={stats.absent}
                subtitle={stats.absent > 0 ? 'Revisar justificaciones' : 'Sin ausencias'}
                icon={XCircle}
                color="var(--status-error)"
            />
            <StatCard
                label="Pendientes"
                value={stats.pending}
                subtitle={stats.pending > 0 ? 'Aún no fichan' : 'Todos ficharon'}
                icon={AlertCircle}
                color="var(--status-offline)"
            />
        </div>
    );
};
