import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useEffect } from 'react';
import { api } from './api';
import { MainLayout } from './components/layout/MainLayout';
import { Dashboard } from './pages/Dashboard';
import { Analytics } from './pages/Analytics';
import { Users } from './pages/Users';
import { DeviceDetail } from './pages/DeviceDetail';
import { DeviceList } from './pages/DeviceList';
import { Departments } from './pages/personnel/Departments';
import { Employees } from './pages/personnel/Employees';
import { Settings } from './pages/system/Settings';
// import { Users as SystemUsers } from './pages/system/Users';  // DEV: Auth disabled
import { Logs } from './pages/Logs';
// import { Login } from './pages/auth/Login';  // DEV: Auth disabled
import { PrivateRoute } from './components/auth/PrivateRoute';
import { Positions } from './pages/organization/Positions';
import { Zones } from './pages/organization/Zones';
import { Timetables } from './pages/asistencia/Timetables';
import { Shifts } from './pages/asistencia/Shifts';
import { EmployeeSchedule } from './pages/asistencia/EmployeeSchedule';
import { Calculation } from './pages/asistencia/Calculation';
import { Reports } from './pages/asistencia/Reports';
import { Absences } from './pages/asistencia/Absences';
import { DayViewPage } from './pages/asistencia/DayViewPage'; // Kept as is, was already there
import { ToastProvider } from './contexts/ToastContext';
import { AuthProvider } from './contexts/AuthContext';
import { AppProvider } from './contexts/AppContext';
import { ErrorBoundary } from './components/ErrorBoundary/ErrorBoundary';
import { useSessionSecurity } from './hooks/useSessionSecurity';
import './App.css';

function AppContent() {
  const location = useLocation();
  const locationState = location.state as { message?: string } | null;
  useSessionSecurity();

  // Fetch CSRF token on app load
  useEffect(() => {
    const fetchCSRFToken = async () => {
      try {
        await api.get('/csrf/');
        // Token is automatically set as cookie by Django
      } catch (error) {
        console.error('Failed to fetch CSRF token:', error);
      }
    };
    fetchCSRFToken();
  }, []);

  return (
    <>
      {locationState?.message && (
        <div style={{
          padding: '12px 16px',
          margin: '16px',
          backgroundColor: 'var(--status-warning)',
          color: 'white',
          borderRadius: 'var(--border-radius)',
          fontSize: '14px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <span>{locationState.message}</span>
        </div>
      )}
      <Routes>
        {/* DEV: Auth disabled */}
        {/* <Route path="/login" element={<Login />} /> */}

        <Route path="/" element={
          <PrivateRoute>
            <MainLayout />
          </PrivateRoute>
        }>
          {/* Default redirect to dashboard */}
          <Route index element={<Navigate to="/dashboard" replace />} />

          <Route path="dashboard" element={<Dashboard />} />
          <Route path="analytics" element={<Analytics />} />

          {/* Device Module */}
          <Route path="devices" element={<DeviceList />} />
          <Route path="devices/:id" element={<DeviceDetail />} />
          <Route path="devices/:id/users" element={<Users />} />

          {/* Personnel Module - Organization Management (Hierarchical Order) */}
          <Route path="personnel" element={<Navigate to="/personnel/departments" replace />} />
          <Route path="personnel/departments" element={<Departments />} />
          <Route path="personnel/shifts" element={<Shifts />} />
          <Route path="personnel/timetables" element={<Timetables />} />
          <Route path="personnel/employees" element={<Employees />} />

          {/* Attendance Module */}
          <Route path="attendance" element={<Navigate to="/attendance/logs" replace />} />
          <Route path="attendance/logs" element={<Logs />} />
          <Route path="attendance/schedule" element={<EmployeeSchedule />} />
          <Route path="attendance/absences" element={<Absences />} />
          <Route path="attendance/calculation" element={<Calculation />} />
          <Route path="attendance/reports" element={<Reports />} />

          {/* Asistencia Module (Legacy) */}
          <Route path="asistencia">
            <Route path="empleado/:employeeId/dia/:date" element={<DayViewPage />} />
          </Route>

          {/* Organization Module (Legacy routes for Positions/Zones) */}
          <Route path="access" element={<Navigate to="/personnel/departments" replace />} />
          <Route path="access/positions" element={<Positions />} />
          <Route path="access/zones" element={<Zones />} />

          {/* System Module */}
          <Route path="system" element={<Navigate to="/system/settings" replace />} />
          <Route path="system/settings" element={<Settings />} />
          {/* DEV: Auth disabled */}
          {/* <Route path="system/users" element={<SystemUsers />} /> */}
        </Route>
      </Routes>
    </>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <AppProvider>
          <ToastProvider>
            <Router>
              <AppContent />
            </Router>
          </ToastProvider>
        </AppProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
