import React, { useContext } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Topbar } from './Topbar';
import { Sidebar } from './Sidebar';
import { ToastContainer } from '../Toast/ToastContainer';
import { ToastContext } from '../../contexts/ToastContext';

export const MainLayout: React.FC = () => {
    const toastCtx = useContext(ToastContext);
    const location = useLocation();
    const isDashboard = location.pathname === '/dashboard';

    return (
        <div className="app-root">
            <Topbar />

            <div className={`app-content-wrapper ${isDashboard ? 'dashboard-layout' : ''}`}>
                {!isDashboard && (
                    <div className="sidebar-wrapper">
                        <Sidebar />
                    </div>
                )}

                <main className={`main-content-area ${isDashboard ? 'dashboard-fullwidth' : ''}`}>
                    <div className="content-container">
                        <div style={{ flex: 1, position: 'relative' }}>
                            <Outlet />
                        </div>
                    </div>
                </main>
            </div>

            {toastCtx && (
                <ToastContainer 
                    toasts={toastCtx.toasts} 
                    onDismiss={toastCtx.removeToast} 
                />
            )}
        </div>
    );
};
