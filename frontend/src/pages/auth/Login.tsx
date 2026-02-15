import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, User } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';

export const Login: React.FC = () => {
    const navigate = useNavigate();
    const { login, isLoading } = useAuth();
    const { error: showError, success: showSuccess } = useToast();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!username.trim()) {
            showError('El usuario es requerido');
            return;
        }
        if (!password.trim()) {
            showError('La contraseña es requerida');
            return;
        }

        try {
            await login(username, password);
            showSuccess('¡Inicio de sesión exitoso!');
            navigate('/dashboard');
        } catch (err: any) {
            // Mostrar error específico del login
            showError(err.message || 'Error al iniciar sesión');
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-card">
                <div className="auth-header">
                    <div className="auth-logo">
                        <img src="/img/sr-logo.png" alt="SR Logo" style={{ width: '80px', height: 'auto' }} />
                    </div>
                    <h2 className="auth-title">SRTimeWeb</h2>
                    <p className="auth-subtitle">Panel de Administración de Tiempo y Asistencia</p>
                </div>

                <form onSubmit={handleLogin} className="auth-form">
                    <div className="auth-field">
                        <label>Usuario</label>
                        <div className="auth-input-wrapper">
                            <User size={18} className="auth-input-icon" />
                            <input
                                className="auth-input"
                                type="text"
                                placeholder="Usuario"
                                value={username}
                                onChange={e => setUsername(e.target.value)}
                                disabled={isLoading}
                                required
                            />
                        </div>
                    </div>
                    <div className="auth-field">
                        <label>Contraseña</label>
                        <div className="auth-input-wrapper">
                            <Lock size={18} className="auth-input-icon" />
                            <input
                                className="auth-input"
                                type="password"
                                placeholder="Contraseña"
                                value={password}
                                onChange={e => setPassword(e.target.value)}
                                disabled={isLoading}
                                required
                            />
                        </div>
                    </div>

                    <div className="auth-actions">
                        <button
                            type="submit"
                            className="primary"
                            disabled={isLoading}
                        >
                            {isLoading ? 'Ingresando...' : 'Iniciar Sesión'}
                        </button>
                    </div>
                </form>

                <div className="auth-footer">
                    &copy; {new Date().getFullYear()} SRTimeWeb - DEV MODE
                </div>
            </div>
        </div>
    );
};
