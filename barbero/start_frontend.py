#!/usr/bin/env python3
"""
Script de inicio rápido para el frontend
Instala dependencias y ejecuta la aplicación React
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description, cwd=None):
    """Ejecutar un comando y mostrar descripción"""
    print(f"\n🚀 {description}...")
    print(f"📝 Comando: {command}")
    if cwd:
        print(f"📁 Directorio: {cwd}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            cwd=cwd
        )
        print(f"✅ {description} completado exitosamente")
        if result.stdout:
            print(f"📤 Salida: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        if e.stderr:
            print(f"📤 Error: {e.stderr.strip()}")
        return False

def check_node():
    """Verificar que Node.js esté disponible"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        print(f"🟢 Node.js detectado: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"❌ Error detectando Node.js: {e}")
        return False

def check_npm():
    """Verificar que npm esté disponible"""
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        print(f"📦 npm detectado: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"❌ Error detectando npm: {e}")
        return False

def install_dependencies():
    """Instalar dependencias del frontend"""
    print("\n📦 Instalando dependencias del frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Directorio 'frontend' no encontrado")
        return False
    
    # Instalar dependencias
    if not run_command("npm install", "Instalando dependencias npm", cwd=frontend_dir):
        return False
    
    return True

def start_frontend():
    """Iniciar el frontend en modo desarrollo"""
    print("\n🚀 Iniciando frontend...")
    
    frontend_dir = Path("frontend")
    
    # Ejecutar en modo desarrollo
    if not run_command("npm run dev", "Iniciando servidor de desarrollo", cwd=frontend_dir):
        return False
    
    return True

def main():
    """Función principal"""
    print("🎯 Sistema de Gestión de Turnos - Frontend")
    print("=" * 50)
    
    # Verificar Node.js
    if not check_node():
        print("❌ Node.js no está disponible. Instala Node.js 16+ y vuelve a intentar.")
        print("   Descarga desde: https://nodejs.org/")
        return
    
    # Verificar npm
    if not check_npm():
        print("❌ npm no está disponible. Verifica la instalación de Node.js.")
        return
    
    # Verificar estructura del proyecto
    if not Path("frontend").exists():
        print("❌ Directorio 'frontend' no encontrado. Ejecuta este script desde la raíz del proyecto.")
        return
    
    try:
        # Instalar dependencias
        if not install_dependencies():
            print("❌ No se pudieron instalar las dependencias")
            return
        
        print("\n🎉 ¡Configuración del frontend completada exitosamente!")
        print("\n📋 Información:")
        print("   1. El frontend se iniciará automáticamente")
        print("   2. Estará disponible en: http://localhost:5173")
        print("   3. Asegúrate de que el backend esté ejecutándose en: http://localhost:8000")
        print("\n🔑 Credenciales de acceso:")
        print("   Admin: admin@barberia.com / admin123")
        print("   Cliente: juan@email.com / cliente123")
        
        # Iniciar frontend
        start_frontend()
        
    except KeyboardInterrupt:
        print("\n\n👋 Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()
