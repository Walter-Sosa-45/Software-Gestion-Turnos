import axios from 'axios';
import { config } from './config';

// Configurar axios con prefijo /api/v1
const api = axios.create({
  baseURL: `${config.API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: config.REQUEST_TIMEOUT,
});

// Interceptor para agregar token de autenticación
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
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
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },
  logout: () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
  }
};

// Servicios de turnos
export const turnosService = {
  getTurnos: async (params = {}) => {
    const response = await api.get('/turnos/', { params });
    return response.data;
  },

  getTurnosPorFecha: async (fecha) => {
    const response = await api.get(`/turnos/fecha/${fecha}`);
    return response.data;
  },

  getTurnosSemana: async (fecha) => {
    const response = await api.get(`/turnos/semana/${fecha}`);
    return response.data;
  },

  createTurno: async (turnoData) => {
    const response = await api.post('/turnos/', turnoData);
    return response.data;
  },

  updateTurno: async (id, turnoData) => {
    const response = await api.put(`/turnos/${id}`, turnoData);
    return response.data;
  },

  deleteTurno: async (id) => {
    const response = await api.delete(`/turnos/${id}`);
    return response.data;
  },

  getEstadisticas: async (fechaInicio, fechaFin) => {
    const response = await api.get('/turnos/estadisticas', {
      params: { fecha_inicio: fechaInicio, fecha_fin: fechaFin }
    });
    return response.data;
  }
};

// Servicios de usuarios
export const usuariosService = {
  getUsuarios: async (params = {}) => {
    const response = await api.get('/usuarios/', { params });
    return response.data;
  },

  getUsuario: async (id) => {
    const response = await api.get(`/usuarios/${id}`);
    return response.data;
  },

  createUsuario: async (usuarioData) => {
    const response = await api.post('/usuarios/', usuarioData);
    return response.data;
  },

  updateUsuario: async (id, usuarioData) => {
    const response = await api.put(`/usuarios/${id}`, usuarioData);
    return response.data;
  }
};

// Servicios de servicios
export const serviciosService = {
  getServicios: async (params = {}) => {
    const response = await api.get('/servicios/', { params });
    return response.data;
  },

  getServicio: async (id) => {
    const response = await api.get(`/servicios/${id}`);
    return response.data;
  },

  createServicio: async (servicioData) => {
    const response = await api.post('/servicios/', servicioData);
    return response.data;
  },

  updateServicio: async (id, servicioData) => {
    const response = await api.put(`/servicios/${id}`, servicioData);
    return response.data;
  }
};

export default api;
