import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useEffect } from 'react';
import { api } from './api';
import { MainLayout } from './components/layout/MainLayout';
import { Dashboard } from './pages/Dashboard';
import { DeviceDetail } from './pages/DeviceDetail';
import { DeviceList } from './pages/DeviceList';
import { Companies } from './pages/personnel/Companies';
import { Departments } from './pages/personnel/Departments';
import { Employees } from './pages/personnel/Employees';
import { Settings } from './pages/system/Settings';
import { Logs } from './pages/Logs';
import { PrivateRoute } from './components/auth/PrivateRoute';
import { Timetables } from './pages/asistencia/Timetables';
import { Shifts } from './pages/asistencia/Shifts';
import { EmployeeSchedule } from './pages/asistencia/EmployeeSchedule';
import { Reports } from './pages/asistencia/Reports';
import { Absences } from './pages/asistencia/Absences';
import { DayViewPage } from './pages/asistencia/DayViewPage';
import { ToastProvider } from './contexts/ToastContext';
import { AuthProvider } from './contexts/AuthContext';
import { AppProvider } from './contexts/AppContext';
import { ErrorBoundary } from './components/ErrorBoundary/ErrorBoundary';
import { useSessionSecurity } from './hooks/useSessionSecurity';
import { Login } from './pages/auth/Login';
import './App.css';

function AppContent() {
  const location = useLocation();
  const locationState = location.state as { message?: string } | null;
  useSessionSecurity();

  useEffect(() => {
    const fetchCSRFToken = async () => {
      try {
        await api.get('/csrf/');
      } catch (error) {
        return;
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
        <Route path="/login" element={<Login />} />
        <Route path="/" element={
          <PrivateRoute>
            <MainLayout />
          </PrivateRoute>
        }>
          <Route index element={<Navigate to="/dashboard" replace />} />

          <Route path="dashboard" element={<Dashboard />} />

          {/* Device Module */}
          <Route path="devices" element={<DeviceList />} />
          <Route path="devices/:id" element={<DeviceDetail />} />

          {/* Personnel Module - Organization Management (Hierarchical Order) */}
          <Route path="personnel" element={<Navigate to="/personnel/company" replace />} />
          <Route path="personnel/company" element={<Companies />} />
          <Route path="personnel/departments" element={<Departments />} />
          <Route path="personnel/shifts" element={<Shifts />} />
          <Route path="personnel/timetables" element={<Timetables />} />
          <Route path="personnel/employees" element={<Employees />} />

          {/* Attendance Module */}
          <Route path="attendance" element={<Navigate to="/attendance/logs" replace />} />
          <Route path="attendance/logs" element={<Logs />} />
          <Route path="attendance/schedule" element={<EmployeeSchedule />} />
          <Route path="attendance/absences" element={<Absences />} />
          <Route path="attendance/reports" element={<Reports />} />

          <Route path="asistencia">
            <Route path="empleado/:employeeId/dia/:date" element={<DayViewPage />} />
          </Route>

          <Route path="system" element={<Navigate to="/system/settings" replace />} />
          <Route path="system/settings" element={<Settings />} />
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
