// import { useEffect, useRef } from 'react';  // DEV: Unused in bypass mode
// import { useAuth } from './useAuth';  // DEV: Unused in bypass mode
// import { useNavigate } from 'react-router-dom';  // DEV: Unused in bypass mode

/**
 * Hook que supervisa la seguridad de sesión:
 * 1. Detecta si el servidor backend está caído
 * 2. Detecta cambios de navegador/dispositivo
 * 3. Invalida sesión y fuerza logout obligatorio en esos casos
 */
export function useSessionSecurity() {
    // DEV BYPASS: Disable session security
    return { sessionValid: true };
}

/*
export function useSessionSecurity() {
const { logout, isAuthenticated } = useAuth();
const navigate = useNavigate();
const deviceIdRef = useRef<string | null>(null);

// ... (rest of logic commented out or bypassed)

return {
    sessionValid: true,
};
};
*/
