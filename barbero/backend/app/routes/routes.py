from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, time
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

from app.core.config import get_db, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.crud import crud
from app.schemas import schemas

router = APIRouter()

# Configuración para JWT
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Endpoints de Autenticación
@router.post("/auth/login", tags=["autenticación"])
def login(credentials: schemas.LoginCredentials, db: Session = Depends(get_db)):
    """Iniciar sesión con email y contraseña"""
    # Buscar usuario por nombre de usuario
    db_usuario = crud.get_usuario_by_usuario(db, usuario=credentials.usuario)
    
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar contraseña usando bcrypt
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    if not pwd_context.verify(credentials.password, db_usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña incorrecta",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_usuario.usuario, "rol": db_usuario.rol}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_usuario.id,
            "usuario": db_usuario.usuario,
            "rol": db_usuario.rol,
            "nombre": db_usuario.nombre
        }
    }

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crear token de acceso JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Endpoints para Usuarios
@router.post("/usuarios/", response_model=schemas.Usuario, tags=["usuarios"])
def create_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    """Crear un nuevo usuario"""
    db_usuario = crud.get_usuario_by_usuario(db, usuario=usuario.usuario)
    if db_usuario:
        raise HTTPException(
            status_code=400,
            detail="El nombre de usuario ya está registrado"
        )
    return crud.create_usuario(db=db, usuario=usuario)

@router.get("/usuarios/", response_model=List[schemas.Usuario], tags=["usuarios"])
def read_usuarios(skip: int = 0, limit: int = 100, rol: Optional[str] = None, db: Session = Depends(get_db)):
    """Obtener lista de usuarios con filtro opcional por rol"""
    usuarios = crud.get_usuarios(db, skip=skip, limit=limit, rol=rol)
    return usuarios

@router.get("/usuarios/{usuario_id}", response_model=schemas.Usuario, tags=["usuarios"])
def read_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Obtener un usuario específico"""
    db_usuario = crud.get_usuario(db, usuario_id=usuario_id)
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_usuario

@router.put("/usuarios/{usuario_id}", response_model=schemas.Usuario, tags=["usuarios"])
def update_usuario(usuario_id: int, usuario: schemas.UsuarioUpdate, db: Session = Depends(get_db)):
    """Actualizar un usuario"""
    db_usuario = crud.update_usuario(db, usuario_id, usuario.dict(exclude_unset=True))
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_usuario

@router.delete("/usuarios/{usuario_id}", tags=["usuarios"])
def delete_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Eliminar un usuario"""
    success = crud.delete_usuario(db, usuario_id)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"message": "Usuario eliminado exitosamente"}

# Endpoints para Servicios
@router.post("/servicios/", response_model=schemas.Servicio, tags=["servicios"])
def create_servicio(servicio: schemas.ServicioCreate, db: Session = Depends(get_db)):
    """Crear un nuevo servicio"""
    return crud.create_servicio(db=db, servicio=servicio)

@router.get("/servicios/", response_model=List[schemas.Servicio], tags=["servicios"])
def read_servicios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener lista de servicios"""
    servicios = crud.get_servicios(db, skip=skip, limit=limit)
    return servicios

@router.get("/servicios/{servicio_id}", response_model=schemas.Servicio, tags=["servicios"])
def read_servicio(servicio_id: int, db: Session = Depends(get_db)):
    """Obtener un servicio específico"""
    db_servicio = crud.get_servicio(db, servicio_id=servicio_id)
    if db_servicio is None:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return db_servicio

@router.put("/servicios/{servicio_id}", response_model=schemas.Servicio, tags=["servicios"])
def update_servicio(servicio_id: int, servicio: schemas.ServicioUpdate, db: Session = Depends(get_db)):
    """Actualizar un servicio"""
    db_servicio = crud.update_servicio(db, servicio_id, servicio.dict(exclude_unset=True))
    if db_servicio is None:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return db_servicio

@router.delete("/servicios/{servicio_id}", tags=["servicios"])
def delete_servicio(servicio_id: int, db: Session = Depends(get_db)):
    """Eliminar un servicio"""
    success = crud.delete_servicio(db, servicio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return {"message": "Servicio eliminado exitosamente"}

# Endpoints para Turnos
@router.post("/turnos/", response_model=schemas.Turno, tags=["turnos"])
def create_turno(turno: schemas.TurnoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo turno"""
    # Verificar disponibilidad del horario
    if not crud.verificar_disponibilidad_turno(
        db, turno.fecha, turno.hora_inicio, turno.hora_fin
    ):
        raise HTTPException(
            status_code=400,
            detail="El horario no está disponible"
        )
    
    # Verificar si el cliente ya tiene un turno en esa semana
    if crud.verificar_turno_semanal_cliente(db, turno.cliente_id, turno.fecha):
        raise HTTPException(
            status_code=400,
            detail="El cliente ya tiene un turno en esta semana. Debe cancelar el turno existente primero."
        )
    
    return crud.create_turno(db=db, turno=turno)

@router.get("/turnos/", response_model=List[schemas.Turno], tags=["turnos"])
def read_turnos(
    skip: int = 0, 
    limit: int = 100, 
    cliente_id: Optional[int] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Obtener lista de turnos con filtros opcionales"""
    # Convertir strings de fecha a date si se proporcionan
    fecha_inicio_dt = None
    fecha_fin_dt = None
    
    if fecha_inicio:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    if fecha_fin:
        try:
            fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    turnos = crud.get_turnos(
        db, 
        skip=skip, 
        limit=limit, 
        cliente_id=cliente_id,
        fecha_inicio=fecha_inicio_dt,
        fecha_fin=fecha_fin_dt,
        estado=estado
    )
    return turnos

# Endpoints especiales para turnos (deben ir ANTES de las rutas con parámetros dinámicos)
@router.get("/turnos/estadisticas", tags=["turnos"])
def obtener_estadisticas_turnos(
    fecha_inicio: str,
    fecha_fin: str,
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de turnos en un rango de fechas"""
    try:
        fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    if fecha_inicio_dt > fecha_fin_dt:
        raise HTTPException(status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de fin")
    
    stats = crud.get_estadisticas_turnos(db, fecha_inicio_dt, fecha_fin_dt)
    
    return {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "estadisticas": stats
    }

@router.get("/turnos/fecha/{fecha}", response_model=List[schemas.Turno], tags=["turnos"])
def read_turnos_por_fecha(fecha: str, db: Session = Depends(get_db)):
    """Obtener turnos de una fecha específica (formato: YYYY-MM-DD)"""
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    turnos = crud.get_turnos_por_fecha(db, fecha_dt)
    return turnos

@router.get("/turnos/semana/{fecha}", response_model=List[schemas.Turno], tags=["turnos"])
def read_turnos_semana(fecha: str, db: Session = Depends(get_db)):
    """Obtener turnos de la semana de una fecha específica (formato: YYYY-MM-DD)"""
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    turnos = crud.get_turnos_semana(db, fecha_dt)
    return turnos

@router.get("/turnos/disponibilidad", tags=["turnos"])
def verificar_disponibilidad(
    fecha: str, 
    hora_inicio: str, 
    hora_fin: str,
    db: Session = Depends(get_db)
):
    """Verificar disponibilidad de un horario específico"""
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
        hora_inicio_dt = datetime.strptime(hora_inicio, "%H:%M").time()
        hora_fin_dt = datetime.strptime(hora_fin, "%H:%M").time()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha/hora inválido")
    
    disponible = crud.verificar_disponibilidad_turno(
        db, fecha_dt, hora_inicio_dt, hora_fin_dt
    )
    
    return {
        "fecha": fecha,
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin,
        "disponible": disponible
    }

@router.get("/turnos/cliente/{cliente_id}/semana/{fecha}", tags=["turnos"])
def verificar_turno_semanal_cliente(
    cliente_id: int, 
    fecha: str, 
    db: Session = Depends(get_db)
):
    """Verificar si un cliente tiene turno en la semana de una fecha específica"""
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    tiene_turno = crud.verificar_turno_semanal_cliente(db, cliente_id, fecha_dt)
    
    return {
        "cliente_id": cliente_id,
        "fecha": fecha,
        "tiene_turno_semana": tiene_turno
    }

@router.post("/turnos/cliente/{cliente_id}/cancelar-semana", tags=["turnos"])
def cancelar_turnos_cliente_semana(
    cliente_id: int, 
    fecha: str, 
    db: Session = Depends(get_db)
):
    """Cancelar todos los turnos activos de un cliente en la semana de una fecha específica"""
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    turnos_cancelados = crud.delete_turnos_cliente_semana(db, cliente_id, fecha_dt)
    
    return {
        "cliente_id": cliente_id,
        "fecha": fecha,
        "turnos_cancelados": turnos_cancelados,
        "message": f"Se cancelaron {turnos_cancelados} turnos"
    }

# Rutas con parámetros dinámicos (deben ir DESPUÉS de las rutas específicas)
@router.get("/turnos/{turno_id}", response_model=schemas.Turno, tags=["turnos"])
def read_turno(turno_id: int, db: Session = Depends(get_db)):
    """Obtener un turno específico"""
    db_turno = crud.get_turno(db, turno_id=turno_id)
    if db_turno is None:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    return db_turno

@router.put("/turnos/{turno_id}", response_model=schemas.Turno, tags=["turnos"])
def update_turno(turno_id: int, turno: schemas.TurnoUpdate, db: Session = Depends(get_db)):
    """Actualizar un turno"""
    # Si se está cambiando la fecha/hora, verificar disponibilidad
    if turno.fecha or turno.hora_inicio or turno.hora_fin:
        db_turno_actual = crud.get_turno(db, turno_id)
        if db_turno_actual:
            fecha = turno.fecha or db_turno_actual.fecha
            hora_inicio = turno.hora_inicio or db_turno_actual.hora_inicio
            hora_fin = turno.hora_fin or db_turno_actual.hora_fin
            
            if not crud.verificar_disponibilidad_turno(
                db, fecha, hora_inicio, hora_fin, turno_id
            ):
                raise HTTPException(
                    status_code=400,
                    detail="El horario no está disponible"
                )
    
    db_turno = crud.update_turno(db, turno_id, turno.dict(exclude_unset=True))
    if db_turno is None:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    return db_turno

@router.delete("/turnos/{turno_id}", tags=["turnos"])
def delete_turno(turno_id: int, db: Session = Depends(get_db)):
    """Eliminar un turno"""
    success = crud.delete_turno(db, turno_id)
    if not success:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    return {"message": "Turno eliminado exitosamente"}

# Endpoints especiales para turnos
@router.get("/turnos/fecha/{fecha}", response_model=List[schemas.Turno], tags=["turnos"])
def read_turnos_por_fecha(fecha: str, db: Session = Depends(get_db)):
    """Obtener turnos de una fecha específica (formato: YYYY-MM-DD)"""
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    turnos = crud.get_turnos_por_fecha(db, fecha_dt)
    return turnos

@router.get("/turnos/semana/{fecha}", response_model=List[schemas.Turno], tags=["turnos"])
def read_turnos_semana(fecha: str, db: Session = Depends(get_db)):
    """Obtener turnos de la semana de una fecha específica (formato: YYYY-MM-DD)"""
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    turnos = crud.get_turnos_semana(db, fecha_dt)
    return turnos

@router.get("/turnos/disponibilidad", tags=["turnos"])
def verificar_disponibilidad(
    fecha: str, 
    hora_inicio: str, 
    hora_fin: str,
    db: Session = Depends(get_db)
):
    """Verificar disponibilidad de un horario específico"""
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
        hora_inicio_dt = datetime.strptime(hora_inicio, "%H:%M").time()
        hora_fin_dt = datetime.strptime(hora_fin, "%H:%M").time()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha/hora inválido")
    
    disponible = crud.verificar_disponibilidad_turno(
        db, fecha_dt, hora_inicio_dt, hora_fin_dt
    )
    
    return {
        "fecha": fecha,
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin,
        "disponible": disponible
    }

@router.get("/turnos/cliente/{cliente_id}/semana/{fecha}", tags=["turnos"])
def verificar_turno_semanal_cliente(
    cliente_id: int, 
    fecha: str, 
    db: Session = Depends(get_db)
):
    """Verificar si un cliente tiene turno en la semana de una fecha específica"""
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    tiene_turno = crud.verificar_turno_semanal_cliente(db, cliente_id, fecha_dt)
    
    return {
        "cliente_id": cliente_id,
        "fecha": fecha,
        "tiene_turno_semana": tiene_turno
    }

@router.post("/turnos/cliente/{cliente_id}/cancelar-semana", tags=["turnos"])
def cancelar_turnos_cliente_semana(
    cliente_id: int, 
    fecha: str, 
    db: Session = Depends(get_db)
):
    """Cancelar todos los turnos activos de un cliente en la semana de una fecha específica"""
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    turnos_cancelados = crud.cancelar_turnos_cliente_semana(db, cliente_id, fecha_dt)
    
    return {
        "cliente_id": cliente_id,
        "fecha": fecha,
        "turnos_cancelados": turnos_cancelados,
        "message": f"Se cancelaron {turnos_cancelados} turnos"
    }
