import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

export const Breadcrumbs: React.FC = () => {
    const location = useLocation();
    const pathnames = location.pathname.split('/').filter(x => x);

    // Map strict path names to readable labels if needed
    const labelMap: { [key: string]: string } = {
        'dashboard': 'Tablero',
        'personnel': 'Personal',
        'departments': 'Departamentos',
        'employees': 'Empleados',
        'attendance': 'Asistencia',
        'timetables': 'Horarios',
        'shifts': 'Turnos',
        'schedule': 'Programación',
        'logs': 'Fichajes',
        'calculation': 'Cálculo',
        'reports': 'Resultados',
        'devices': 'Dispositivos',
        'users': 'Usuarios',
        'system': 'Sistema',
        'settings': 'Configuración'
    };

    if (pathnames.length === 0 || (pathnames.length === 1 && pathnames[0] === 'dashboard')) return null;

    return (
        <div style={{ display: 'flex', alignItems: 'center', fontSize: '13px', color: '#666', marginBottom: '15px' }}>
            <Link to="/dashboard" style={{ display: 'flex', alignItems: 'center', color: '#666', textDecoration: 'none' }}>
                <Home size={14} />
            </Link>
            {pathnames.map((value, index) => {
                const to = `/${pathnames.slice(0, index + 1).join('/')}`;
                const isLast = index === pathnames.length - 1;
                const label = labelMap[value] || value;

                return (
                    <div key={to} style={{ display: 'flex', alignItems: 'center' }}>
                        <ChevronRight size={14} style={{ margin: '0 5px' }} />
                        {isLast ? (
                            <span style={{ fontWeight: 500, color: '#333' }}>{label}</span>
                        ) : (
                            <Link to={to} style={{ color: '#666', textDecoration: 'none' }}>{label}</Link>
                        )}
                    </div>
                );
            })}
        </div>
    );
};
