import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';

interface MenuItem {
    label: string;
    path: string;
}

const MENU_STRUCTURE: { [key: string]: { title: string, items: MenuItem[] } } = {
    'dashboard': {
        title: 'Principal',
        items: []
    },
    'employees': {
        title: 'Visualización',
        items: [
            { label: 'Empleados', path: '/employees' },
        ]
    },
    'personnel': {
        title: 'Organización',
        items: [
            { label: 'Departamentos', path: '/personnel/departments' },
            { label: 'Horarios', path: '/personnel/timetables' },
            { label: 'Turnos', path: '/personnel/shifts' },
            { label: 'Empleados', path: '/personnel/employees' },
            { label: 'Asignación Individual', path: '/attendance/schedule' },
        ]
    },
    'attendance': {
        title: 'Asistencia',
        items: [
            { label: 'Marcaciones', path: '/attendance/logs' },
            { label: 'Reporte Diario', path: '/attendance/reports' },
            { label: 'Ausencias', path: '/attendance/absences' },
        ]
    },
    'system': {
        title: 'Configuración',
        items: [
            { label: 'Ajustes', path: '/system/settings' },
            { label: 'Terminales', path: '/devices' },
        ]
    }
};

export const Sidebar: React.FC = () => {
    const location = useLocation();

    // Determine active module from path
    const pathSegments = location.pathname.split('/').filter(Boolean);
    let activeModule = pathSegments[0] || 'dashboard';

    // Map legacy/other paths to main sections
    if (activeModule === 'employees') activeModule = 'employees';
    if (activeModule === 'devices') activeModule = 'system';
    if (activeModule === 'access') activeModule = 'system';
    if (activeModule === 'attendance' && pathSegments[1] === 'schedule') activeModule = 'personnel';

    const menu = MENU_STRUCTURE[activeModule];

    // Don't show sidebar for dashboard
    if (activeModule === 'dashboard' || !menu) return null;

    return (
        <aside style={{
            display: 'flex',
            flexDirection: 'column',
            padding: '20px 0',
            height: '100%'
        }}>
            <div style={{
                padding: '0 20px 10px 20px',
                fontWeight: 'bold',
                color: '#5c6b77',
                textTransform: 'uppercase',
                fontSize: '12px',
                borderBottom: '1px solid var(--border-color)',
                marginBottom: '10px'
            }}>
                {menu.title}
            </div>

            <nav style={{ display: 'flex', flexDirection: 'column' }}>
                {menu.items.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        end
                        style={({ isActive }) => ({
                            padding: '10px 20px',
                            textDecoration: 'none',
                            color: isActive ? 'var(--sidebar-active-text)' : 'var(--sidebar-text)',
                            backgroundColor: isActive ? 'var(--sidebar-active-bg)' : 'transparent',
                            borderLeft: isActive ? '3px solid var(--sidebar-active-border)' : '3px solid transparent',
                            fontSize: '14px',
                            fontWeight: isActive ? 500 : 400
                        })}
                    >
                        {item.label}
                    </NavLink>
                ))}
            </nav>
        </aside>
    );
};
