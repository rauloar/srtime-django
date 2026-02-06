import React, { useEffect, useState } from 'react';
import { getDailyReports } from '../../api';
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

                const data = await getDailyReports(date, date);

                // Calculate stats
                const total = data.length;
                const present = data.filter(d => d.status === 'Normal').length;
                const late = data.filter(d => d.status === 'Late').length;
                const absent = data.filter(d => d.status === 'Absent').length;
                const pending = data.filter(d =>
                    !d.status || d.status === 'Pending' || d.status === ''
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
                console.error('Error loading today summary:', err);
                // DEBUG: Show technical error
                const techMsg = err?.response?.status
                    ? `Status: ${err.response.status} (${err.response.statusText})`
                    : (err?.message || String(err));
                setError(`Error: ${techMsg}`);
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
            <div className="card" style={{ padding: '20px', background: 'rgba(198, 40, 40, 0.1)', color: 'var(--att-absent)' }}>
                ⚠️ {error} <br />
                <small style={{ opacity: 0.8 }}>{(error as any)?.message || String(error)}</small>
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
            <div className="card-stat-icon" style={{ background: `${color}20`, color }}>
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
                color="#2e7d32"
            />
            <StatCard
                label="Llegadas Tarde"
                value={stats.late}
                subtitle={stats.late > 0 ? 'Requiere atención' : 'Todo en orden'}
                icon={Clock}
                color="#ed6c02"
            />
            <StatCard
                label="Ausentes"
                value={stats.absent}
                subtitle={stats.absent > 0 ? 'Revisar justificaciones' : 'Sin ausencias'}
                icon={XCircle}
                color="#d32f2f"
            />
            <StatCard
                label="Pendientes"
                value={stats.pending}
                subtitle={stats.pending > 0 ? 'Aún no fichan' : 'Todos ficharon'}
                icon={AlertCircle}
                color="#757575"
            />
        </div>
    );
};
