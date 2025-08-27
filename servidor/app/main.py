from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import routes
from app.core.config import tenant_engine, TenantBase
import os

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

@app.on_event("startup")
def ensure_tables():
    try:
        TenantBase.metadata.create_all(bind=tenant_engine)
    except Exception:
        # En caso de error, dejamos que el servidor siga y se vea en logs
        pass

@app.get("/")
async def root():
    return {"message": "Sistema de Gestión de Turnos API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(os.environ.get("PORT",8000))
