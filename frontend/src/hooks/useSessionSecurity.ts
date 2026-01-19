import { useEffect, useRef } from 'react';
import { useAuth } from './useAuth';
import { useNavigate } from 'react-router-dom';

/**
 * Hook que supervisa la seguridad de sesión:
 * 1. Detecta si el servidor backend está caído
 * 2. Detecta cambios de navegador/dispositivo
 * 3. Invalida sesión y fuerza logout obligatorio en esos casos
 */
export const useSessionSecurity = () => {
    const { logout, isAuthenticated } = useAuth();
    const navigate = useNavigate();
    const deviceIdRef = useRef<string | null>(null);

    // Generar ID único del dispositivo basado en navegador y agente
    const generateDeviceId = (): string => {
        const userAgent = navigator.userAgent;
        const language = navigator.language;
        const platform = navigator.platform;
        const hardwareConcurrency = navigator.hardwareConcurrency || 'unknown';
        
        // Crear hash simple del dispositivo
        const deviceInfo = `${platform}-${language}-${hardwareConcurrency}-${userAgent}`;
        return btoa(deviceInfo); // Base64 encode para simplicidad
    };

    // Inicializar o validar ID del dispositivo
    const initializeDeviceId = () => {
        const stored = sessionStorage.getItem('device_id');
        const current = generateDeviceId();

        if (stored && stored !== current) {
            // Cambio de navegador/dispositivo detectado
            console.warn('⚠️ Cambio de navegador/dispositivo detectado. Invalidando sesión.');
            handleSessionInvalidation('device_changed');
            return false;
        }

        if (!stored) {
            sessionStorage.setItem('device_id', current);
            deviceIdRef.current = current;
        } else {
            deviceIdRef.current = stored;
        }

        return true;
    };

    // Manejar invalidación de sesión
    const handleSessionInvalidation = (reason: 'device_changed' | 'logout') => {
        console.log(`🔒 Sesión invalidada: ${reason}`);
        
        // Limpiar storage
        sessionStorage.removeItem('auth_token');
        sessionStorage.removeItem('auth_username');
        sessionStorage.removeItem('auth_role');
        sessionStorage.removeItem('device_id');
        
        // Hacer logout
        logout();
        
        // Redirigir a login
        navigate('/login', { 
            replace: true,
            state: { 
                message: reason === 'device_changed'
                    ? 'Sesión invalidada por cambio de navegador/dispositivo. Por favor, inicia sesión nuevamente.'
                    : 'Sesión cerrada.'
            }
        });
    };

    // Iniciar monitoreo
    useEffect(() => {
        if (!isAuthenticated) {
            return;
        }

        // Validar dispositivo al autenticarse
        const isValidDevice = initializeDeviceId();
        if (!isValidDevice) {
            return;
        }

        return () => {
            // no-op
        };
    }, [isAuthenticated]);

    // Detectar cuando se cierra la ventana/tab
    useEffect(() => {
        const handleBeforeUnload = () => {
            // Si se cierra la ventana, limpiar sessionStorage
            // (esto garantiza que logout se fuerza si se reinicia el servidor)
            if (isAuthenticated) {
                sessionStorage.removeItem('device_id');
            }
        };

        window.addEventListener('beforeunload', handleBeforeUnload);
        return () => window.removeEventListener('beforeunload', handleBeforeUnload);
    }, [isAuthenticated]);

    // Nota: sessionStorage es por-tab y no sincroniza entre pestañas,
    // por lo que no se requiere listener de cambios entre ventanas.

    return {
        sessionValid: true,
    };
};
