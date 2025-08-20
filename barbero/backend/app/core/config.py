from pydantic_settings import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

class Settings(BaseSettings):
    # Configuración de la base de datos SQLite
    DATABASE_URL: str = "sqlite:///./turnos.db"
    
    # Configuración de la aplicación
    APP_NAME: str = "Sistema de Gestión de Turnos"
    DEBUG: bool = True
    
    # Configuración de seguridad
    SECRET_KEY: str = "tu_clave_secreta_aqui_cambiar_en_produccion"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    class Config:
        env_file = ".env"

settings = Settings()

# Exportar variables para uso en otros módulos
SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
ALGORITHM = settings.ALGORITHM

# Crear el motor de la base de datos SQLite
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Necesario para SQLite
    echo=settings.DEBUG  # Mostrar SQL en consola si DEBUG=True
)

# Crear la sesión de la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Función para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
