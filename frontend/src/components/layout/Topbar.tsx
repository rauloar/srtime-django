import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { Home, User, Monitor, Clock, Settings, LogOut, Menu, Building } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { useApp } from '../../hooks/useApp';
import { ThemeToggle } from '../ui/ThemeToggle';

interface TopbarProps {
    onMenuCheck?: () => void;
}

export const Topbar: React.FC<TopbarProps> = ({ onMenuCheck }) => {
    const navigate = useNavigate();
    const { logout } = useAuth();
    const { success } = useToast();
    const { theme, setTheme } = useApp();

    const handleLogout = () => {
        logout();
        success('Sesión cerrada correctamente');
        navigate('/login');
    };

    const handleToggleTheme = () => {
        setTheme(theme === 'light' ? 'dark' : 'light');
    };

    return (
        <header className="app-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '20px', flex: 1 }}>
                {/* Mobile Menu Toggle */}
                <button
                    className="mobile-menu-toggle"
                    onClick={onMenuCheck}
                    style={{
                        background: 'transparent',
                        border: 'none',
                        color: 'white',
                        cursor: 'pointer',
                        display: 'none' // Hidden by default, shown via CSS query
                    }}
                >
                    <Menu size={24} />
                </button>

                <div style={{ fontSize: '20px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <img src="/img/sr-logo.png" alt="Logo" style={{ height: '32px', width: 'auto' }} onError={(e) => { e.currentTarget.style.display = 'none'; e.currentTarget.nextElementSibling?.classList.remove('hidden'); }} />
                    <Monitor size={24} className="hidden" style={{ display: 'none' }} />
                    <span className="brand-text">SRTimeWeb</span>
                    <span style={{ fontSize: '12px', opacity: 0.7, fontWeight: 'normal', marginLeft: '5px' }}>by Service Reloj</span>
                </div>

                <nav className="desktop-nav" style={{ display: 'flex', height: 'var(--header-height)' }}>
                    <TabLink to="/dashboard" icon={<Home size={18} />} label="Home" />
                    <TabLink to="/access" icon={<Building size={18} />} label="Organización" />
                    <TabLink to="/personnel" icon={<User size={18} />} label="RRHH" />
                    <TabLink to="/devices" icon={<Monitor size={18} />} label="Dispositivo" />
                    <TabLink to="/attendance" icon={<Clock size={18} />} label="Asistencia" />
                    <TabLink to="/system" icon={<Settings size={18} />} label="Sistema" />
                </nav>

                {/* User & Logout */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginLeft: 'auto' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'rgba(255,255,255,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <User size={16} />
                        </div>
                        <span className="username-text" style={{ fontSize: '14px', fontWeight: 500 }}>Admin</span>
                    </div>

                    <ThemeToggle theme={theme} onToggle={handleToggleTheme} />

                    <div style={{ width: '1px', height: '20px', background: 'rgba(255,255,255,0.3)' }}></div>

                    <button
                        onClick={handleLogout}
                        style={{ background: 'transparent', border: 'none', color: 'white', padding: '4px', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
                        title="Cerrar Sesión"
                    >
                        <LogOut size={18} />
                    </button>
                </div>
            </div>
        </header>
    );
};

const TabLink: React.FC<{ to: string, icon: React.ReactNode, label: string }> = ({ to, icon, label }) => {
    return (
        <NavLink
            to={to}
            className={({ isActive }) => isActive ? 'active-tab' : 'inactive-tab'}
            style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '0 15px',
                textDecoration: 'none',
                color: 'white',
                background: isActive ? 'rgba(0,0,0,0.15)' : 'transparent',
                borderBottom: isActive ? '3px solid #bce1ff' : '3px solid transparent',
                height: '100%',
                boxSizing: 'border-box',
                opacity: isActive ? 1 : 0.8
            })}
        >
            {icon}
            {label}
        </NavLink>
    );
}
