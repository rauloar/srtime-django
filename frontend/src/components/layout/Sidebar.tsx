import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

interface MenuItem {
    label: string;
    path: string;
    allowedGroups?: string[];
}

const MENU_STRUCTURE: { [key: string]: { title: string, items: MenuItem[] } } = {
    'dashboard': {
        title: 'Principal',
        items: []
    },
    'personnel': {
        title: 'Organización',
        items: [
            { label: 'Empresas', path: '/personnel/company', allowedGroups: ['admin_system', 'hr_manager'] },
            { label: 'Departamentos', path: '/personnel/departments', allowedGroups: ['admin_system', 'hr_manager'] },
            { label: 'Horarios', path: '/personnel/timetables', allowedGroups: ['admin_system', 'hr_manager'] },
            { label: 'Turnos', path: '/personnel/shifts', allowedGroups: ['admin_system', 'hr_manager'] },
            { label: 'Empleados', path: '/personnel/employees', allowedGroups: ['admin_system', 'hr_manager'] },
            { label: 'Asignación Individual', path: '/attendance/schedule', allowedGroups: ['admin_system', 'hr_manager'] },
        ]
    },
    'attendance': {
        title: 'Asistencia',
        items: [
            { label: 'Marcaciones', path: '/attendance/logs', allowedGroups: ['admin_system', 'hr_manager', 'attendance_admin', 'viewer'] },
            { label: 'Reporte Diario', path: '/attendance/reports', allowedGroups: ['admin_system', 'hr_manager', 'attendance_admin', 'viewer'] },
            { label: 'Ausencias', path: '/attendance/absences', allowedGroups: ['admin_system', 'hr_manager', 'attendance_admin', 'viewer'] },
        ]
    },
    'system': {
        title: 'Configuración',
        items: [
            { label: 'Ajustes', path: '/system/settings', allowedGroups: ['admin_system'] },
        ]
    }
};

export const Sidebar: React.FC = () => {
    const location = useLocation();
    const { groups, isSuperuser } = useAuth();

    const hasGroup = (allowed?: string[]) => {
        if (!allowed || allowed.length === 0) return true;
        if (isSuperuser) return true;
        return allowed.some((group) => groups.includes(group));
    };

    // Determine active module from path
    const pathSegments = location.pathname.split('/').filter(Boolean);
    let activeModule = pathSegments[0] || 'dashboard';

    // Map legacy/other paths to main sections
    if (activeModule === 'devices') activeModule = 'system';
    if (activeModule === 'attendance' && pathSegments[1] === 'schedule') activeModule = 'personnel';

    const menu = MENU_STRUCTURE[activeModule];

    // Don't show sidebar for dashboard
    if (activeModule === 'dashboard' || !menu) return null;

    const visibleItems = menu.items.filter((item) => hasGroup(item.allowedGroups));

    if (visibleItems.length === 0) return null;

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
                {visibleItems.map((item) => (
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
