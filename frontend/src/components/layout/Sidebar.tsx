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
    'attendance': {
        title: 'Asistencia',
        items: [
            { label: 'Marcaciones', path: '/attendance/logs' },
            { label: 'Reporte Diario', path: '/attendance/reports' },
            { label: 'Calendario', path: '/attendance/schedule' },
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

    const systemItems: MenuItem[] = [
        { label: 'Ajustes', path: '/system/settings' },
        { label: 'Terminales', path: '/devices' },
        { label: 'Turnos', path: '/attendance/shifts' },
        { label: 'Horarios', path: '/attendance/timetables' },
    ];

    // Determine active module from path
    const pathSegments = location.pathname.split('/').filter(Boolean);
    let activeModule = pathSegments[0] || 'dashboard';

    // Map legacy/other paths to the 4 main sections
    if (activeModule === 'employees') activeModule = 'employees';
    if (activeModule === 'devices') activeModule = 'system';
    if (activeModule === 'access') activeModule = 'system';

    const menu = MENU_STRUCTURE[activeModule];
    const isSystemSettings = location.pathname.startsWith('/system/settings');
    const isDevices = location.pathname.startsWith('/devices');

    const resolvedMenu = activeModule === 'system'
        ? {
            ...menu,
            items: isSystemSettings
                ? systemItems.filter(item => item.path === '/system/settings')
                : isDevices
                    ? systemItems.filter(item => item.path === '/devices' || item.path === '/system/settings')
                    : systemItems
        }
        : menu;

    // Don't show sidebar for dashboard
    if (activeModule === 'dashboard' || !resolvedMenu) return null;

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
                {resolvedMenu.title} <span style={{ fontSize: '10px', color: 'red' }}>DEBUG v2.0</span>
            </div>

            <nav style={{ display: 'flex', flexDirection: 'column' }}>
                {resolvedMenu.items.map((item) => (
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
