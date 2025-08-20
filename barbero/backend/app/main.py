from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import routes

app = FastAPI(
    title="Sistema de Gestión de Turnos",
    description="API para gestionar turnos de barberos",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas
app.include_router(routes.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Sistema de Gestión de Turnos API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
