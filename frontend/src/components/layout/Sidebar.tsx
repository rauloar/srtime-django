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
    'attendance': {
        title: 'Asistencia',
        items: [
            { label: 'Reporte Diario', path: '/attendance' }, // Defaults to daily
            { label: 'Calendario', path: '/attendance/schedule' },
            { label: 'Marcaciones', path: '/attendance/logs' },
            { label: 'Ausencias', path: '/attendance/absences' },
            // Removed technical: Timetables, Shifts, Calculation
        ]
    },
    'personnel': {
        title: 'Empleados',
        items: [
            { label: 'Lista Empleados', path: '/personnel/employees' },
            { label: 'Departamentos', path: '/personnel/departments' },
            // Simplified structure
        ]
    },
    'system': { // Maps to "Configuración" conceptually
        title: 'Configuración',
        items: [
            // { label: 'Usuarios', path: '/system/users' },  // DEV: Auth disabled
            { label: 'Ajustes', path: '/system/settings' },
            { label: 'Terminales', path: '/devices' }, // Devices moved here
            { label: 'Turnos', path: '/attendance/shifts' }, // Technical config here
            { label: 'Horarios', path: '/attendance/timetables' }, // Technical config here
        ]
    }
};

export const Sidebar: React.FC = () => {
    const location = useLocation();

    // Determine active module from path
    const pathSegments = location.pathname.split('/').filter(Boolean);
    let activeModule = pathSegments[0] || 'dashboard';

    // Map legacy/other paths to the 4 main sections
    if (activeModule === 'devices') activeModule = 'system';
    if (activeModule === 'access') activeModule = 'system';

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
                {menu.title} <span style={{ fontSize: '10px', color: 'red' }}>DEBUG v2.0</span>
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
