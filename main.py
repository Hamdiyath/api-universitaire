# ============================================================
# main.py - Point d'entrée de l'API FastAPI
# ============================================================

from contextlib import asynccontextmanager
from fastapi import FastAPI
from routes import enseignement as enseignements_router
from scripts.seed_admin import seed_admin
from routes.user import router as user_router
from routes import auth as auth_router
from routes import matiere as matiere_router
from routes import role as role_router
from routes import filiere as filieres_router
from routes import note as notes_router          # ← AJOUTER
from routes import bulletin as bulletins_router  # ← AJOUTER
from core.handlers import setup_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("✅ API Universitaire démarrée")
    seed_admin()
    yield
    print("👋 API Universitaire arrêtée")


app = FastAPI(
    title="API Universitaire",
    description="API de gestion de la scolarité",
    version="1.0.0",
    lifespan=lifespan,
)

setup_exception_handlers(app)

# Inclusion des routeurs
app.include_router(auth_router.router)
app.include_router(filieres_router.router)
app.include_router(matiere_router.router)
app.include_router(role_router.router)
app.include_router(user_router)
app.include_router(notes_router.router)          # ← AJOUTER
app.include_router(bulletins_router.router)      # ← AJOUTER
app.include_router(enseignements_router.router)

@app.get("/")
def root():
    return {
        "success": True,
        "message": "Bienvenue sur l'API Universitaire",
        "data": None,
    }