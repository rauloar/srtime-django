import React, { useEffect, useState } from 'react';
import { getDailyReports } from '../../api';

interface DayActionsProps {
    employeeId: string;
    date: string;
}

export const DayActions: React.FC<DayActionsProps> = ({ employeeId, date }) => {
    const [hasProblems, setHasProblems] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const checkProblems = async () => {
            try {
                const results = await getDailyReports(date, date);
                const employeeData = results.find(r => r.employee_id?.toString() === employeeId);

                if (employeeData) {
                    // Consider day has problems if status is not Normal
                    const problematicStatuses = ['Late', 'Absent', 'Early', 'Partial'];
                    setHasProblems(problematicStatuses.includes(employeeData.status));
                }
            } catch (err) {
                console.error('Error checking day problems:', err);
                setHasProblems(false);
            } finally {
                setLoading(false);
            }
        };

        checkProblems();
    }, [employeeId, date]);

    if (loading) {
        return null;
    }

    return (
        <div className="card" style={{ padding: '20px' }}>
            <div style={{
                display: 'flex',
                gap: '12px',
                flexWrap: 'wrap',
                justifyContent: hasProblems ? 'space-between' : 'flex-end'
            }}>
                {hasProblems && (
                    <button
                        className="primary"
                        style={{
                            padding: '12px 24px',
                            fontSize: '15px',
                            fontWeight: 600,
                            background: '#ed6c02',
                            border: 'none',
                            cursor: 'not-allowed',
                            opacity: 0.7
                        }}
                        disabled
                        title="Funcionalidad disponible en Fase 2"
                    >
                        📝 Corregir Fichadas
                    </button>
                )}

                <button
                    className="secondary"
                    onClick={() => {
                        const detailsSection = document.getElementById('day-details');
                        if (detailsSection) {
                            detailsSection.style.display =
                                detailsSection.style.display === 'none' ? 'block' : 'none';
                        }
                    }}
                    style={{
                        padding: '12px 24px',
                        fontSize: '15px'
                    }}
                >
                    📄 Ver Detalles Técnicos
                </button>
            </div>

            {/* Technical details section (collapsed by default) */}
            <div
                id="day-details"
                style={{
                    display: 'none',
                    marginTop: '20px',
                    padding: '16px',
                    background: '#f5f5f5',
                    borderRadius: '4px',
                    fontSize: '13px',
                    color: '#666'
                }}
            >
                <div style={{ marginBottom: '12px', fontWeight: 600 }}>
                    Información Técnica
                </div>
                <div>
                    • Employee ID: {employeeId}<br />
                    • Fecha: {date}<br />
                    • Los detalles completos están disponibles en las secciones superiores
                </div>
            </div>

            {hasProblems && (
                <div style={{
                    marginTop: '16px',
                    padding: '12px',
                    background: '#fff3e0',
                    borderRadius: '4px',
                    fontSize: '13px',
                    color: '#ed6c02'
                }}>
                    ℹ️ <strong>Nota:</strong> La función "Corregir Fichadas" estará disponible en la Fase 2 del desarrollo.
                </div>
            )}
        </div>
    );
};

