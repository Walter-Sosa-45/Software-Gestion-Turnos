import axios from 'axios';
import { config } from './config';

// Configurar axios
const api = axios.create({
  baseURL: config.API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: config.REQUEST_TIMEOUT,
});

// Interceptor para agregar token de autenticación (solo si existe)
api.interceptors.request.use(
  (config) => {
    // Solo agregar token si existe en el estado actual (no en localStorage)
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar respuestas y errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Si el token expiró, limpiar localStorage
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
    }
    return Promise.reject(error);
  }
);

// Servicios de autenticación
export const authService = {
  login: async (credentials) => {
    try {
      const response = await api.post('/auth/login', credentials);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
  }
};

// Servicios de turnos
export const turnosService = {
  getTurnos: async (params = {}) => {
    try {
      const response = await api.get('/turnos/', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  getTurnosPorFecha: async (fecha) => {
    try {
      const response = await api.get(`/turnos/fecha/${fecha}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  getTurnosSemana: async (fecha) => {
    try {
      const response = await api.get(`/turnos/semana/${fecha}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  createTurno: async (turnoData) => {
    try {
      const response = await api.post('/turnos/', turnoData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  updateTurno: async (id, turnoData) => {
    try {
      const response = await api.put(`/turnos/${id}`, turnoData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  deleteTurno: async (id) => {
    try {
      const response = await api.delete(`/turnos/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  getEstadisticas: async (fechaInicio, fechaFin) => {
    try {
      const response = await api.get('/turnos/estadisticas', {
        params: { fecha_inicio: fechaInicio, fecha_fin: fechaFin }
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

// Servicios de usuarios
export const usuariosService = {
  getUsuarios: async (params = {}) => {
    try {
      const response = await api.get('/usuarios/', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  getUsuario: async (id) => {
    try {
      const response = await api.get(`/usuarios/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  createUsuario: async (usuarioData) => {
    try {
      const response = await api.post('/usuarios/', usuarioData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  updateUsuario: async (id, usuarioData) => {
    try {
      const response = await api.put(`/usuarios/${id}`, usuarioData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

// Servicios de servicios
export const serviciosService = {
  getServicios: async (params = {}) => {
    try {
      const response = await api.get('/servicios/', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  getServicio: async (id) => {
    try {
      const response = await api.get(`/servicios/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  createServicio: async (servicioData) => {
    try {
      const response = await api.post('/servicios/', servicioData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  updateServicio: async (id, servicioData) => {
    try {
      const response = await api.put(`/servicios/${id}`, servicioData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default api;
