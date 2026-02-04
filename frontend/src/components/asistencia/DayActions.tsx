import React from 'react';

interface DayActionsProps {
    employeeId: string;
    date: string;
}

export const DayActions: React.FC<DayActionsProps> = ({ employeeId, date }) => {
    return (
        <div className="card" style={{ padding: '20px' }}>
            <div style={{
                display: 'flex',
                gap: '12px',
                flexWrap: 'wrap',
                justifyContent: 'flex-start'
            }}>
                <button
                    className="primary"
                    style={{
                        padding: '12px 24px',
                        fontSize: '15px',
                        fontWeight: 600,
                        background: '#2196f3',
                        border: 'none',
                        cursor: 'not-allowed',
                        opacity: 0.7
                    }}
                    disabled
                    title="Funcionalidad disponible en Fase 2"
                >
                    ✏️ Registrar Ajuste Manual
                </button>

                <button
                    className="secondary"
                    style={{
                        padding: '12px 24px',
                        fontSize: '15px',
                        fontWeight: 600,
                        background: '#f5f5f5',
                        border: '1px solid #ccc',
                        cursor: 'not-allowed',
                        opacity: 0.7
                    }}
                    disabled
                    title="Funcionalidad disponible en Fase 2"
                >
                    📝 Agregar Nota de RRHH
                </button>

                <button
                    className="secondary"
                    onClick={() => {
                        const detailsSection = document.getElementById('day-technical-details');
                        if (detailsSection) {
                            detailsSection.style.display =
                                detailsSection.style.display === 'none' ? 'block' : 'none';
                        }
                    }}
                    style={{
                        padding: '12px 24px',
                        fontSize: '15px',
                        marginLeft: 'auto'
                    }}
                >
                    🔍 Ver Detalles Técnicos
                </button>
            </div>

            {/* Technical details section (collapsed by default) */}
            <div
                id="day-technical-details"
                style={{
                    display: 'none',
                    marginTop: '20px',
                    padding: '16px',
                    background: '#f5f5f5',
                    borderRadius: '4px',
                    fontSize: '13px',
                    color: '#666',
                    fontFamily: 'monospace'
                }}
            >
                <div style={{ marginBottom: '12px', fontWeight: 600, fontFamily: 'inherit' }}>
                    📊 Información Técnica
                </div>
                <div>
                    • <strong>Employee ID:</strong> {employeeId}<br />
                    • <strong>Fecha:</strong> {date}<br />
                    • <strong>Vista:</strong> Día de asistencia individual<br />
                    • Los detalles completos están disponibles en las secciones superiores
                </div>
            </div>

            <div style={{
                marginTop: '16px',
                padding: '12px',
                background: '#e3f2fd',
                borderRadius: '4px',
                fontSize: '13px',
                color: '#1565c0',
                borderLeft: '3px solid #2196f3'
            }}>
                ℹ️ <strong>Nota:</strong> Las funciones de ajuste manual y notas de RRHH estarán disponibles en la Fase 2 del desarrollo.
            </div>
        </div>
    );
};

