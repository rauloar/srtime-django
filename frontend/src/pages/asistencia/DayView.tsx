import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../../api';
import type { DailyAttendance } from '../../api';
import './asistencia.css';

export function DayView() {
  const { id, date } = useParams<{ id: string; date: string }>();
  const [dayData, setDayData] = useState<DailyAttendance | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [employeeName, setEmployeeName] = useState<string>('');

  useEffect(() => {
    const loadDayData = async () => {
      try {
        setLoading(true);
        setError(null);
        if (!id || !date || id.includes('{') || date.includes('{') || id.includes('}') || date.includes('}')) {
          setError('Parámetros inválidos');
          setDayData(null);
          return;
        }

        if (id && date) {
          // Get employee name
          const empRes = await api.get(`/employees/${id}`);
          setEmployeeName(empRes.data.name || empRes.data.user_id);

          // Get daily attendance for specific date
          const attendanceRes = await api.get('/attendance/day/', {
            params: {
              employee_id: id,
              date
            }
          });

          const data = attendanceRes.data as DailyAttendance | DailyAttendance[] | null;
          if (Array.isArray(data)) {
            setDayData(data.length > 0 ? data[0] : null);
          } else if (data && typeof data === 'object' && Object.keys(data).length === 0) {
            setDayData(null);
          } else {
            setDayData(data ?? null);
          }
        }
      } catch (err) {
        setError(`Error cargando datos del día: ${err instanceof Error ? err.message : 'Error desconocido'}`);
      } finally {
        setLoading(false);
      }
    };

    loadDayData();
  }, [id, date]);

  if (loading) {
    return <div className="asistencia-loading">Cargando datos del día...</div>;
  }

  if (error) {
    return <div className="asistencia-error">{error}</div>;
  }

  return (
    <div className="asistencia-container">
      <div className="asistencia-back">
        <Link to={`/employees/${id}`} className="link-back">← Volver a Detalle</Link>
      </div>

      <div className="asistencia-header">
        <h1>Registros del Día</h1>
        <p className="asistencia-subtitle">{employeeName} - {date}</p>
      </div>

      {!dayData ? (
        <div className="asistencia-empty">
          No hay registros de asistencia para esta fecha
        </div>
      ) : (
        <div className="day-view-card">
          <div className="day-summary">
            <div className="summary-item">
              <span className="label">Fecha</span>
              <span className="value">{dayData.date}</span>
            </div>
            <div className="summary-item">
              <span className="label">Estado</span>
              <span className={`value status-badge status-${dayData.status?.toLowerCase()}`}>
                {dayData.status}
              </span>
            </div>
            <div className="summary-item">
              <span className="label">Minutos Trabajados</span>
              <span className="value">{dayData.worked_minutes} min</span>
            </div>
            <div className="summary-item">
              <span className="label">Minutos de Atraso</span>
              <span className="value">{dayData.late_minutes} min</span>
            </div>
            <div className="summary-item">
              <span className="label">Minutos de Salida Temprana</span>
              <span className="value">{dayData.early_minutes} min</span>
            </div>
            <div className="summary-item">
              <span className="label">Horas Extra</span>
              <span className="value">{dayData.overtime_minutes} min</span>
            </div>
            <div className="summary-item">
              <span className="label">Hora de Entrada</span>
              <span className="value">{dayData.check_in ? new Date(dayData.check_in).toLocaleTimeString() : '—'}</span>
            </div>
            <div className="summary-item">
              <span className="label">Hora de Salida</span>
              <span className="value">{dayData.check_out ? new Date(dayData.check_out).toLocaleTimeString() : '—'}</span>
            </div>
          </div>

          {dayData.exception_reason && (
            <div className="exception-box">
              <h3>Observación</h3>
              <p>{dayData.exception_reason}</p>
            </div>
          )}

          {dayData.is_absent && (
            <div className="absent-notice">
              ⚠️ Empleado ausente en esta fecha
            </div>
          )}

          {dayData.schedule_type && (
            <div className="schedule-info">
              <strong>Tipo de Horario:</strong> {dayData.schedule_type}
            </div>
          )}

          <div className="action-buttons" style={{ marginTop: '20px' }}>
            <Link
              to={`/employees/${id}/timeline/${date}`}
              className="button button-primary"
            >
              Ver Timeline
            </Link>
            <Link
              to={`/employees/${id}`}
              className="button button-secondary"
            >
              Volver
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
