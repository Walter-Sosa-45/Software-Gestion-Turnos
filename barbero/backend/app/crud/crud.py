from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime, date, time, timedelta
import hashlib

from app.models.models import Usuario, Servicio, Turno
from app.schemas.schemas import UsuarioCreate, ServicioCreate, TurnoCreate

# Funciones CRUD para Usuarios
def get_usuario(db: Session, usuario_id: int) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()

def get_usuario_by_usuario(db: Session, usuario: str) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.usuario == usuario).first()

def get_usuario_by_telefono(db: Session, telefono: str) -> Optional[Usuario]:
    """Obtener usuario por teléfono (usando el campo usuario como teléfono)"""
    return db.query(Usuario).filter(Usuario.usuario == f"cliente_{telefono}").first()

def get_usuarios(db: Session, skip: int = 0, limit: int = 100, rol: Optional[str] = None) -> List[Usuario]:
    query = db.query(Usuario)
    if rol:
        query = query.filter(Usuario.rol == rol)
    return query.offset(skip).limit(limit).all()

def create_usuario(db: Session, usuario: UsuarioCreate) -> Usuario:
    # Hash de la contraseña usando bcrypt
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    password_hash = pwd_context.hash(usuario.password)
    
    db_usuario = Usuario(
        nombre=usuario.nombre,
        usuario=usuario.usuario,
        password_hash=password_hash,
        rol=usuario.rol
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def update_usuario(db: Session, usuario_id: int, usuario_update: dict) -> Optional[Usuario]:
    db_usuario = get_usuario(db, usuario_id)
    if db_usuario:
        for field, value in usuario_update.items():
            if value is not None:
                setattr(db_usuario, field, value)
        db.commit()
        db.refresh(db_usuario)
    return db_usuario

def delete_usuario(db: Session, usuario_id: int) -> bool:
    db_usuario = get_usuario(db, usuario_id)
    if db_usuario:
        db.delete(db_usuario)
        db.commit()
        return True
    return False

# Funciones CRUD para Servicios
def get_servicio(db: Session, servicio_id: int) -> Optional[Servicio]:
    return db.query(Servicio).filter(Servicio.id == servicio_id).first()

def get_servicios(db: Session, skip: int = 0, limit: int = 100) -> List[Servicio]:
    return db.query(Servicio).offset(skip).limit(limit).all()

def create_servicio(db: Session, servicio: ServicioCreate) -> Servicio:
    db_servicio = Servicio(**servicio.dict())
    db.add(db_servicio)
    db.commit()
    db.refresh(db_servicio)
    return db_servicio

def update_servicio(db: Session, servicio_id: int, servicio_update: dict) -> Optional[Servicio]:
    db_servicio = get_servicio(db, servicio_id)
    if db_servicio:
        for field, value in servicio_update.items():
            if value is not None:
                setattr(db_servicio, field, value)
        db.commit()
        db.refresh(db_servicio)
    return db_servicio

def delete_servicio(db: Session, servicio_id: int) -> bool:
    db_servicio = get_servicio(db, servicio_id)
    if db_servicio:
        db.delete(db_servicio)
        db.commit()
        return True
    return False

def get_servicio_by_nombre(db: Session, nombre: str) -> Optional[Servicio]:
    """Obtener servicio por nombre"""
    return db.query(Servicio).filter(Servicio.nombre == nombre).first()

# Funciones CRUD para Turnos
def get_turno(db: Session, turno_id: int) -> Optional[Turno]:
    return db.query(Turno).filter(Turno.id == turno_id).first()

def get_turnos(db: Session, skip: int = 0, limit: int = 100, 
                cliente_id: Optional[int] = None, 
                fecha_inicio: Optional[date] = None,
                fecha_fin: Optional[date] = None,
                estado: Optional[str] = None) -> List[Turno]:
    query = db.query(Turno)
    
    if cliente_id:
        query = query.filter(Turno.cliente_id == cliente_id)
    if fecha_inicio:
        query = query.filter(Turno.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Turno.fecha <= fecha_fin)
    if estado:
        query = query.filter(Turno.estado == estado)
    
    return query.order_by(Turno.fecha, Turno.hora_inicio).offset(skip).limit(limit).all()

def create_turno(db: Session, turno: TurnoCreate) -> Turno:
    db_turno = Turno(**turno.dict())
    db.add(db_turno)
    db.commit()
    db.refresh(db_turno)
    return db_turno

def update_turno(db: Session, turno_id: int, turno_update: dict) -> Optional[Turno]:
    db_turno = get_turno(db, turno_id)
    if db_turno:
        for field, value in turno_update.items():
            if value is not None:
                setattr(db_turno, field, value)
        db.commit()
        db.refresh(db_turno)
    return db_turno

def delete_turno(db: Session, turno_id: int) -> bool:
    db_turno = get_turno(db, turno_id)
    if db_turno:
        db.delete(db_turno)
        db.commit()
        return True
    return False

# Funciones de validación especiales
def verificar_disponibilidad_turno(db: Session, fecha: date, hora_inicio: time, 
                                 hora_fin: time, turno_id_excluir: Optional[int] = None) -> bool:
    """Verifica si un horario está disponible (sin conflictos con otros turnos)"""
    query = db.query(Turno).filter(
        and_(
            Turno.fecha == fecha,
            Turno.estado.in_(["pendiente", "confirmado"]),
            or_(
                and_(Turno.hora_inicio < hora_fin, Turno.hora_inicio >= hora_inicio),
                and_(Turno.hora_fin > hora_inicio, Turno.hora_fin <= hora_fin),
                and_(Turno.hora_inicio <= hora_inicio, Turno.hora_fin >= hora_fin)
            )
        )
    )
    
    if turno_id_excluir:
        query = query.filter(Turno.id != turno_id_excluir)
    
    return query.first() is None

def verificar_turno_semanal_cliente(db: Session, cliente_id: int, fecha: date) -> bool:
    """Verifica si un cliente ya tiene un turno en la semana de la fecha dada"""
    # Calcular inicio y fin de la semana (lunes a domingo)
    fecha_iso = fecha.isocalendar()
    lunes = date.fromisocalendar(fecha_iso[0], fecha_iso[1], 1)
    domingo = lunes + timedelta(days=6)
    
    # Buscar turnos activos en esa semana
    turnos_semana = db.query(Turno).filter(
        and_(
            Turno.cliente_id == cliente_id,
            Turno.fecha >= lunes,
            Turno.fecha <= domingo,
            Turno.estado.in_(["pendiente", "confirmado"])
        )
    ).all()
    
    return len(turnos_semana) > 0

def get_turnos_por_fecha(db: Session, fecha: date) -> List[Turno]:
    """Obtiene todos los turnos de una fecha específica"""
    return db.query(Turno).filter(
        and_(
            Turno.fecha == fecha,
            Turno.estado.in_(["pendiente", "confirmado"])
        )
    ).order_by(Turno.hora_inicio).all()

def get_turnos_semana(db: Session, fecha: date) -> List[Turno]:
    """Obtiene todos los turnos de la semana de una fecha específica"""
    fecha_iso = fecha.isocalendar()
    lunes = date.fromisocalendar(fecha_iso[0], fecha_iso[1], 1)
    domingo = lunes + timedelta(days=6)
    
    return db.query(Turno).filter(
        and_(
            Turno.fecha >= lunes,
            Turno.fecha <= domingo,
            Turno.estado.in_(["pendiente", "confirmado"])
        )
    ).order_by(Turno.fecha, Turno.hora_inicio).all()

def cancelar_turnos_cliente_semana(db: Session, cliente_id: int, fecha: date) -> int:
    """Cancela todos los turnos activos de un cliente en la semana de la fecha dada"""
    fecha_iso = fecha.isocalendar()
    lunes = date.fromisocalendar(fecha_iso[0], fecha_iso[1], 1)
    domingo = lunes + timedelta(days=6)
    
    # Actualizar estado de turnos activos a 'cancelado'
    result = db.query(Turno).filter(
        and_(
            Turno.cliente_id == cliente_id,
            Turno.fecha >= lunes,
            Turno.fecha <= domingo,
            Turno.estado.in_(["pendiente", "confirmado"])
        )
    ).update({"estado": "cancelado"})
    
    db.commit()
    return result

def get_estadisticas_turnos(db: Session, fecha_inicio: date, fecha_fin: date) -> dict:
    """Obtiene estadísticas de turnos en un rango de fechas"""
    stats = db.query(
        func.count(Turno.id).label('total_turnos'),
        func.count(Turno.id).filter(Turno.estado == 'pendiente').label('pendientes'),
        func.count(Turno.id).filter(Turno.estado == 'confirmado').label('confirmados'),
        func.count(Turno.id).filter(Turno.estado == 'cancelado').label('cancelados'),
        func.count(Turno.id).filter(Turno.estado == 'completado').label('completados')
    ).filter(
        and_(
            Turno.fecha >= fecha_inicio,
            Turno.fecha <= fecha_fin
        )
    ).first()
    
    return {
        'total_turnos': stats.total_turnos or 0,
        'pendientes': stats.pendientes or 0,
        'confirmados': stats.confirmados or 0,
        'cancelados': stats.cancelados or 0,
        'completados': stats.completados or 0
    }
