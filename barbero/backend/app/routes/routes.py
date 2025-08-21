from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, time, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.core.config import get_db, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.crud import crud
from app.schemas import schemas

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- JWT Helpers ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Autenticación ---
@router.post("/auth/login", tags=["autenticación"])
def login(credentials: schemas.LoginCredentials, db: Session = Depends(get_db)):
    db_usuario = crud.get_usuario_by_usuario(db, usuario=credentials.usuario)
    if not db_usuario or not pwd_context.verify(credentials.password, db_usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": db_usuario.usuario, "rol": db_usuario.rol},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
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

# --- Usuarios ---
@router.post("/usuarios/", response_model=schemas.Usuario, tags=["usuarios"])
def create_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    if crud.get_usuario_by_usuario(db, usuario.usuario):
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    return crud.create_usuario(db=db, usuario=usuario)

@router.get("/usuarios/", response_model=List[schemas.Usuario], tags=["usuarios"])
def read_usuarios(skip: int = 0, limit: int = 100, rol: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.get_usuarios(db, skip=skip, limit=limit, rol=rol)

# --- Servicios ---
@router.post("/servicios/", response_model=schemas.Servicio, tags=["servicios"])
def create_servicio(servicio: schemas.ServicioCreate, db: Session = Depends(get_db)):
    return crud.create_servicio(db=db, servicio=servicio)

@router.get("/servicios/", response_model=List[schemas.Servicio], tags=["servicios"])
def read_servicios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_servicios(db, skip=skip, limit=limit)

# --- Endpoints adicionales para servicios ---
@router.get("/servicios/{servicio_id}", response_model=schemas.Servicio, tags=["servicios"])
def get_servicio(servicio_id: int, db: Session = Depends(get_db)):
    """Obtiene un servicio específico por ID"""
    servicio = crud.get_servicio(db, servicio_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return servicio

@router.put("/servicios/{servicio_id}", response_model=schemas.Servicio, tags=["servicios"])
def update_servicio(servicio_id: int, servicio_update: dict, db: Session = Depends(get_db)):
    """Actualiza un servicio existente"""
    try:
        servicio = crud.get_servicio(db, servicio_id)
        if not servicio:
            raise HTTPException(status_code=404, detail="Servicio no encontrado")
        
        # Actualizar campos
        for field, value in servicio_update.items():
            if hasattr(servicio, field):
                setattr(servicio, field, value)
        
        db.commit()
        db.refresh(servicio)
        return servicio
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar servicio: {str(e)}")

# --- Endpoints adicionales para usuarios ---
@router.get("/usuarios/{usuario_id}", response_model=schemas.Usuario, tags=["usuarios"])
def get_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Obtiene un usuario específico por ID"""
    usuario = crud.get_usuario(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@router.put("/usuarios/{usuario_id}", response_model=schemas.Usuario, tags=["usuarios"])
def update_usuario(usuario_id: int, usuario_update: dict, db: Session = Depends(get_db)):
    """Actualiza un usuario existente"""
    try:
        usuario = crud.get_usuario(db, usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Actualizar campos (excluyendo password_hash por seguridad)
        for field, value in usuario_update.items():
            if field != "password_hash" and hasattr(usuario, field):
                setattr(usuario, field, value)
        
        db.commit()
        db.refresh(usuario)
        return usuario
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar usuario: {str(e)}")

# --- Turnos ---
@router.get("/turnos/", tags=["turnos"])
def read_turnos(
    skip: int = 0,
    limit: int = 100,
    cliente_id: Optional[int] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d").date() if fecha_inicio else None
        fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d").date() if fecha_fin else None
        turnos = crud.get_turnos(db, skip, limit, cliente_id, fecha_inicio_dt, fecha_fin_dt, estado)
        return {"turnos": turnos}
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener turnos: {str(e)}")

# --- Endpoint para obtener horarios disponibles ---
@router.get("/turnos/disponibilidad", tags=["turnos"])
def get_horarios_disponibles(fecha: str, db: Session = Depends(get_db)):
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
        horarios = crud.get_horarios_disponibles(db, fecha_dt)
        return {"horarios_disponibles": horarios}
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener horarios: {str(e)}")

# --- Crear turno desde cliente (frontend) ---
@router.post("/turnos/", tags=["turnos"])
def crear_turno_desde_cliente(turno_data: dict, db: Session = Depends(get_db)):
    try:
        nombre = turno_data.get("nombre")
        apellido = turno_data.get("apellido")
        telefono = turno_data.get("telefono")
        servicio_nombre = turno_data.get("servicio")
        fecha_str = turno_data.get("fecha")
        hora_str = turno_data.get("hora")

        if not all([nombre, apellido, telefono, servicio_nombre, fecha_str, hora_str]):
            raise HTTPException(status_code=400, detail="Todos los campos son requeridos")

        fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        hora_dt = datetime.strptime(hora_str, "%H:%M").time()
        hora_fin_dt = (datetime.combine(fecha_dt, hora_dt) + timedelta(minutes=30)).time()

        # Buscar o crear cliente
        cliente = crud.get_cliente_by_telefono(db, telefono)
        if not cliente:
            cliente = crud.create_cliente(db, f"{nombre} {apellido}", telefono)

        # Buscar servicio
        servicio = crud.get_servicio_by_nombre(db, servicio_nombre)
        if not servicio:
            raise HTTPException(status_code=400, detail="Servicio no encontrado")

        # Verificar disponibilidad
        if not crud.verificar_disponibilidad_turno(db, fecha_dt, hora_dt, hora_fin_dt):
            raise HTTPException(status_code=400, detail="El horario no está disponible")

        # Crear turno
        turno = crud.create_turno(db, cliente.id, servicio.id, fecha_dt, hora_dt, hora_fin_dt)

        return {
            "message": "Turno creado exitosamente",
            "turno_id": turno.id,
            "cliente": cliente.nombre,
            "servicio": servicio.nombre,
            "fecha": fecha_str,
            "hora": hora_str
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear turno: {str(e)}")

# --- Crear turno desde cliente (frontend) ---
@router.post("/turnos/crear-desde-cliente", tags=["turnos"])
def crear_turno_desde_cliente_legacy(turno_data: dict, db: Session = Depends(get_db)):
    try:
        nombre = turno_data.get("nombre")
        apellido = turno_data.get("apellido")
        telefono = turno_data.get("telefono")
        servicio_nombre = turno_data.get("servicio")
        fecha_str = turno_data.get("fecha")
        hora_str = turno_data.get("hora")

        if not all([nombre, apellido, telefono, servicio_nombre, fecha_str, hora_str]):
            raise HTTPException(status_code=400, detail="Todos los campos son requeridos")

        fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        hora_dt = datetime.strptime(hora_str, "%H:%M").time()
        hora_fin_dt = (datetime.combine(fecha_dt, hora_dt) + timedelta(minutes=30)).time()

        # Buscar o crear cliente
        cliente = crud.get_cliente_by_telefono(db, telefono)
        if not cliente:
            cliente = crud.create_cliente(db, f"{nombre} {apellido}", telefono)

        # Buscar servicio
        servicio = crud.get_servicio_by_nombre(db, servicio_nombre)
        if not servicio:
            raise HTTPException(status_code=400, detail="Servicio no encontrado")

        # Verificar disponibilidad
        if not crud.verificar_disponibilidad_turno(db, fecha_dt, hora_dt, hora_fin_dt):
            raise HTTPException(status_code=400, detail="El horario no está disponible")

        # Crear turno
        turno = crud.create_turno(db, cliente.id, servicio.id, fecha_dt, hora_dt, hora_fin_dt)

        return {
            "message": "Turno creado exitosamente",
            "turno_id": turno.id,
            "cliente": cliente.nombre,
            "servicio": servicio.nombre,
            "fecha": fecha_str,
            "hora": hora_str
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear turno: {str(e)}")

# --- Endpoints adicionales para el frontend del barbero ---

@router.get("/turnos/fecha/{fecha}", tags=["turnos"])
def get_turnos_por_fecha(fecha: str, db: Session = Depends(get_db)):
    """Obtiene todos los turnos para una fecha específica"""
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
        turnos = crud.get_turnos(db, fecha_inicio=fecha_dt, fecha_fin=fecha_dt)
        return {"turnos": turnos}
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")

@router.get("/turnos/semana/{fecha}", response_model=List[schemas.Turno], tags=["turnos"])
def get_turnos_semana(fecha: str, db: Session = Depends(get_db)):
    """Obtiene todos los turnos para la semana que contiene la fecha especificada"""
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
        # Calcular inicio y fin de la semana (lunes a domingo)
        inicio_semana = fecha_dt - timedelta(days=fecha_dt.weekday())
        fin_semana = inicio_semana + timedelta(days=6)
        turnos = crud.get_turnos(db, fecha_inicio=inicio_semana, fecha_fin=fin_semana)
        return turnos
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")

@router.put("/turnos/{turno_id}", response_model=schemas.Turno, tags=["turnos"])
def update_turno(turno_id: int, turno_update: dict, db: Session = Depends(get_db)):
    """Actualiza un turno existente"""
    try:
        turno = crud.update_turno(db, turno_id, turno_update)
        if not turno:
            raise HTTPException(status_code=404, detail="Turno no encontrado")
        return turno
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar turno: {str(e)}")

@router.delete("/turnos/{turno_id}", tags=["turnos"])
def delete_turno(turno_id: int, db: Session = Depends(get_db)):
    """Elimina un turno"""
    try:
        success = crud.delete_turno(db, turno_id)
        if not success:
            raise HTTPException(status_code=404, detail="Turno no encontrado")
        return {"message": "Turno eliminado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar turno: {str(e)}")

@router.get("/turnos/estadisticas", tags=["turnos"])
def get_estadisticas_turnos(fecha_inicio: str, fecha_fin: str, db: Session = Depends(get_db)):
    """Obtiene estadísticas de turnos para un rango de fechas"""
    try:
        fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        
        turnos = crud.get_turnos(db, fecha_inicio=fecha_inicio_dt, fecha_fin=fecha_fin_dt)
        
        # Calcular estadísticas básicas
        total_turnos = len(turnos)
        turnos_confirmados = len([t for t in turnos if t.estado == "confirmado"])
        turnos_completados = len([t for t in turnos if t.estado == "completado"])
        turnos_cancelados = len([t for t in turnos if t.estado == "cancelado"])
        
        estadisticas = {
            "total_turnos": total_turnos,
            "confirmados": turnos_confirmados,
            "completados": turnos_completados,
            "cancelados": turnos_cancelados,
            "pendientes": total_turnos - turnos_confirmados - turnos_completados - turnos_cancelados
        }
        
        return {"estadisticas": estadisticas}
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
