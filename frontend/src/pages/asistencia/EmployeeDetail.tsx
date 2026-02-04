import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getEmployee } from '../../api';
import type { Employee } from '../../api';
import './asistencia.css';

export function EmployeeDetail() {
  const { id } = useParams<{ id: string }>();
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);

  useEffect(() => {
    const loadEmployee = async () => {
      try {
        setLoading(true);
        setError(null);
        if (id) {
          const data = await getEmployee(parseInt(id));
          setEmployee(data);
        }
      } catch (err) {
        setError(`Error cargando empleado: ${err instanceof Error ? err.message : 'Error desconocido'}`);
      } finally {
        setLoading(false);
      }
    };

    loadEmployee();
  }, [id]);

  if (loading) {
    return <div className="asistencia-loading">Cargando empleado...</div>;
  }

  if (error) {
    return <div className="asistencia-error">{error}</div>;
  }

  if (!employee) {
    return <div className="asistencia-empty">Empleado no encontrado</div>;
  }

  return (
    <div className="asistencia-container">
      <div className="asistencia-back">
        <Link to="/employees" className="link-back">← Volver a Empleados</Link>
      </div>

      <div className="employee-detail-card">
        <div className="employee-header">
          <div className="employee-info">
            <h1>{employee.name || 'Sin nombre'}</h1>
            <p className="employee-id">ID: {employee.user_id}</p>
          </div>
          <div className={`employee-status ${employee.active ? 'active' : 'inactive'}`}>
            {employee.active ? 'Activo' : 'Inactivo'}
          </div>
        </div>

        <div className="employee-grid">
          <div className="info-group">
            <span className="label">Email</span>
            <span className="value">{employee.email || '—'}</span>
          </div>
          <div className="info-group">
            <span className="label">Departamento</span>
            <span className="value">{employee.department_name || '—'}</span>
          </div>
          <div className="info-group">
            <span className="label">Teléfono</span>
            <span className="value">{employee.phone || '—'}</span>
          </div>
          <div className="info-group">
            <span className="label">Móvil</span>
            <span className="value">{employee.mobile_phone || '—'}</span>
          </div>
          <div className="info-group">
            <span className="label">Documento</span>
            <span className="value">{employee.ssn || '—'}</span>
          </div>
          <div className="info-group">
            <span className="label">Género</span>
            <span className="value">{employee.gender || '—'}</span>
          </div>
          <div className="info-group">
            <span className="label">Cumpleaños</span>
            <span className="value">{employee.birthday || '—'}</span>
          </div>
          <div className="info-group">
            <span className="label">Dirección</span>
            <span className="value">{employee.address || '—'}</span>
          </div>
        </div>
      </div>

      <div className="asistencia-header" style={{ marginTop: '32px' }}>
        <h2>Visualización de Asistencia</h2>
      </div>

      <div className="date-selector-box">
        <label htmlFor="date-input">Selecciona una fecha:</label>
        <input
          id="date-input"
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          className="date-input"
        />
        <div className="action-buttons">
          <Link
            to={`/employees/${employee.user_id}/day/${selectedDate}`}
            className="button button-primary"
          >
            Ver Día
          </Link>
          <Link
            to={`/employees/${employee.user_id}/timeline/${selectedDate}`}
            className="button button-secondary"
          >
            Ver Timeline
          </Link>
        </div>
      </div>
    </div>
  );
}
