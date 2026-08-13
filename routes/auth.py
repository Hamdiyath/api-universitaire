# ============================================================
# routes/auth.py - Routes d'authentification (Épurées)
# ============================================================

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.user import UserLogin, UserActivate, UserActivationInfo
from schemas.response import ApiResponse
from controllers.auth import AuthController

router = APIRouter(
    prefix="/auth",
    tags=["Authentification"]
)


# ---------- Connexion ----------
@router.post("/login", response_model=ApiResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Connexion d'un utilisateur.
    """
    controller = AuthController(db)
    result = controller.login(user_data)

    return {"message": "Connexion réussie","data": result}


# ---------- Vérification du token d'activation ----------
@router.get("/activate/{token}", response_model=ApiResponse[UserActivationInfo])
def verify_activation_token(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Vérifie si le token d'activation est valide.
    Filtrage automatique des champs via UserActivationInfo.
    """
    controller = AuthController(db)
    result = controller.verify_activation_token(token)

    return { "message": "Token valide. Veuillez définir votre mot de passe.","data": result }


# ---------- Activation du compte (définition du mot de passe) ----------
@router.post("/activate/{token}", response_model=ApiResponse[UserActivationInfo])
def activate_user(token: str,password_data: UserActivate,db: Session = Depends(get_db)):
    """
    Active le compte en définissant le mot de passe.
    """
    controller = AuthController(db)
    result = controller.activate_user(token, password_data)

    return { "message": "Compte activé avec succès. Vous pouvez maintenant vous connecter.","data": result}
