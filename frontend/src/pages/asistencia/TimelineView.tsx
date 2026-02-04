import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getTimeline, getExplanation, api } from '../../api';
import type { TimelineData, ExplanationData } from '../../api';
import './asistencia.css';

export function TimelineView() {
  const { id, date } = useParams<{ id: string; date: string }>();
  const [timeline, setTimeline] = useState<TimelineData | null>(null);
  const [explanation, setExplanation] = useState<ExplanationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [employeeName, setEmployeeName] = useState<string>('');

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        if (id && date) {
          // Get employee name
          const empRes = await api.get(`/employees/${id}`);
          setEmployeeName(empRes.data.name || empRes.data.user_id);

          // Get timeline
          const timelineData = await getTimeline(id, date);
          setTimeline(timelineData);

          // Get explanation
          const explanationData = await getExplanation(id, date);
          setExplanation(explanationData);
        }
      } catch (err) {
        setError(`Error cargando timeline: ${err instanceof Error ? err.message : 'Error desconocido'}`);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [id, date]);

  const formatTime = (timeStr: string): string => {
    try {
      const date = new Date(timeStr);
      return date.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' });
    } catch {
      return timeStr;
    }
  };

  if (loading) {
    return <div className="asistencia-loading">Cargando timeline...</div>;
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
        <h1>Timeline de Asistencia</h1>
        <p className="asistencia-subtitle">{employeeName} - {date}</p>
      </div>

      {!timeline || !timeline.blocks || timeline.blocks.length === 0 ? (
        <div className="asistencia-empty">
          Sin registros en el timeline para esta fecha
        </div>
      ) : (
        <>
          <div className="timeline-container">
            <div className="timeline-header">
              <h3>Bloques de Tiempo Registrados</h3>
              <span className="timeline-count">{timeline.blocks.length} bloque(s)</span>
            </div>

            <div className="timeline-blocks">
              {timeline.blocks.map((block, index) => (
                <div key={index} className="timeline-block">
                  <div className="block-type">
                    <span className={`type-badge type-${block.type?.toLowerCase()}`}>
                      {block.type}
                    </span>
                  </div>
                  <div className="block-times">
                    <div className="time-item">
                      <span className="time-label">Inicio:</span>
                      <span className="time-value">{formatTime(block.start_time)}</span>
                    </div>
                    <div className="time-item">
                      <span className="time-label">Fin:</span>
                      <span className="time-value">{formatTime(block.end_time)}</span>
                    </div>
                    <div className="time-item">
                      <span className="time-label">Duración:</span>
                      <span className="time-value">{block.duration_minutes} min</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {explanation && (
            <div className="explanation-container">
              <div className="explanation-header">
                <h3>Análisis y Explicación</h3>
              </div>

              {explanation.summary && (
                <div className="explanation-section">
                  <h4>Resumen</h4>
                  <p className="summary-text">{explanation.summary}</p>
                </div>
              )}

              {explanation.anomalies && explanation.anomalies.length > 0 && (
                <div className="explanation-section">
                  <h4>Anomalías Detectadas</h4>
                  <ul className="anomalies-list">
                    {explanation.anomalies.map((anomaly, idx) => (
                      <li key={idx} className="anomaly-item">{anomaly}</li>
                    ))}
                  </ul>
                </div>
              )}

              {explanation.recommendations && explanation.recommendations.length > 0 && (
                <div className="explanation-section">
                  <h4>Recomendaciones</h4>
                  <ul className="recommendations-list">
                    {explanation.recommendations.map((rec, idx) => (
                      <li key={idx} className="recommendation-item">{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          <div className="action-buttons" style={{ marginTop: '20px' }}>
            <Link
              to={`/employees/${id}/day/${date}`}
              className="button button-secondary"
            >
              Ver Resumen del Día
            </Link>
            <Link
              to={`/employees/${id}`}
              className="button button-secondary"
            >
              Volver
            </Link>
          </div>
        </>
      )}
    </div>
  );
}
