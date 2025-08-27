# insert_services.py
from sqlalchemy.orm import Session
from app.core.config import get_tenant_db
from app.models.models import Servicio

def insert_services():
    """Inserta servicios de ejemplo en la base de datos"""
    db = next(get_tenant_db())
    
    # Lista de servicios de ejemplo
    servicios = [
        {
            "nombre": "Corte de cabello",
            "duracion_min": 30,
            "precio": 2500  # $25.00
        },
        {
            "nombre": "Arreglo de barba",
            "duracion_min": 20,
            "precio": 1500  # $15.00
        },
        {
            "nombre": "Corte + Barba",
            "duracion_min": 45,
            "precio": 3500  # $35.00
        },
        {
            "nombre": "Tinte",
            "duracion_min": 60,
            "precio": 5000  # $50.00
        },
        {
            "nombre": "Peinado",
            "duracion_min": 30,
            "precio": 2000  # $20.00
        }
    ]
    
    try:
        # Verificar si ya existen servicios
        existing_services = db.query(Servicio).count()
        if existing_services > 0:
            print(f"Ya existen {existing_services} servicios en la base de datos.")
            return
        
        # Insertar servicios
        for servicio_data in servicios:
            servicio = Servicio(**servicio_data)
            db.add(servicio)
        
        db.commit()
        print(f"Se insertaron {len(servicios)} servicios correctamente:")
        for servicio in servicios:
            print(f"- {servicio['nombre']}: ${servicio['precio']/100:.2f}")
            
    except Exception as e:
        print(f"Error al insertar servicios: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    insert_services()
