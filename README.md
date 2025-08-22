# Sistema de Gestión de Turnos - Barbería

Sistema web para gestionar turnos de una barbería, desarrollado con FastAPI (backend) y React (frontend).

## 🚀 Características

- **Gestión de turnos** con validación de horarios
- **Autenticación JWT** para usuarios
- **Roles**: Admin (barbero) y Cliente
- **Base de datos SQLite** para desarrollo
- **API REST** documentada con Swagger
- **Frontend React** responsive

## 🛠️ Tecnologías

### Backend
- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para Python
- **SQLite** - Base de datos ligera
- **JWT** - Autenticación segura
- **Pydantic** - Validación de datos

### Frontend
- **React** - Biblioteca de interfaz de usuario
- **Vite** - Herramienta de construcción
- **CSS** - Estilos personalizados

## 📁 Estructura del Proyecto

```
barbero/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── core/           # Configuración
│   │   ├── crud/           # Operaciones de base de datos
│   │   ├── models/         # Modelos SQLAlchemy
│   │   ├── routes/         # Endpoints de la API
│   │   └── schemas/        # Esquemas Pydantic
│   ├── init_db.py          # Script de inicialización
│   ├── main.py             # Punto de entrada
│   └── requirements.txt    # Dependencias Python
└── frontend/               # Aplicación React
    ├── src/
    │   ├── components/     # Componentes React
    │   ├── context/        # Contexto de autenticación
    │   └── services/       # Servicios de API
    └── package.json        # Dependencias Node.js
```

## 🚀 Instalación y Configuración

### 1. Backend

```bash
cd barbero/backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Inicializar base de datos
python init_db.py

# Ejecutar servidor
python -m app.main
```

El backend estará disponible en: http://localhost:8000
Documentación API: http://localhost:8000/docs

### 2. Frontend

```bash
cd barbero/frontend

# Instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm run dev
```

El frontend estará disponible en: http://localhost:5173

## 🔑 Credenciales de Acceso

### Usuario Admin (Barbero)
- **Email**: admin@barberia.com
- **Contraseña**: admin123

### Clientes de Ejemplo
- **Email**: juan@email.com
- **Contraseña**: cliente123

## 📊 Base de Datos

- **Tipo**: SQLite
- **Archivo**: `turnos.db` (se crea automáticamente)
- **Tablas**:
  - `usuarios` - Usuarios del sistema
  - `servicios` - Servicios ofrecidos
  - `turnos` - Turnos reservados

## 🔧 Scripts Útiles

### Inicializar Base de Datos
```bash
python init_db.py
```

### Ejecutar Backend
```bash
python -m app.main
```

### Ejecutar Frontend
```bash
npm run dev
```

## 📱 Endpoints Principales

- `POST /api/v1/auth/login` - Iniciar sesión
- `GET /api/v1/turnos/` - Listar turnos
- `POST /api/v1/turnos/` - Crear turno
- `PUT /api/v1/turnos/{id}` - Actualizar turno
- `DELETE /api/v1/turnos/{id}` - Eliminar turno

## 🎯 Funcionalidades

### Para el Barbero (Admin)
- Ver todos los turnos
- Confirmar/cancelar turnos
- Gestionar servicios
- Ver estadísticas

### Para el Cliente
- Reservar turnos
- Ver sus turnos
- Cancelar turnos
- Seleccionar servicios

## 🚨 Notas Importantes

- **Desarrollo**: Este proyecto está configurado para desarrollo con SQLite
- **Producción**: Cambiar configuración de base de datos y secretos
- **Seguridad**: Cambiar SECRET_KEY en producción
- **Base de datos**: Se crea automáticamente al ejecutar `init_db.py`

## 🔍 Solución de Problemas

### Error de conexión a la base de datos
- Verificar que `init_db.py` se haya ejecutado
- Verificar permisos de escritura en el directorio

### Error de dependencias
- Verificar que el entorno virtual esté activado
- Ejecutar `pip install -r requirements.txt`

### Error del frontend
- Verificar que el backend esté ejecutándose
- Verificar la URL en `src/services/config.js`

## 📝 Licencia

Este proyecto es para uso educativo y de desarrollo.
