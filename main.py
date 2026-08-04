# ============================================================
# main.py - Point d'entrée de l'API FastAPI
# ============================================================

from contextlib import asynccontextmanager
from fastapi import FastAPI


# ---------- Gestion du cycle de vie ----------
# Ici, on ne crée plus les tables automatiquement.
# Les migrations sont gérées via Alembic.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code exécuté au démarrage
    # On peut ajouter une vérification de connexion à la DB ici
    # (mais pas de création de tables)
    print("✅ API Universitaire démarrée")
    yield
    # Code exécuté à l'arrêt
    print("👋 API Universitaire arrêtée")


# ---------- Création de l'application ----------
app = FastAPI(
    title="API Universitaire",
    description="API de gestion de la scolarité",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------- Routes ----------
@app.get("/")
def root():
    return {"message": "API en ligne"}