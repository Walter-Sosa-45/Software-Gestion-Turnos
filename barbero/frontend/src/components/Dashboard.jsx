import React, { useState, useEffect } from 'react';
import { Calendar, Users, Clock, User, Phone, MessageCircle, Scissors, AlertCircle } from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { turnosService } from '../services/api';

const Dashboard = () => {
  const [expandedTurnos, setExpandedTurnos] = useState(new Set());
  const [turnos, setTurnos] = useState([]);
  const [estadisticas, setEstadisticas] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const fechaActual = new Date();
  const diaSemana = format(fechaActual, 'EEEE', { locale: es });
  const diaMes = format(fechaActual, 'dd', { locale: es });
  const mes = format(fechaActual, 'MMMM', { locale: es });

  // Cargar datos del backend
  useEffect(() => {
    const cargarDatos = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Obtener fecha actual en formato YYYY-MM-DD
        const fechaHoy = format(new Date(), 'yyyy-MM-dd');
        console.log('🔍 Fecha actual:', fechaHoy);
        
        // Cargar turnos del día
        const turnosDelDia = await turnosService.getTurnosPorFecha(fechaHoy);
        setTurnos(turnosDelDia);
        
        // Cargar estadísticas del mes actual (usando el año correcto del sistema)
        const ahora = new Date();
        console.log('🔍 Fecha actual (Date):', ahora);
        console.log('🔍 Año del sistema:', ahora.getFullYear());
        console.log('🔍 Mes del sistema:', ahora.getMonth());
        
        // Usar el año actual del sistema (no forzar 2024)
        const añoActual = ahora.getFullYear();
        const mesActual = ahora.getMonth(); // 0-11 (enero=0, agosto=7)
        
        console.log('🔍 Usando año del sistema:', añoActual);
        console.log('🔍 Mes actual (0-11):', mesActual);
        
        const primerDiaMes = new Date(añoActual, mesActual, 1);
        const ultimoDiaMes = new Date(añoActual, mesActual + 1, 0);
        
        console.log('🔍 Fechas calculadas:', {
          primerDia: primerDiaMes,
          ultimoDia: ultimoDiaMes,
          primerDiaFormateado: format(primerDiaMes, 'yyyy-MM-dd'),
          ultimoDiaFormateado: format(ultimoDiaMes, 'yyyy-MM-dd')
        });
        
        const stats = await turnosService.getEstadisticas(
          format(primerDiaMes, 'yyyy-MM-dd'),
          format(ultimoDiaMes, 'yyyy-MM-dd')
        );
        
        // Procesar estadísticas
        const estadisticasProcesadas = {
          total: stats.estadisticas?.total_turnos || 0,
          pendientes: stats.estadisticas?.pendientes || 0,
          completados: stats.estadisticas?.completados || 0,
          enCurso: stats.estadisticas?.confirmados || 0
        };
        
        setEstadisticas(estadisticasProcesadas);
        
      } catch (error) {
        console.error('❌ Error al cargar datos:', error);
        
        // Manejo específico de errores
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
    
    // Actualizar datos cada 5 minutos
    const interval = setInterval(cargarDatos, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  const handleWhatsApp = (telefono) => {
    const mensaje = encodeURIComponent('Hola! Te confirmo tu turno en la barbería.');
    window.open(`https://wa.me/${telefono.replace(/\s/g, '')}?text=${mensaje}`, '_blank');
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

  // Función para formatear la hora del turno
  const formatearHora = (hora) => {
    if (typeof hora === 'string') {
      return hora;
    }
    // Si es un objeto time de la base de datos
    return `${hora.hours.toString().padStart(2, '0')}:${hora.minutes.toString().padStart(2, '0')}`;
  };

  // Función para obtener el nombre del cliente
  const obtenerNombreCliente = (turno) => {
    // Aquí deberías tener acceso al cliente a través de la relación en la base de datos
    // Por ahora, asumimos que el turno tiene la información del cliente
    return turno.cliente_nombre || turno.cliente?.nombre || 'Cliente';
  };

  // Función para obtener el teléfono del cliente
  const obtenerTelefonoCliente = (turno) => {
    return turno.cliente_telefono || turno.cliente?.telefono || 'Sin teléfono';
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
      {/* Header */}
      <header className="header">
        <h1>Barber</h1>
        <div className="date">
          <Calendar />
          <span>{diaSemana} {diaMes} de {mes}</span>
        </div>
      </header>

      {/* Tarjetas de estadísticas */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="icon">
            <Users size={24} />
          </div>
          <div className="number">{estadisticas.total || 0}</div>
          <div className="label">Total Turnos</div>
        </div>
        
        <div className="stat-card">
          <span className="status-dot orange"></span>
          <div className="number">{estadisticas.pendientes || 0}</div>
          <div className="label">Pendientes</div>
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

      {/* Sección de turnos */}
      <section className="turnos-section">
        <div className="turnos-header">
          <h2>
            <Scissors size={20} />
            Turnos del Día
          </h2>
          <a href="#" className="ver-mas">ver más</a>
        </div>

        {turnos.length === 0 ? (
          <div className="no-turnos">
            <p>No hay turnos programados para hoy</p>
          </div>
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
                    <span className={`turno-estado ${turno.estado}`}>
                      {turno.estado}
                    </span>
                  </div>
                  
                  <div className="cliente">
                    <User />
                    {obtenerNombreCliente(turno)}
                  </div>
                  
                  {/* Contenido expandible */}
                  <div className={`turno-expandible ${isExpanded ? 'show' : ''}`}>
                    <div className="telefono">
                      Tel: {obtenerTelefonoCliente(turno)}
                    </div>
                    
                    <button 
                      className="whatsapp"
                      onClick={(e) => {
                        e.stopPropagation(); // Evitar que se cierre la tarjeta
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
    </div>
  );
};

export default Dashboard;
