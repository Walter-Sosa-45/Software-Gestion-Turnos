#!/usr/bin/env python3
"""
Script de prueba para verificar la autenticación del backend
"""
import requests
import json

# Configuración
BASE_URL = "http://192.168.0.102:8000"
API_URL = f"{BASE_URL}/api/v1"

def test_backend_connection():
    """Prueba la conexión básica al backend"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Backend conectado: {response.status_code}")
        print(f"   Respuesta: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Error conectando al backend: {e}")
        return False

def test_login_endpoint():
    """Prueba el endpoint de login"""
    try:
        # Datos de prueba
        login_data = {
            "usuario": "admin",
            "password": "admin123"
        }
        
        print(f"🔐 Probando login con: {login_data['usuario']}")
        
        response = requests.post(
            f"{API_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Login exitoso!")
            print(f"   Token: {data.get('access_token', 'No token')[:20]}...")
            print(f"   Usuario: {data.get('user', {}).get('nombre', 'No nombre')}")
            return data.get('access_token')
        else:
            print(f"   ❌ Login falló: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error probando login: {e}")
        return None

def test_protected_endpoint(token):
    """Prueba un endpoint protegido con el token"""
    if not token:
        print("❌ No hay token para probar endpoint protegido")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/usuarios/", headers=headers)
        
        print(f"🔒 Probando endpoint protegido: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Endpoint protegido accesible")
            return True
        else:
            print(f"   ❌ Endpoint protegido falló: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando endpoint protegido: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 Iniciando pruebas de autenticación...")
    print("=" * 50)
    
    # 1. Probar conexión al backend
    if not test_backend_connection():
        print("\n❌ No se puede conectar al backend. Verifica que esté ejecutándose.")
        return
    
    print()
    
    # 2. Probar endpoint de login
    token = test_login_endpoint()
    
    print()
    
    # 3. Probar endpoint protegido
    if token:
        test_protected_endpoint(token)
    
    print("\n" + "=" * 50)
    print("🏁 Pruebas completadas")

if __name__ == "__main__":
    main()
