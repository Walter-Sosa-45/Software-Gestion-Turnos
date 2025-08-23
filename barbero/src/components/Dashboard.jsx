import React, { useState, useEffect } from 'react';
import { Calendar, Users, Clock, User, MessageCircle, Scissors, AlertCircle, Lock, Bell, LogOut } from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { turnosService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import MonthlyCalendar from './MonthlyCalendar';
import BloqueoModal from './BloqueoModal';
import '../styles/Dashboard.css';

const Dashboard = () => {
  const { logout, user, loading: authLoading } = useAuth();
  const [expandedTurnos, setExpandedTurnos] = useState(new Set());
  const [turnos, setTurnos] = useState([]);
  const [estadisticas, setEstadisticas] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showMonthlyCalendar, setShowMonthlyCalendar] = useState(false);
  const [showBloqueoModal, setShowBloqueoModal] = useState(false);
  
  const fechaActual = new Date();
  const diaSemana = format(fechaActual, 'EEEE', { locale: es });
  const diaMes = format(fechaActual, 'dd', { locale: es });
  const mes = format(fechaActual, 'MMMM', { locale: es });

  // Mostrar loading mientras se inicializa la autenticación
  if (authLoading) {
    return (
      <div className="loading-container">
        <div className="loading">Inicializando...</div>
      </div>
    );
  }

  // Verificar que el usuario esté autenticado
  if (!user) {
    return (
      <div className="error-container">
        <div className="error-message">No se pudo cargar la información del usuario. Por favor, inicia sesión nuevamente.</div>
        <button onClick={logout} className="logout-button">Cerrar Sesión</button>
      </div>
    );
  }

  useEffect(() => {
    const cargarDatos = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const fechaHoy = format(new Date(), 'yyyy-MM-dd');
        console.log('🔍 Fecha actual:', fechaHoy);
        
        // Obtener turnos del día
        const turnosDelDiaResponse = await turnosService.getTurnosPorFecha(fechaHoy);
        setTurnos(turnosDelDiaResponse.turnos || []);
        
        // Cargar estadísticas del mes actual
        const ahora = new Date();
        const añoActual = ahora.getFullYear();
        const mesActual = ahora.getMonth(); // 0-11
        const primerDiaMes = new Date(añoActual, mesActual, 1);
        const ultimoDiaMes = new Date(añoActual, mesActual + 1, 0);

        const statsResponse = await turnosService.getEstadisticas(
          format(primerDiaMes, 'yyyy-MM-dd'),
          format(ultimoDiaMes, 'yyyy-MM-dd')
        );

        const estadisticasProcesadas = {
          total: statsResponse.estadisticas?.total_turnos || 0,
          pendientes: statsResponse.estadisticas?.pendientes || 0,
          completados: statsResponse.estadisticas?.completados || 0,
          enCurso: statsResponse.estadisticas?.confirmados || 0
        };
        setEstadisticas(estadisticasProcesadas);

      } catch (error) {
        console.error('❌ Error al cargar datos:', error);
        if (error.response?.status === 422) {
          setError('Error en el formato de fechas. Intenta recargar la página.');
        } else if (error.response?.status === 500) {
          setError('Error del servidor. Verifica que la base de datos esté inicializada.');
        } else if (error.code === 'ERR_NETWORK') {
          setError('No se pudo conectar con el servidor. Verifica que el backend esté ejecutándose.');
        } else {
          setError('Error al cargar los datos. Intenta recargar la página.');
        }
      } finally {
        setLoading(false);
      }
    };

    cargarDatos();
    const interval = setInterval(cargarDatos, 5 * 60 * 1000); // cada 5 min
    return () => clearInterval(interval);
  }, []);

  const handleWhatsApp = (telefono) => {
    const mensaje = encodeURIComponent('Hola! Te confirmo tu turno en la barbería.');
    window.open(`https://wa.me/${telefono.replace(/\s/g, '')}?text=${mensaje}`, '_blank');
  };

  const handleLogout = () => {
    if (window.confirm('¿Estás seguro de que quieres cerrar sesión?')) {
      logout();
    }
  };

  const handleNotifications = () => {
    // Aquí puedes implementar la lógica para mostrar notificaciones
    alert('Funcionalidad de notificaciones próximamente disponible');
  };

  const toggleTurnoExpansion = (turnoId) => {
    setExpandedTurnos(prev => {
      const newSet = new Set(prev);
      if (newSet.has(turnoId)) {
        newSet.delete(turnoId);
      } else {
        newSet.add(turnoId);
      }
      return newSet;
    });
  };

  const formatearHora = (hora) => {
    if (!hora) return '';
    return hora.slice(0, 5); // HH:MM
  };

  const obtenerNombreCliente = (turno) => {
    return turno.cliente?.nombre || 'Cliente';
  };

  const obtenerTelefonoCliente = (turno) => {
    return turno.cliente?.telefono || 'Sin teléfono';
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Cargando información...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="error-container">
          <AlertCircle size={48} color="#dc3545" />
          <h3>Error al cargar datos</h3>
          <p>{error}</p>
          <button 
            className="retry-button"
            onClick={() => window.location.reload()}
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <header className="header">
        <div className="title-bock">
          <h1>Barber</h1>
          <div className="date">
            <Calendar />
            <span>{diaSemana} {diaMes} de {mes}</span>
          </div>
        </div>
        <div className="header-right">
          <div className="user-info">
            <span className="user-name">{user?.nombre || 'Usuario'}</span>
          </div>
          <div className="notification-icon" onClick={handleNotifications}>
            <Bell size={24} />
            <span className="notification-badge">3</span>
          </div>
          <div className="logout-icon" onClick={handleLogout}>
            <LogOut size={24} />
          </div>
        </div>
      </header>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="icon"><Users size={24} /></div>
          <div className="number">{estadisticas.total || 0}</div>
          <div className="label">Total Turnos</div>
        </div>
        <div className="stat-card">
          <span className="status-dot orange"></span>
          <div className="pendiente">
            <div className="number">{estadisticas.pendientes || 0}</div>
            <div className="label">Pendientes</div>
          </div>
        </div>
        <div className="stat-card">
          <span className="status-dot green"></span>
          <div className="number">{estadisticas.completados || 0}</div>
          <div className="label">Completados</div>
        </div>
        <div className="stat-card">
          <span className="status-dot blue"></span>
          <div className="number">{estadisticas.enCurso || 0}</div>
          <div className="label">En Curso</div>
        </div>
      </div>

      <section className="turnos-section">
        <div className="turnos-header">
          <h2><Scissors size={20}/> Turnos del Día</h2>
          <button 
            className="ver-mas-button"
            onClick={() => setShowMonthlyCalendar(true)}
          >
            ver más
          </button>
          <button
            className="ver-mas-button"
            onClick={() => setShowBloqueoModal(true)}
            title="Bloquear agenda"
          >
            <Lock size={16} /> bloquear
          </button>
        </div>

        {turnos.length === 0 ? (
          <div className="no-turnos"><p>No hay turnos programados para hoy</p></div>
        ) : (
          <div className="turnos-list">
            {turnos.map((turno) => {
              const isExpanded = expandedTurnos.has(turno.id);
              return (
                <div 
                  key={turno.id} 
                  className={`turno-card ${isExpanded ? 'expanded' : ''}`}
                  onClick={() => toggleTurnoExpansion(turno.id)}
                >
                  <div className="turno-header">
                    <div className="hora">
                      <Clock />
                      {formatearHora(turno.hora_inicio)}
                    </div>
                    <span className={`turno-estado ${turno.estado}`}>{turno.estado}</span>
                  </div>
                  <div className="cliente">
                    <User />
                    {obtenerNombreCliente(turno)}
                  </div>
                  <div className={`turno-expandible ${isExpanded ? 'show' : ''}`}>
                    <div className="telefono">Tel: {obtenerTelefonoCliente(turno)}</div>
                    <button 
                      className="whatsapp"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleWhatsApp(obtenerTelefonoCliente(turno));
                      }}
                    >
                      <MessageCircle />
                      WhatsApp
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* Modal del calendario mensual */}
      {showMonthlyCalendar && (
        <MonthlyCalendar onClose={() => setShowMonthlyCalendar(false)} />
      )}

      {/* Modal de bloqueo */}
      {showBloqueoModal && (
        <BloqueoModal 
          onClose={() => setShowBloqueoModal(false)}
          onCreated={() => {
            // refrescar datos del día por si bloqueó hoy
            const fechaHoy = format(new Date(), 'yyyy-MM-dd');
            turnosService.getTurnosPorFecha(fechaHoy).then(r => setTurnos(r.turnos || []));
          }}
        />
      )}
    </div>
  );
};

export default Dashboard;
