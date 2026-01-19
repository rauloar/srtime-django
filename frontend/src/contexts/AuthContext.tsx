import React, { createContext, useState, useCallback, type ReactNode, useEffect } from 'react';
import { api } from '../api';

interface AuthContextType {
  token: string | null;
  username: string | null;
  role: string | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  error: string | null;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(() => {
    return sessionStorage.getItem('auth_token');
  });
  const [username, setUsername] = useState<string | null>(() => {
    return sessionStorage.getItem('auth_username');
  });
  const [role, setRole] = useState<string | null>(() => {
    return sessionStorage.getItem('auth_role');
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = useCallback(async (username: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.post('/auth/login', {
        username,
        password
      });

      const { access_token, username: returnedUsername, role: returnedRole } = response.data;

      // Guardar token y datos en sessionStorage (solo sesión actual)
      sessionStorage.setItem('auth_token', access_token);
      sessionStorage.setItem('auth_username', returnedUsername);
      sessionStorage.setItem('auth_role', returnedRole);

      // Actualizar estado
      setToken(access_token);
      setUsername(returnedUsername);
      setRole(returnedRole);

      // Agregar token a headers para futuras peticiones
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    } catch (err: any) {
      let errorMsg = 'Error al iniciar sesión';
      
      if (err.code === 'ERR_NETWORK' || err.message === 'Network Error') {
        errorMsg = '⚠️ El servidor no responde. Verifique que el backend esté ejecutándose.';
      } else if (err.code === 'ECONNABORTED') {
        errorMsg = '⚠️ Tiempo de espera agotado. El servidor tardó demasiado en responder.';
      } else if (err.response) {
        // El servidor respondió con un código de error
        const status = err.response.status;
        
        if (status === 401 || status === 403) {
          errorMsg = '❌ Usuario o contraseña incorrectos. Verifique sus credenciales.';
        } else if (status === 422) {
          errorMsg = '⚠️ Datos de acceso inválidos. Complete todos los campos correctamente.';
        } else if (status >= 500) {
          errorMsg = '⚠️ Error del servidor. Intente nuevamente en unos momentos.';
        } else if (err.response.data?.detail) {
          errorMsg = err.response.data.detail;
        }
      } else if (err.request) {
        // La petición se hizo pero no hubo respuesta
        errorMsg = '⚠️ No se pudo conectar con el servidor. Verifique su conexión de red.';
      }
      
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    sessionStorage.removeItem('auth_token');
    sessionStorage.removeItem('auth_username');
    sessionStorage.removeItem('auth_role');
    sessionStorage.removeItem('device_id');
    setToken(null);
    setUsername(null);
    setRole(null);
    delete api.defaults.headers.common['Authorization'];
  }, []);

  // Cargar token al montar
  useEffect(() => {
    const savedToken = sessionStorage.getItem('auth_token');
    const savedUsername = sessionStorage.getItem('auth_username');
    const savedRole = sessionStorage.getItem('auth_role');
    
    if (savedToken) {
      setToken(savedToken);
      setUsername(savedUsername);
      setRole(savedRole);
      api.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`;
    }
  }, []);

  const value: AuthContextType = {
    token,
    username,
    role,
    isAuthenticated: !!token,
    login,
    logout,
    isLoading,
    error,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
