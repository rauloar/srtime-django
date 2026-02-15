import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    BarChart3,
    Users,
    Calendar,
    Building2,
    Clock,
    Layers
} from 'lucide-react';
import { getDashboardSummary } from '../api';
import type { DashboardSummary } from '../api';

export const Dashboard: React.FC = () => {
    const navigate = useNavigate();
    const [summary, setSummary] = useState<DashboardSummary | null>(null);
    const [summaryError, setSummaryError] = useState(false);

    useEffect(() => {
        const loadSummary = async () => {
            try {
                const response = await getDashboardSummary(7);
                setSummary(response);
                setSummaryError(false);
            } catch (error) {
                setSummaryError(true);
            }
        };

        loadSummary();
    }, []);

    const quickLinks = useMemo(() => ([
        {
            title: 'Marcaciones',
            description: 'Ver registros de asistencia y fichadas',
            icon: <BarChart3 size={28} />,
            path: '/attendance/logs',
            colorClass: 'dash-color-info'
        },
        {
            title: 'Reporte Diario',
            description: 'Analisis historico de asistencia',
            icon: <Calendar size={28} />,
            path: '/attendance/reports',
            colorClass: 'dash-color-success'
        },
        {
            title: 'RRHH',
            description: 'Gestión completa de organización y personal',
            icon: <Users size={28} />,
            path: '/personnel',
            colorClass: 'dash-color-warning'
        }
    ]), []);

    const metrics = useMemo(() => ([
        {
            title: 'Empleados',
            value: summary?.counts.employees ?? null,
            icon: <Users size={20} />,
            colorClass: 'dash-color-info'
        },
        {
            title: 'Empresa',
            value: summary?.company_name ?? null,
            icon: <Building2 size={20} />,
            colorClass: 'dash-color-accent'
        },
        {
            title: 'Departamentos',
            value: summary?.counts.departments ?? null,
            icon: <Layers size={20} />,
            colorClass: 'dash-color-muted'
        },
        {
            title: 'Turnos',
            value: summary?.counts.shifts ?? null,
            icon: <Clock size={20} />,
            colorClass: 'dash-color-warning'
        }
    ]), [summary]);

    const formatMinutes = (minutes: number | null) => {
        if (minutes === null || Number.isNaN(minutes)) return '-';
        const hours = Math.floor(minutes / 60);
        const mins = Math.round(minutes % 60);
        return `${hours}h ${mins}m`;
    };

    return (
        <div className="dashboard-page">
            <div className="dashboard-hero">
                <h1 className="dashboard-title">Bienvenido al Sistema SRTime</h1>
                <p className="dashboard-subtitle">Selecciona una opcion para comenzar</p>
            </div>

            <div className="dashboard-section">
                <div className="dashboard-section-header">
                    <h2 className="dashboard-section-title">Resumen general</h2>
                    {summaryError && (
                        <span className="dashboard-section-note">Resumen no disponible</span>
                    )}
                </div>
                <div className="dashboard-metrics">
                    {metrics.map((metric, idx) => (
                        <div key={idx} className="dashboard-metric-card">
                            <div className={`dashboard-metric-icon ${metric.colorClass}`}>
                                {metric.icon}
                            </div>
                            <div className="dashboard-metric-content">
                                <div className="dashboard-metric-title">{metric.title}</div>
                                <div className="dashboard-metric-value">
                                    {metric.value === null || metric.value === '' ? '-' : metric.value}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="dashboard-links">
                {quickLinks.map((link, idx) => (
                    <button
                        key={idx}
                        type="button"
                        onClick={() => navigate(link.path)}
                        className="dashboard-link-card"
                    >
                        <div className={`dashboard-link-icon ${link.colorClass}`}>
                            {link.icon}
                        </div>
                        <div className="dashboard-link-title">{link.title}</div>
                        <div className="dashboard-link-desc">{link.description}</div>
                    </button>
                ))}
            </div>

            <div className="dashboard-section">
                <div className="dashboard-section-header">
                    <h2 className="dashboard-section-title">Reporte diario</h2>
                    <span className="dashboard-section-note">Historico previo a bajadas de logs</span>
                </div>
                <div className="dashboard-chart">
                    {(summary?.recent_reports || []).length === 0 && (
                        <div className="dashboard-chart-empty">No hay reportes historicos disponibles</div>
                    )}
                    {(summary?.recent_reports || []).map((report) => {
                        const total = report.present + report.absent || 1;
                        const presentPct = Math.round((report.present / total) * 100);
                        const absentPct = 100 - presentPct;
                        return (
                            <div key={report.date} className="dashboard-chart-row">
                                <div className="dashboard-chart-date">{report.date}</div>
                                <div className="dashboard-chart-bars">
                                    <div className="dashboard-chart-bar dash-bar-present" style={{ ['--bar-size' as any]: `${presentPct}%` }}>
                                        <span>{report.present}</span>
                                    </div>
                                    <div className="dashboard-chart-bar dash-bar-absent" style={{ ['--bar-size' as any]: `${absentPct}%` }}>
                                        <span>{report.absent}</span>
                                    </div>
                                </div>
                                <div className="dashboard-chart-hours">{formatMinutes(report.avg_worked_minutes)}</div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};
