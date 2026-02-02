import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, ChevronRight, Calendar } from 'lucide-react';

interface DayNavigationProps {
    currentDate: string;
    employeeId: string;
}

export const DayNavigation: React.FC<DayNavigationProps> = ({ currentDate, employeeId }) => {
    const navigate = useNavigate();

    const getPreviousDay = () => {
        const date = new Date(currentDate);
        date.setDate(date.getDate() - 1);
        return date.toISOString().split('T')[0];
    };

    const getNextDay = () => {
        const date = new Date(currentDate);
        date.setDate(date.getDate() + 1);
        return date.toISOString().split('T')[0];
    };

    const goToDay = (newDate: string) => {
        navigate(`/asistencia/empleado/${employeeId}/dia/${newDate}`);
    };

    const goToToday = () => {
        const today = new Date().toISOString().split('T')[0];
        goToDay(today);
    };

    const isToday = currentDate === new Date().toISOString().split('T')[0];

    return (
        <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '12px 0'
        }}>
            <button
                onClick={() => goToDay(getPreviousDay())}
                className="secondary"
                style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '8px 16px'
                }}
            >
                <ChevronLeft size={18} />
                Día Anterior
            </button>

            <button
                onClick={goToToday}
                className={isToday ? 'primary' : 'secondary'}
                disabled={isToday}
                style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '8px 16px'
                }}
            >
                <Calendar size={18} />
                Hoy
            </button>

            <button
                onClick={() => goToDay(getNextDay())}
                className="secondary"
                style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '8px 16px'
                }}
            >
                Día Siguiente
                <ChevronRight size={18} />
            </button>
        </div>
    );
};
