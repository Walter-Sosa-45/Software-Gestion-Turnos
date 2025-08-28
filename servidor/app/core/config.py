import os
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator, Optional


class Settings(BaseSettings):
    # Configuración de la aplicación
    APP_NAME: str = "Sistema de Gestión de Turnos"
    DEBUG: bool = True

    # Seguridad
    SECRET_KEY: str = "tu_clave_secreta_aqui_cambiar_en_produccion"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # Base de datos (PostgreSQL)
    DATABASE_URL: str | None = None

    class Config:
        extra = "ignore"
        env_file = ".env"


settings = Settings()

# Exportables
SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
ALGORITHM = settings.ALGORITHM

# Solo una base declarativa
Base = declarative_base()
TenantBase = declarative_base()

# Motor y fábrica de sesión para la única base de datos
tenant_engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)
TenantSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=tenant_engine)


def get_tenant_db(tenant_db_url: Optional[str] = None) -> Generator:
    # Permite inyectar otra barbería si se pasa un URL
    if tenant_db_url:
        Session = sessionmaker(autocommit=False, autoflush=False, bind=create_engine(tenant_db_url, echo=settings.DEBUG, pool_pre_ping=True))
    else:
        Session = TenantSessionLocal
    db = Session()
    try:
        yield db
    finally:
        db.close()
