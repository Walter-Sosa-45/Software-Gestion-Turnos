from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime, date, time

# ---------------------------
# Esquemas para Usuarios
# ---------------------------
class UsuarioBase(BaseModel):
    nombre: str
    usuario: str
    rol: str

    @validator('rol')
    def validate_rol(cls, v):
        if v not in ['admin', 'barbero', 'cliente']:
            raise ValueError('El rol debe ser "admin", "barbero" o "cliente"')
        return v

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    usuario: Optional[str] = None
    rol: Optional[str] = None

    @validator('rol')
    def validate_rol(cls, v):
        if v is not None and v not in ['admin', 'barbero', 'cliente']:
            raise ValueError('El rol debe ser "admin", "barbero" o "cliente"')
        return v

class Usuario(UsuarioBase):
    id: int
    fecha_registro: datetime

    class Config:
        orm_mode = True

class LoginCredentials(BaseModel):
    usuario: str
    password: str

# ---------------------------
# Esquemas para Clientes
# ---------------------------
class ClienteBase(BaseModel):
    nombre: str
    telefono: str

class ClienteCreate(ClienteBase):
    pass

class Cliente(ClienteBase):
    id: int
    fecha_registro: datetime

    class Config:
        orm_mode = True

# ---------------------------
# Esquemas para Servicios
# ---------------------------
class ServicioBase(BaseModel):
    nombre: str
    duracion_min: int
    precio: int  # en centavos

    @validator('duracion_min')
    def validate_duracion(cls, v):
        if v <= 0:
            raise ValueError('La duración debe ser mayor a 0')
        return v

    @validator('precio')
    def validate_precio(cls, v):
        if v < 0:
            raise ValueError('El precio no puede ser negativo')
        return v

class ServicioCreate(ServicioBase):
    pass

class ServicioUpdate(BaseModel):
    nombre: Optional[str] = None
    duracion_min: Optional[int] = None
    precio: Optional[int] = None

    @validator('duracion_min')
    def validate_duracion(cls, v):
        if v is not None and v <= 0:
            raise ValueError('La duración debe ser mayor a 0')
        return v

    @validator('precio')
    def validate_precio(cls, v):
        if v is not None and v < 0:
            raise ValueError('El precio no puede ser negativo')
        return v

class Servicio(ServicioBase):
    id: int

    class Config:
        orm_mode = True

# ---------------------------
# Esquemas para Turnos
# ---------------------------
class TurnoBase(BaseModel):
    cliente_id: int
    servicio_id: int
    fecha: date
    hora_inicio: time
    hora_fin: time
    estado: str

    @validator('estado')
    def validate_estado(cls, v):
        if v not in ['pendiente', 'confirmado', 'cancelado', 'completado']:
            raise ValueError('El estado debe ser: pendiente, confirmado, cancelado o completado')
        return v

    @validator('hora_fin')
    def validate_hora_fin(cls, v, values):
        if 'hora_inicio' in values and values['hora_inicio'] is not None:
            if v <= values['hora_inicio']:
                raise ValueError('La hora de fin debe ser posterior a la hora de inicio')
        return v

class TurnoCreate(TurnoBase):
    pass

class TurnoUpdate(BaseModel):
    fecha: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    estado: Optional[str] = None

    @validator('estado')
    def validate_estado(cls, v):
        if v is not None and v not in ['pendiente', 'confirmado', 'cancelado', 'completado']:
            raise ValueError('El estado debe ser: pendiente, confirmado, cancelado o completado')
        return v

    @validator('hora_fin')
    def validate_hora_fin(cls, v, values):
        if v is not None and 'hora_inicio' in values and values['hora_inicio'] is not None:
            if v <= values['hora_inicio']:
                raise ValueError('La hora de fin debe ser posterior a la hora de inicio')
        return v

class Turno(TurnoBase):
    id: int
    creado_en: datetime
    cliente: Cliente
    servicio: Servicio

    class Config:
        orm_mode = True

# ---------------------------
# Esquemas para Bloqueos
# ---------------------------
class BloqueoBase(BaseModel):
    fecha: date
    todo_dia: bool = False
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    motivo: Optional[str] = None

    @validator('hora_fin')
    def validate_hora_fin(cls, v, values):
        if not values.get('todo_dia'):
            # si no es todo el día, ambas horas deben existir y ser válidas
            if values.get('hora_inicio') is None or v is None:
                raise ValueError('Debe especificar hora_inicio y hora_fin cuando no es todo el día')
            if v <= values['hora_inicio']:
                raise ValueError('hora_fin debe ser posterior a hora_inicio')
        return v

class BloqueoCreate(BloqueoBase):
    pass

class Bloqueo(BloqueoBase):
    id: int
    creado_en: datetime

    class Config:
        orm_mode = True

# ---------------------------
# Esquemas para JWT / Tokens
# ---------------------------
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    usuario: Optional[str] = None

# ---------------------------
# Esquemas de listas (opcional)
# ---------------------------
class UsuarioList(BaseModel):
    usuarios: List[Usuario]

class ServicioList(BaseModel):
    servicios: List[Servicio]

class TurnoList(BaseModel):
    turnos: List[Turno]

# ---------------------------
# Esquemas especiales para turnos
# ---------------------------
class TurnoSemanal(BaseModel):
    cliente_id: int
    fecha_inicio: date
    fecha_fin: date
    turnos_existentes: List[Turno]

class DisponibilidadTurno(BaseModel):
    fecha: date
    hora_inicio: time
    hora_fin: time
    disponible: bool
    turnos_conflictivos: Optional[List[Turno]] = None
