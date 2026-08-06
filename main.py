# ============================================================
# main.py - Point d'entrée de l'API FastAPI
# ============================================================

from contextlib import asynccontextmanager
from fastapi import FastAPI

from routes import auth as auth_router
from routes import matiere as matiere_router
from routes import filiere as filieres_router  # ← Ajouté
from core.handlers import setup_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("✅ API Universitaire démarrée")
    yield
    print("👋 API Universitaire arrêtée")


app = FastAPI(
    title="API Universitaire",
    description="API de gestion de la scolarité",
    version="1.0.0",
    lifespan=lifespan,
)

# Configuration des handlers d'erreurs
setup_exception_handlers(app)

# Inclusion des routeurs
app.include_router(auth_router.router)
app.include_router(filieres_router.router)
app.include_router(matiere_router.router)


@app.get("/")
def root():
    return {
        "success": True,
        "message": "Bienvenue sur l'API Universitaire",
        "data": None,
    }