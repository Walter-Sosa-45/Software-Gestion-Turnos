"""Crea tablas en la base de datos del tenant (clientes/servicios/turnos)."""
from app.core.config import tenant_engine, TenantBase  # <<--- cambiar Base por TenantBase
from app.models import models  # importa definiciones


def crear_base_de_datos():
    print("Creando tablas en base TENANT (barbería)...")
    TenantBase.metadata.create_all(bind=tenant_engine)  # <<--- usar TenantBase
    print("OK base TENANT")


if __name__ == "__main__":
    crear_base_de_datos()
