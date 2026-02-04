import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { DayHeader } from '../../components/asistencia/DayHeader';
import { DayTimeline } from '../../components/asistencia/DayTimeline';
import { DayExplanation } from '../../components/asistencia/DayExplanation';
import { DayPunchList } from '../../components/asistencia/DayPunchList';
import { DayActions } from '../../components/asistencia/DayActions';
import { DayNavigation } from '../../components/asistencia/DayNavigation';
import { api } from '../../api';

interface DayViewData {
    employee_id: string;
    employee_name: string;
    date: string;
    status: string;
    worked_minutes: number;
    logs: Array<{ type: string; time: string }>;
}

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
                // Use params object instead of template string to safely encode parameters
                const response = await api.get('/attendance/day/', {
                    params: {
                        employee_id: employeeId,
                        date: date
                    }
                });
                setData(response.data);
                setError(null);
            } catch (err) {
                console.error("Error fetching day view:", err);
                setError("Error al cargar datos. Verifique conexión con Django.");
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
                <button onClick={() => navigate('/asistencia/buscar')}>
                    Volver a búsqueda
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

            {/* Explanation - Keep generic for now */}
            <DayExplanation
                employeeId={employeeId!}
                date={date!}
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
