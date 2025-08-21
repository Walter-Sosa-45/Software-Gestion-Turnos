import React, { useState, useEffect } from 'react';
import { Calendar, ChevronLeft, ChevronRight, Clock, User, X } from 'lucide-react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, addMonths, subMonths, startOfWeek, endOfWeek } from 'date-fns';
import { es } from 'date-fns/locale';
import { turnosService } from '../services/api';

const MonthlyCalendar = ({ onClose }) => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [turnos, setTurnos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedDateTurnos, setSelectedDateTurnos] = useState([]);

  // Estados de disponibilidad
  const DISPONIBILIDAD = {
    SIN_TURNOS: 'sin-turnos',
    CON_TURNOS_DISPONIBLE: 'con-turnos-disponible',
    COMPLETO: 'completo'
  };

  useEffect(() => {
    cargarTurnosDelMes();
  }, [currentDate]);

  const cargarTurnosDelMes = async () => {
    try {
      setLoading(true);
      const fechaInicio = format(startOfMonth(currentDate), 'yyyy-MM-dd');
      const fechaFin = format(endOfMonth(currentDate), 'yyyy-MM-dd');
      
      const response = await turnosService.getTurnos({
        fecha_inicio: fechaInicio,
        fecha_fin: fechaFin
      });
      
      setTurnos(response.turnos || []);
    } catch (error) {
      console.error('Error al cargar turnos del mes:', error);
    } finally {
      setLoading(false);
    }
  };

  const obtenerDisponibilidadFecha = (fecha) => {
    const turnosFecha = turnos.filter(turno => 
      isSameDay(new Date(turno.fecha), fecha)
    );

    if (turnosFecha.length === 0) {
      return DISPONIBILIDAD.SIN_TURNOS;
    }

    // Verificar si hay horarios disponibles (asumiendo horarios de 9:00 a 22:00 cada 30 min)
    const horariosOcupados = turnosFecha.length;
    const totalHorarios = 26; // 13 horas * 2 slots por hora

    if (horariosOcupados >= totalHorarios) {
      return DISPONIBILIDAD.COMPLETO;
    } else {
      return DISPONIBILIDAD.CON_TURNOS_DISPONIBLE;
    }
  };

  const handleDateClick = async (fecha) => {
    setSelectedDate(fecha);
    try {
      const fechaStr = format(fecha, 'yyyy-MM-dd');
      const response = await turnosService.getTurnosPorFecha(fechaStr);
      setSelectedDateTurnos(response.turnos || []);
    } catch (error) {
      console.error('Error al cargar turnos de la fecha:', error);
      setSelectedDateTurnos([]);
    }
  };

  const cambiarMes = (direccion) => {
    setCurrentDate(prev => 
      direccion === 'next' ? addMonths(prev, 1) : subMonths(prev, 1)
    );
  };

  const generarDiasCalendario = () => {
    const inicioMes = startOfMonth(currentDate);
    const finMes = endOfMonth(currentDate);
    const inicioSemana = startOfWeek(inicioMes, { weekStartsOn: 1 }); // Lunes
    const finSemana = endOfWeek(finMes, { weekStartsOn: 1 });

    return eachDayOfInterval({ start: inicioSemana, end: finSemana });
  };

  const formatearHora = (hora) => {
    if (!hora) return '';
    return hora.slice(0, 5);
  };

  const obtenerNombreCliente = (turno) => {
    return turno.cliente?.nombre || 'Cliente';
  };

  const obtenerTelefonoCliente = (turno) => {
    return turno.cliente?.telefono || 'Sin teléfono';
  };

  const handleWhatsApp = (telefono) => {
    const mensaje = encodeURIComponent('Hola! Te confirmo tu turno en la barbería.');
    window.open(`https://wa.me/${telefono.replace(/\s/g, '')}?text=${mensaje}`, '_blank');
  };

  const diasSemana = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa', 'Do'];

  return (
    <div className="monthly-calendar-overlay">
      <div className="monthly-calendar-container">
        {/* Header */}
        <div className="calendar-header">
          <div className="calendar-title">
            <Calendar size={24} />
            <h2>Vista de Turnos por mes</h2>
          </div>
          <button className="close-button" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        {/* Navegación del mes */}
        <div className="month-navigation">
          <button 
            className="nav-button" 
            onClick={() => cambiarMes('prev')}
          >
            <ChevronLeft size={20} />
          </button>
          <h3 className="current-month">
            {format(currentDate, 'MMMM yyyy', { locale: es })}
          </h3>
          <button 
            className="nav-button" 
            onClick={() => cambiarMes('next')}
          >
            <ChevronRight size={20} />
          </button>
        </div>

        {/* Leyenda */}
        <div className="calendar-legend">
          <div className="legend-item">
            <div className="legend-color sin-turnos"></div>
            <span>Sin turnos</span>
          </div>
          <div className="legend-item">
            <div className="legend-color con-turnos-disponible"></div>
            <span>Con turnos (disponible)</span>
          </div>
          <div className="legend-item">
            <div className="legend-color completo"></div>
            <span>Completo</span>
          </div>
        </div>

        {/* Calendario */}
        <div className="calendar-grid">
          {/* Días de la semana */}
          <div className="calendar-weekdays">
            {diasSemana.map(dia => (
              <div key={dia} className="weekday">{dia}</div>
            ))}
          </div>

          {/* Días del mes */}
          <div className="calendar-days">
            {loading ? (
              <div className="loading-calendar">Cargando...</div>
            ) : (
              generarDiasCalendario().map((fecha, index) => {
                const esMesActual = isSameMonth(fecha, currentDate);
                const disponibilidad = obtenerDisponibilidadFecha(fecha);
                const esHoy = isSameDay(fecha, new Date());
                
                return (
                  <button
                    key={index}
                    className={`calendar-day ${disponibilidad} ${
                      !esMesActual ? 'other-month' : ''
                    } ${esHoy ? 'today' : ''}`}
                    onClick={() => handleDateClick(fecha)}
                    disabled={!esMesActual}
                  >
                    {format(fecha, 'd')}
                  </button>
                );
              })
            )}
          </div>
        </div>

        {/* Modal de turnos del día seleccionado */}
        {selectedDate && (
          <div className="day-details-modal">
            <div className="day-details-content">
              <div className="day-details-header">
                <h3>Turnos del {format(selectedDate, 'EEEE dd \'de\' MMMM', { locale: es })}</h3>
                <button 
                  className="close-details" 
                  onClick={() => setSelectedDate(null)}
                >
                  <X size={20} />
                </button>
              </div>
              
              {selectedDateTurnos.length === 0 ? (
                <div className="no-turnos-day">
                  <p>No hay turnos programados para este día</p>
                </div>
              ) : (
                <div className="turnos-list-day">
                  {selectedDateTurnos.map((turno) => (
                    <div key={turno.id} className="turno-item-day">
                      <div className="turno-time">
                        <Clock size={16} />
                        {formatearHora(turno.hora_inicio)}
                      </div>
                      <div className="turno-client">
                        <User size={16} />
                        {obtenerNombreCliente(turno)}
                      </div>
                      <div className="turno-service">
                        {turno.servicio?.nombre}
                      </div>
                      <div className="turno-actions">
                        <span className={`turno-status ${turno.estado}`}>
                          {turno.estado}
                        </span>
                        <button 
                          className="whatsapp-small"
                          onClick={() => handleWhatsApp(obtenerTelefonoCliente(turno))}
                        >
                          WhatsApp
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MonthlyCalendar;
