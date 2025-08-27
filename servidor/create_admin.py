"""Crea un usuario admin en la base TENANT (ej: juancho-barber)."""
from app.core.config import TenantSessionLocal
from app.models.models import Usuario
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def crear_admin():
    db = TenantSessionLocal()
    try:
        # Verificar si ya existe un admin
        admin_existente = db.query(Usuario).filter(Usuario.usuario == "admin").first()
        if admin_existente:
            print("El usuario admin ya existe.")
            return

        # Crear usuario admin
        password_hash = pwd_context.hash("admin123")
        nuevo_admin = Usuario(
            nombre="Administrador",
            usuario="admin",
            password_hash=password_hash,
            rol="admin"
        )
        db.add(nuevo_admin)
        db.commit()
        print("Usuario admin creado correctamente en juancho-barber: usuario='admin', password='admin123'")
    except IntegrityError:
        db.rollback()
        print("Error al crear el usuario admin. Probablemente ya existe.")
    finally:
        db.close()

if __name__ == "__main__":
    crear_admin()
