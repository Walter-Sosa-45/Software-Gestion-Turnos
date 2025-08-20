from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime, date, time

# Esquemas base
class UsuarioBase(BaseModel):
    nombre: str
    usuario: str
    rol: str

    @validator('rol')
    def validate_rol(cls, v):
        if v not in ['admin', 'cliente']:
            raise ValueError('El rol debe ser "admin" o "cliente"')
        return v

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    rol: Optional[str] = None

    @validator('rol')
    def validate_rol(cls, v):
        if v is not None and v not in ['admin', 'cliente']:
            raise ValueError('El rol debe ser "admin" o "cliente"')
        return v

class Usuario(UsuarioBase):
    id: int
    fecha_registro: datetime
    
    class Config:
        from_attributes = True

class UsuarioLogin(BaseModel):
    usuario: str
    password: str

class LoginCredentials(BaseModel):
    usuario: str
    password: str

# Esquemas para servicios
class ServicioBase(BaseModel):
    nombre: str
    duracion_min: int
    precio: int  # Precio en centavos

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
        from_attributes = True

# Esquemas para turnos
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
        if 'hora_inicio' in values and v <= values['hora_inicio']:
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
    cliente: Usuario
    servicio: Servicio
    
    class Config:
        from_attributes = True

# Esquemas para respuestas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Esquemas para listas
class UsuarioList(BaseModel):
    usuarios: List[Usuario]

class ServicioList(BaseModel):
    servicios: List[Servicio]

class TurnoList(BaseModel):
    turnos: List[Turno]

# Esquemas especiales para turnos
class TurnoSemanal(BaseModel):
    """Esquema para verificar turnos semanales de un cliente"""
    cliente_id: int
    fecha_inicio: date
    fecha_fin: date
    turnos_existentes: List[Turno]

class DisponibilidadTurno(BaseModel):
    """Esquema para verificar disponibilidad de un horario"""
    fecha: date
    hora_inicio: time
    hora_fin: time
    disponible: bool
    turnos_conflictivos: Optional[List[Turno]] = None
