# create_db.py
from app.core.config import engine, Base
from app.models import models

def crear_base_de_datos():
    """Crea todas las tablas definidas en los modelos si no existen"""
    print("Creando base de datos y tablas...")
    Base.metadata.create_all(bind=engine)
    print("¡Base de datos y tablas creadas correctamente!")

if __name__ == "__main__":
    crear_base_de_datos()
