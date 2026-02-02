import React, { useEffect, useState } from 'react';
import { getExplanation } from '../../api';

interface DayExplanationProps {
    employeeId: string;
    date: string;
}

interface ExplanationData {
    summary: string;
    anomalies: string[];
    recommendations: string[];
}

export const DayExplanation: React.FC<DayExplanationProps> = ({ employeeId, date }) => {
    const [data, setData] = useState<ExplanationData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchExplanation = async () => {
            try {
                setLoading(true);
                const result = await getExplanation(employeeId, date);
                setData(result);
                setError(null);
            } catch (err: any) {
                console.error('Error loading explanation:', err);
                // Silently fail - explanation is optional
                setData(null);
            } finally {
                setLoading(false);
            }
        };

        fetchExplanation();
    }, [employeeId, date]);

    if (loading) {
        return null; // Don't show loading for optional section
    }

    if (error || !data) {
        return null; // Silently hide if no explanation available
    }

    const hasContent = data.summary || data.anomalies?.length > 0 || data.recommendations?.length > 0;

    if (!hasContent) {
        return null;
    }

    return (
        <div className="card" style={{ padding: '20px' }}>
            <h3 style={{ margin: '0 0 16px 0' }}>Explicación del Día</h3>

            {data.summary && (
                <div style={{
                    padding: '12px 16px',
                    background: '#e3f2fd',
                    borderLeft: '4px solid #2196f3',
                    borderRadius: '4px',
                    marginBottom: '16px'
                }}>
                    <div style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '12px'
                    }}>
                        <span style={{ fontSize: '20px' }}>ℹ️</span>
                        <div style={{ flex: 1, fontSize: '14px', color: '#212121' }}>
                            {data.summary}
                        </div>
                    </div>
                </div>
            )}

            {data.anomalies && data.anomalies.length > 0 && (
                <div style={{ marginBottom: '16px' }}>
                    <h4 style={{
                        margin: '0 0 8px 0',
                        fontSize: '14px',
                        fontWeight: 600,
                        color: '#c62828'
                    }}>
                        🚩 Anomalías Detectadas
                    </h4>
                    <ul style={{
                        margin: 0,
                        padding: '0 0 0 20px',
                        listStyle: 'none'
                    }}>
                        {data.anomalies.slice(0, 5).map((anomaly, index) => (
                            <li key={index} style={{
                                padding: '8px 0',
                                borderBottom: index < data.anomalies.length - 1 ? '1px solid #e0e0e0' : 'none',
                                fontSize: '14px',
                                color: '#c62828'
                            }}>
                                • {anomaly}
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {data.recommendations && data.recommendations.length > 0 && (
                <div>
                    <h4 style={{
                        margin: '0 0 8px 0',
                        fontSize: '14px',
                        fontWeight: 600,
                        color: '#2e7d32'
                    }}>
                        ✅ Notas
                    </h4>
                    <ul style={{
                        margin: 0,
                        padding: '0 0 0 20px',
                        listStyle: 'none'
                    }}>
                        {data.recommendations.slice(0, 5).map((rec, index) => (
                            <li key={index} style={{
                                padding: '8px 0',
                                borderBottom: index < data.recommendations.length - 1 ? '1px solid #e0e0e0' : 'none',
                                fontSize: '14px',
                                color: '#666'
                            }}>
                                • {rec}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};
