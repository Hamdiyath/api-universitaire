from contextlib import asynccontextmanager
from fastapi import FastAPI
from routes import enseignement as enseignements_router
from scripts.seed_admin import seed_admin
from routes.user import router as user_router
from routes import auth as auth_router
from routes import matiere as matiere_router
from routes import role as role_router
from routes import filiere as filieres_router
from routes import note as notes_router
from routes import bulletin as bulletins_router
from core.handlers import setup_exception_handlers
from routes import matiere_filiere as matieres_filieres_router
from routes import inscription as inscriptions_router
from routes import  resultat_matiere as resultat_matieres_router
from routes import decision_annuelle as decisions_annuelles_router


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
app.include_router(notes_router.router)
app.include_router(bulletins_router.router)       # ← une seule fois
app.include_router(enseignements_router.router)
app.include_router(matieres_filieres_router.router)
app.include_router(inscriptions_router.router)

app.include_router(resultat_matieres_router.router)
app.include_router(decisions_annuelles_router.router)



@app.get("/")
def root():
    return {
        "success": True,
        "message": "Bienvenue sur l'API Universitaire",
        "data": None,
    }