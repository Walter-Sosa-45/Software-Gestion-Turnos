#!/usr/bin/env python3
"""
Script de inicio rápido para desarrollo
Inicializa la base de datos y ejecuta el backend
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Ejecutar un comando y mostrar descripción"""
    print(f"\n🚀 {description}...")
    print(f"📝 Comando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado exitosamente")
        if result.stdout:
            print(f"📤 Salida: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        if e.stderr:
            print(f"📤 Error: {e.stderr.strip()}")
        return False

def check_python():
    """Verificar que Python esté disponible"""
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"🐍 Python detectado: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"❌ Error detectando Python: {e}")
        return False

def check_venv():
    """Verificar si el entorno virtual existe"""
    venv_path = Path("backend/venv")
    if venv_path.exists():
        print(f"✅ Entorno virtual encontrado en: {venv_path}")
        return True
    else:
        print(f"⚠️  Entorno virtual no encontrado en: {venv_path}")
        return False

def create_venv():
    """Crear entorno virtual"""
    print("\n🔧 Creando entorno virtual...")
    
    # Cambiar al directorio backend
    os.chdir("backend")
    
    # Crear entorno virtual
    if not run_command(f"{sys.executable} -m venv venv", "Creando entorno virtual"):
        return False
    
    print("✅ Entorno virtual creado exitosamente")
    return True

def install_dependencies():
    """Instalar dependencias Python"""
    print("\n📦 Instalando dependencias...")
    
    # Activar entorno virtual e instalar dependencias
    if os.name == "nt":  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Linux/Mac
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # Instalar dependencias
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Instalando dependencias"):
        return False
    
    return True

def init_database():
    """Inicializar base de datos"""
    print("\n🗄️  Inicializando base de datos...")
    
    # Ejecutar script de inicialización
    if not run_command(f"{sys.executable} init_db.py", "Inicializando base de datos"):
        return False
    
    return True

def start_backend():
    """Iniciar el backend"""
    print("\n🚀 Iniciando backend...")
    
    # Ejecutar el backend
    if not run_command(f"{sys.executable} -m app.main", "Iniciando servidor backend"):
        return False
    
    return True

def main():
    """Función principal"""
    print("🎯 Sistema de Gestión de Turnos - Inicio Rápido")
    print("=" * 50)
    
    # Verificar Python
    if not check_python():
        print("❌ Python no está disponible. Instala Python 3.8+ y vuelve a intentar.")
        return
    
    # Verificar estructura del proyecto
    if not Path("backend").exists():
        print("❌ Directorio 'backend' no encontrado. Ejecuta este script desde la raíz del proyecto.")
        return
    
    # Cambiar al directorio backend
    original_dir = os.getcwd()
    os.chdir("backend")
    
    try:
        # Verificar entorno virtual
        if not check_venv():
            if not create_venv():
                print("❌ No se pudo crear el entorno virtual")
                return
        
        # Instalar dependencias
        if not install_dependencies():
            print("❌ No se pudieron instalar las dependencias")
            return
        
        # Inicializar base de datos
        if not init_database():
            print("❌ No se pudo inicializar la base de datos")
            return
        
        print("\n🎉 ¡Configuración completada exitosamente!")
        print("\n📋 Próximos pasos:")
        print("   1. El backend se iniciará automáticamente")
        print("   2. Abre: http://localhost:8000/docs")
        print("   3. Para el frontend, abre otra terminal y ejecuta:")
        print("      cd frontend && npm install && npm run dev")
        print("\n🔑 Credenciales de acceso:")
        print("   Admin: admin@barberia.com / admin123")
        print("   Cliente: juan@email.com / cliente123")
        
        # Iniciar backend
        start_backend()
        
    except KeyboardInterrupt:
        print("\n\n👋 Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    finally:
        # Volver al directorio original
        os.chdir(original_dir)

if __name__ == "__main__":
    main()
