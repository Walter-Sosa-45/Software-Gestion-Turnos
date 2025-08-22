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

    # Bases de datos (PostgreSQL)
    # Global: usuarios del sistema
    GLOBAL_DATABASE_URL: str = (
        "postgresql+psycopg://postgres:4585874556@localhost/software-gestion-turnos-usuarios"
    )
    # Tenant: por barbería; por defecto juancho-barber
    DEFAULT_TENANT_DATABASE_URL: str = (
        "postgresql+psycopg://postgres:4585874556@localhost/juancho-barber"
    )

    class Config:
        env_file = ".env"


settings = Settings()

# Exportables
SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
ALGORITHM = settings.ALGORITHM

# Bases separadas para modelos
GlobalBase = declarative_base()
TenantBase = declarative_base()

# Motores y fábricas de sesión
global_engine = create_engine(
    settings.GLOBAL_DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

def _create_tenant_engine(database_url: Optional[str] = None):
    return create_engine(
        database_url or settings.DEFAULT_TENANT_DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )

tenant_engine = _create_tenant_engine()

GlobalSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=global_engine)
TenantSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=tenant_engine)


def get_global_db() -> Generator:
    db = GlobalSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_tenant_db(tenant_db_url: Optional[str] = None) -> Generator:
    # Permite inyectar otra barbería si se pasa un URL
    if tenant_db_url:
        Session = sessionmaker(autocommit=False, autoflush=False, bind=_create_tenant_engine(tenant_db_url))
    else:
        Session = TenantSessionLocal
    db = Session()
    try:
        yield db
    finally:
        db.close()
