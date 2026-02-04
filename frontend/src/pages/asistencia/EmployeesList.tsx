import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getEmployees } from '../../api';
import type { Employee } from '../../api';
import './asistencia.css';

export function EmployeesList() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const loadEmployees = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getEmployees(0, 100);
        setEmployees(data);
      } catch (err) {
        setError(`Error cargando empleados: ${err instanceof Error ? err.message : 'Error desconocido'}`);
      } finally {
        setLoading(false);
      }
    };

    loadEmployees();
  }, []);

  const filteredEmployees = employees.filter(emp =>
    (emp.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
     emp.user_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
     emp.email?.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (loading) {
    return <div className="asistencia-loading">Cargando empleados...</div>;
  }

  if (error) {
    return <div className="asistencia-error">{error}</div>;
  }

  if (employees.length === 0) {
    return <div className="asistencia-empty">No hay empleados disponibles</div>;
  }

  return (
    <div className="asistencia-container">
      <div className="asistencia-header">
        <h1>Empleados - Visualización de Asistencia</h1>
        <p className="asistencia-subtitle">Selecciona un empleado para ver sus registros de asistencia</p>
      </div>

      <div className="asistencia-search-box">
        <input
          type="text"
          placeholder="Buscar por nombre, ID o email..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="asistencia-search-input"
        />
        <span className="asistencia-search-count">{filteredEmployees.length} de {employees.length}</span>
      </div>

      <div className="asistencia-list">
        {filteredEmployees.length === 0 ? (
          <div className="asistencia-empty">No hay resultados que coincidan con la búsqueda</div>
        ) : (
          <table className="asistencia-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Nombre</th>
                <th>Email</th>
                <th>Departamento</th>
                <th>Activo</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filteredEmployees.map(emp => (
                <tr key={emp.id}>
                  <td className="cell-id">{emp.user_id}</td>
                  <td className="cell-name">{emp.name || '—'}</td>
                  <td className="cell-email">{emp.email || '—'}</td>
                  <td className="cell-dept">{emp.department_name || '—'}</td>
                  <td className="cell-status">
                    <span className={`badge ${emp.active ? 'badge-active' : 'badge-inactive'}`}>
                      {emp.active ? 'Sí' : 'No'}
                    </span>
                  </td>
                  <td className="cell-actions">
                    <Link
                      to={`/employees/${emp.user_id}`}
                      className="link-button"
                    >
                      Ver
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
