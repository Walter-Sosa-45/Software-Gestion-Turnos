# Imagen base
FROM python:3.12-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Crear directorio de la app
WORKDIR /app

# Copiar solo requirements primero (para cachear)
COPY requirements.txt .

# Actualizar pip e instalar dependencias
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar todo el código
COPY . .

# Puerto expuesto (Render lo puede sobrescribir)
EXPOSE 8000

# Comando para arrancar la app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
