import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // No cargar usuario desde localStorage al iniciar
  useEffect(() => {
    setLoading(false);
  }, []);

  // Listener para detectar cuando se cierra la pestaña o se recarga
  useEffect(() => {
    const handleBeforeUnload = () => {
      // Limpiar sesión al cerrar/recargar
      setUser(null);
      localStorage.removeItem('user');
      localStorage.removeItem('authToken');
    };

    const handleVisibilityChange = () => {
      // Si la pestaña se oculta (se cierra o cambia), limpiar sesión
      if (document.hidden) {
        setUser(null);
        localStorage.removeItem('user');
        localStorage.removeItem('authToken');
      }
    };

    // Evento cuando se cierra/recarga la pestaña
    window.addEventListener('beforeunload', handleBeforeUnload);
    
    // Evento cuando cambia la visibilidad de la pestaña
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    // Evento cuando se recarga la página
    window.addEventListener('unload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('unload', handleBeforeUnload);
    };
  }, []);

  const login = async (credentials) => {
    try {
      setError(null);
      setLoading(true);
      
      // Usar el servicio de API real
      const response = await authService.login(credentials);
      
      if (response.access_token) {
        const userData = {
          id: response.user.id,
          nombre: response.user.nombre,
          usuario: response.user.usuario,
          rol: response.user.rol
        };
        
        setUser(userData);
        
        // NO guardar en localStorage - solo en estado de memoria
        // localStorage.setItem('user', JSON.stringify(userData));
        // localStorage.setItem('authToken', response.access_token);
        
        return { success: true, user: userData };
      } else {
        throw new Error('Respuesta inválida del servidor');
      }
    } catch (error) {
      let errorMessage = 'Error al iniciar sesión';
      
      if (error.response) {
        // Error del servidor
        if (error.response.status === 401) {
          errorMessage = 'Usuario o contraseña incorrectos';
        } else if (error.response.data && error.response.data.detail) {
          errorMessage = error.response.data.detail;
        } else {
          errorMessage = `Error del servidor: ${error.response.status}`;
        }
      } else if (error.request) {
        // Error de red
        errorMessage = 'No se pudo conectar con el servidor. Verifica que el backend esté ejecutándose.';
      } else {
        // Otro tipo de error
        errorMessage = error.message || 'Error desconocido';
      }
      
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setError(null);
    // Limpiar localStorage también por si acaso
    localStorage.removeItem('user');
    localStorage.removeItem('authToken');
    authService.logout();
  };

  const clearError = () => {
    setError(null);
  };

  const value = {
    user,
    loading,
    error,
    login,
    logout,
    clearError,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
