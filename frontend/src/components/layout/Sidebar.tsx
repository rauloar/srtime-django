import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';

interface MenuItem {
    label: string;
    path: string;
}

const MENU_STRUCTURE: { [key: string]: { title: string, items: MenuItem[] } } = {
    'personnel': {
        title: 'Personal',
        items: [
            { label: 'Departamentos', path: '/personnel/departments' },
            { label: 'Empleados', path: '/personnel/employees' },
        ]
    },
    'devices': {
        title: 'Dispositivo',
        items: [
            { label: 'Terminales', path: '/devices' }, // Root of devices
        ]
    },
    'attendance': {
        title: 'Asistencia',
        items: [
            { label: 'Horarios', path: '/attendance/timetables' },
            { label: 'Turnos', path: '/attendance/shifts' },
            { label: 'Calendario', path: '/attendance/schedule' },
            { label: 'Marcaciones', path: '/attendance/logs' },
            { label: 'Cálculo', path: '/attendance/calculation' },
            { label: 'Reportes', path: '/attendance/reports' },
            { label: 'Ausencias', path: '/attendance/absences' },
        ]
    },
    'access': {
        title: 'Organización',
        items: [
            { label: 'Empresa', path: '/access/company' },
            { label: 'Departamentos', path: '/access/departments' },
            { label: 'Cargos', path: '/access/positions' },
            { label: 'Zonas', path: '/access/zones' },
        ]
    },
    'system': {
        title: 'Sistema',
        items: [
            { label: 'Usuarios Sistema', path: '/system/users' },
            { label: 'Configuración', path: '/system/settings' },
        ]
    },
    'dashboard': {
        title: 'Módulos',
        items: []
    }
};

export const Sidebar: React.FC = () => {
    const location = useLocation();

    // Determine active module from path
    const pathSegments = location.pathname.split('/').filter(Boolean);
    const activeModule = pathSegments[0] || 'dashboard';

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
