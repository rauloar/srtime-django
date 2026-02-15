import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { DayHeader } from '../../components/asistencia/DayHeader';
import { DayTimeline } from '../../components/asistencia/DayTimeline';
import { DayPunchList } from '../../components/asistencia/DayPunchList';
import { DayActions } from '../../components/asistencia/DayActions';
import { DayNavigation } from '../../components/asistencia/DayNavigation';
import { getDayView, type DayViewResponse } from '../../api';

// Using DayViewResponse from api.ts
type DayViewData = DayViewResponse;

export const DayViewPage: React.FC = () => {
    const { employeeId, date } = useParams<{ employeeId: string; date: string }>();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [data, setData] = useState<DayViewData | null>(null);

    useEffect(() => {
        if (!employeeId || !date) {
            setError('Parámetros inválidos');
            setLoading(false);
            return;
        }

        // Validate that parameters don't contain placeholder literals
        if (employeeId.includes('{') || employeeId.includes('}') || 
            date.includes('{') || date.includes('}')) {
            setError('Parámetros inválidos');
            setLoading(false);
            return;
        }

        const fetchData = async () => {
            setLoading(true);
            try {
                const data = await getDayView(employeeId, date);
                setData(data);
                setError(null);
            } catch (err) {
                setError("Error al cargar datos. Verifique conexión con el servidor.");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [employeeId, date]);

    if (error) {
        return (
            <div style={{ padding: '40px', textAlign: 'center' }}>
                <h2>Error</h2>
                <p>{error}</p>
                <button onClick={() => navigate('/attendance/reports')}>
                    Volver a reportes
                </button>
            </div>
        );
    }

    if (loading || !data) {
        return <div style={{ padding: '40px', textAlign: 'center' }}>Cargando día laboral...</div>;
    }

    return (
        <div style={{
            maxWidth: '1200px',
            margin: '0 auto',
            padding: '20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '20px'
        }}>
            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                <button 
                    onClick={() => navigate('/attendance/reports')} 
                    className="secondary"
                    style={{ fontSize: '14px' }}
                >
                    ← Volver a Reportes
                </button>
            </div>

            <DayNavigation
                currentDate={date!}
                employeeId={employeeId!}
            />

            {/* Pass REAL data to Header */}
            <DayHeader
                employeeId={employeeId!}
                date={date!}
                // @ts-ignore - passing extra props for now until components update
                employeeName={data.employee_name}
                status={data.status}
                workedMinutes={data.worked_minutes}
            />

            {/* Pass REAL logs to Timeline */}
            <DayTimeline
                employeeId={employeeId!}
                date={date!}
                // @ts-ignore
                logs={data.logs}
            />

            {/* Pass REAL logs to List */}
            <DayPunchList
                employeeId={employeeId!}
                date={date!}
                // @ts-ignore
                logs={data.logs}
            />

            <DayActions
                employeeId={employeeId!}
                date={date!}
            />
        </div>
    );
};
