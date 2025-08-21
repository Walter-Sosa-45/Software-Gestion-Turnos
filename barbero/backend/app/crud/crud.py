from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime, date, time, timedelta
import hashlib

from app.models.models import Usuario, Clientes, Servicio, Turno
from app.schemas.schemas import UsuarioCreate, ServicioCreate, TurnoCreate

# Funciones CRUD para Usuarios (admin)
def get_usuario(db: Session, usuario_id: int) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()

def get_usuario_by_usuario(db: Session, usuario: str) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.usuario == usuario).first()

def get_usuarios(db: Session, skip: int = 0, limit: int = 100, rol: Optional[str] = None) -> List[Usuario]:
    query = db.query(Usuario)
    if rol:
        query = query.filter(Usuario.rol == rol)
    return query.offset(skip).limit(limit).all()

def create_usuario(db: Session, usuario: UsuarioCreate) -> Usuario:
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

# Funciones CRUD para Clientes
def get_cliente(db: Session, cliente_id: int) -> Optional[Clientes]:
    return db.query(Clientes).filter(Clientes.id == cliente_id).first()

def get_cliente_by_telefono(db: Session, telefono: str) -> Optional[Clientes]:
    return db.query(Clientes).filter(Clientes.telefono == telefono).first()

def get_clientes(db: Session, skip: int = 0, limit: int = 100) -> List[Clientes]:
    return db.query(Clientes).offset(skip).limit(limit).all()

def create_cliente(db: Session, nombre: str, telefono: str) -> Clientes:
    db_cliente = Clientes(nombre=nombre, telefono=telefono)
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

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

# Funciones CRUD para Turnos (modificadas para usar Clientes)
def get_turno(db: Session, turno_id: int) -> Optional[Turno]:
    return db.query(Turno).filter(Turno.id == turno_id).first()

def get_turnos(db: Session, skip: int = 0, limit: int = 100, 
                cliente_id: Optional[int] = None, 
                fecha_inicio: Optional[date] = None,
                fecha_fin: Optional[date] = None,
                estado: Optional[str] = None) -> List[Turno]:
    query = db.query(Turno).options(
        joinedload(Turno.cliente),
        joinedload(Turno.servicio)
    )
    
    if cliente_id:
        query = query.filter(Turno.cliente_id == cliente_id)
    if fecha_inicio:
        query = query.filter(Turno.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Turno.fecha <= fecha_fin)
    if estado:
        query = query.filter(Turno.estado == estado)
    
    return query.order_by(Turno.fecha, Turno.hora_inicio).offset(skip).limit(limit).all()

def create_turno(db: Session, cliente_id: int, servicio_id: int, fecha: date, hora_inicio: time, hora_fin: time) -> Turno:
    db_turno = Turno(
        cliente_id=cliente_id,
        servicio_id=servicio_id,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        estado="pendiente"
    )
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

# Funciones adicionales necesarias para el frontend
def get_servicio_by_nombre(db: Session, nombre: str) -> Optional[Servicio]:
    return db.query(Servicio).filter(Servicio.nombre == nombre).first()

def verificar_disponibilidad_turno(db: Session, fecha: date, hora_inicio: time, hora_fin: time) -> bool:
    """
    Verifica si hay disponibilidad para un turno en la fecha y horario especificados.
    Retorna True si está disponible, False si hay conflicto.
    """
    # Buscar turnos que se superpongan con el horario solicitado
    turnos_conflicto = db.query(Turno).filter(
        and_(
            Turno.fecha == fecha,
            Turno.estado != "cancelado",
            or_(
                # El turno solicitado empieza durante un turno existente
                and_(Turno.hora_inicio <= hora_inicio, Turno.hora_fin > hora_inicio),
                # El turno solicitado termina durante un turno existente
                and_(Turno.hora_inicio < hora_fin, Turno.hora_fin >= hora_fin),
                # El turno solicitado contiene completamente un turno existente
                and_(Turno.hora_inicio >= hora_inicio, Turno.hora_fin <= hora_fin)
            )
        )
    ).count()
    
    return turnos_conflicto == 0

def get_horarios_disponibles(db: Session, fecha: date) -> List[str]:
    """
    Obtiene los horarios disponibles para una fecha específica.
    Retorna una lista de horarios en formato "HH:MM".
    """
    # Horarios de trabajo (9:00 a 22:00, cada 30 minutos)
    horarios_trabajo = []
    hora_actual = time(9, 0)  # 9:00 AM
    hora_fin = time(22, 0)    # 10:00 PM
    
    while hora_actual < hora_fin:
        horarios_trabajo.append(hora_actual.strftime("%H:%M"))
        # Avanzar 30 minutos
        hora_actual = (datetime.combine(date.today(), hora_actual) + timedelta(minutes=30)).time()
    
    # Obtener turnos existentes para esa fecha
    turnos_existentes = db.query(Turno).filter(
        and_(
            Turno.fecha == fecha,
            Turno.estado != "cancelado"
        )
    ).all()
    
    # Crear conjunto de horarios ocupados
    horarios_ocupados = set()
    for turno in turnos_existentes:
        hora_actual = turno.hora_inicio
        while hora_actual < turno.hora_fin:
            horarios_ocupados.add(hora_actual.strftime("%H:%M"))
            hora_actual = (datetime.combine(date.today(), hora_actual) + timedelta(minutes=30)).time()
    
    # Filtrar horarios disponibles
    horarios_disponibles = [h for h in horarios_trabajo if h not in horarios_ocupados]
    
    return horarios_disponibles

# Funciones de validación especiales siguen igual, ya funcionan con cliente_id
