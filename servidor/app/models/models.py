from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Time, Index, Boolean, JSON
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from app.core.config import TenantBase

class Usuario(TenantBase):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    usuario = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(10), nullable=False)  # 'admin', 'barbero'
    fecha_registro = Column(DateTime, server_default=func.now())

class Clientes(TenantBase):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=False)
    fecha_registro = Column(DateTime, server_default=func.now())

    turnos = relationship("Turno", back_populates="cliente")

class Servicio(TenantBase):
    __tablename__ = "servicios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    duracion_min = Column(Integer, nullable=False)
    precio = Column(Integer, nullable=False)  # Precio en centavos
    
    turnos = relationship("Turno", back_populates="servicio")
    barbero_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    barbero = relationship("Usuario")

class Turno(TenantBase):
    __tablename__ = "turnos"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    servicio_id = Column(Integer, ForeignKey("servicios.id"), nullable=False)
    barbero_id = Column(Integer, nullable=True)  # Sin ForeignKey
    fecha = Column(Date, nullable=False, index=True)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    estado = Column(String(20), nullable=False, index=True)  # 'pendiente', 'confirmado', 'cancelado', 'completado'
    creado_en = Column(DateTime, server_default=func.now())
    notificado = Column(Boolean, default=False, nullable=False)
    
    cliente = relationship("Clientes", back_populates="turnos")
    servicio = relationship("Servicio", back_populates="turnos")
    # barbero = relationship("Usuario")

# Índices compuestos para optimizar consultas
Index('idx_turnos_cliente_fecha', Turno.cliente_id, Turno.fecha)
Index('idx_turnos_fecha_estado', Turno.fecha, Turno.estado)
Index('idx_turnos_cliente_estado', Turno.cliente_id, Turno.estado)

class BloqueoAgenda(TenantBase):
    __tablename__ = "bloqueos_agenda"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False, index=True)
    todo_dia = Column(Boolean, nullable=False, default=False)
    hora_inicio = Column(Time, nullable=True)
    hora_fin = Column(Time, nullable=True)
    motivo = Column(String(255), nullable=True)
    creado_en = Column(DateTime, server_default=func.now())

Index('idx_bloqueos_fecha', BloqueoAgenda.fecha)