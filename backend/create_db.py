"""Crea tablas en ambas bases: global (usuarios) y tenant (clientes/servicios/turnos)."""
from app.core.config import global_engine, tenant_engine, GlobalBase, TenantBase
from app.models import models  # importa definiciones


def crear_base_de_datos():
    print("Creando tablas en base GLOBAL (usuarios)...")
    GlobalBase.metadata.create_all(bind=global_engine)
    print("OK base GLOBAL")

    print("Creando tablas en base TENANT (barbería)...")
    TenantBase.metadata.create_all(bind=tenant_engine)
    print("OK base TENANT")

if __name__ == "__main__":
    crear_base_de_datos()
