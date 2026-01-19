import { Link, Outlet, useLocation } from 'react-router-dom';
import { FileText, Users, Server } from 'lucide-react';
import { MessageConsole } from './MessageConsole';

export function Layout() {
    const location = useLocation();

    const isActive = (path: string) => location.pathname === path || (path !== '/' && location.pathname.startsWith(path));

    return (
        <div className="layout">
            <aside className="sidebar">
                <h2 style={{ padding: '0 15px', marginBottom: '20px' }}>ZK TimeNet</h2>
                <nav>
                    <Link to="/" className={`nav-link ${isActive('/') ? 'active' : ''}`}>
                        <Server size={20} />
                        Terminales
                    </Link>
                    <Link to="/logs" className={`nav-link ${isActive('/logs') ? 'active' : ''}`}>
                        <FileText size={20} />
                        Attendance Logs
                    </Link>
                    <Link to="/devices/1/users" className={`nav-link ${isActive('/devices/1/users') ? 'active' : ''}`}>
                        <Users size={20} />
                        Usuarios
                    </Link>
                </nav>
            </aside>
            <main className="content">
                <Outlet />
            </main>
            <MessageConsole />
        </div>
    );
}
