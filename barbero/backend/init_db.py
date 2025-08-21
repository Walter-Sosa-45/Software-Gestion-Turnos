#!/usr/bin/env python3
"""
Script para inicializar la base de datos SQLite del Sistema de Gestión de Turnos
"""

import os
import sys
from pathlib import Path

# Agregar el directorio app al path
sys.path.append(str(Path(__file__).parent / "app"))

from app.core.config import engine, Base
from app.models.models import Usuario, Servicio, Turno
from app.crud.crud import create_usuario, create_servicio
from sqlalchemy.orm import Session
from app.core.config import SessionLocal
from passlib.context import CryptContext

# Configurar el contexto de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_database():
    """Inicializar la base de datos creando todas las tablas"""
    print("🔧 Creando tablas de la base de datos...")
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente")
    
    # Crear datos iniciales
    create_initial_data()
    
    print("🎉 Base de datos inicializada correctamente!")

def create_initial_data():
    """Crear datos iniciales para la aplicación"""
    print("📝 Creando datos iniciales...")
    
    db = SessionLocal()
    try:
        # Verificar si ya existen datos
        if db.query(Usuario).first():
            print("ℹ️  La base de datos ya contiene datos, saltando creación inicial")
            return
        
        # Crear usuario admin/barbero
        admin_user = Usuario(
            nombre="Barbero Principal",
            usuario="admin",
            password_hash=pwd_context.hash("admin123"),
            rol="admin"
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print("👤 Usuario admin creado: admin@barberia.com / admin123")
        
        # Crear servicios básicos
        servicios = [
            {"nombre": "Corte de cabello", "duracion_min": 30, "precio": 2500},
            {"nombre": "Arreglo de barba", "duracion_min": 20, "precio": 1500},
            {"nombre": "Corte + Barba", "duracion_min": 45, "precio": 3500},
            {"nombre": "Tinte", "duracion_min": 60, "precio": 5000},
            {"nombre": "Peinado", "duracion_min": 30, "precio": 2000}
        ]
        
        for servicio_data in servicios:
            servicio = Servicio(**servicio_data)
            db.add(servicio)
        
        db.commit()
        print("✂️  Servicios básicos creados")
        
        # Crear algunos clientes de ejemplo
        clientes = [
            {"nombre": "Juan Pérez", "usuario": "juan", "password_hash": pwd_context.hash("cliente123"), "rol": "cliente"},
            {"nombre": "María García", "usuario": "maria", "password_hash": pwd_context.hash("cliente123"), "rol": "cliente"},
            {"nombre": "Carlos López", "usuario": "carlos", "password_hash": pwd_context.hash("cliente123"), "rol": "cliente"}
        ]
        
        for cliente_data in clientes:
            cliente = Usuario(**cliente_data)
            db.add(cliente)
        
        db.commit()
        print("👥 Clientes de ejemplo creados")
        
    except Exception as e:
        print(f"❌ Error creando datos iniciales: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Inicializando base de datos SQLite...")
    init_database()
    print("\n📋 Información de acceso:")
    print("   Admin: admin / admin123")
    print("   Clientes: juan / cliente123")
    print("   Base de datos: turnos.db")
