
# routes/auth.py - Routes d'authentification


from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.user import UserLogin, UserActivate
from services.auth_service import authenticate_user, activate_user_account
from core.security import create_access_token
from core.handlers import handle_request
from schemas.response import ApiResponse

router = APIRouter(
    prefix="/auth",
    tags=["Authentification"]
)


# ---------- Connexion ----------
@router.post("/login", response_model=ApiResponse)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Connexion d'un utilisateur.
    """
    user = authenticate_user(db, user_data.email, user_data.password)

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    return {
        "success": True,
        "message": "Connexion réussie",
        "data": {
            "access_token": access_token,
            "token_type": "bearer"
        }
    }


# ---------- Vérification du token d'activation ----------
@router.get("/activate/{token}", response_model=ApiResponse)
def verify_activation_token(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Vérifie si le token d'activation est valide.
    """
    from crud.user import get_by_activation_token
    from datetime import datetime

    user = get_by_activation_token(db, token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token d'activation invalide"
        )

    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce compte est déjà activé"
        )

    if user.activation_token_expires and user.activation_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le token d'activation a expiré"
        )

    return {
        "success": True,
        "message": "Token valide. Veuillez définir votre mot de passe.",
        "data": {
            "email": user.email,
            "nom": user.nom,
            "prenom": user.prenom
        }
    }


# ---------- Activation du compte (définition du mot de passe) ----------
@router.post("/activate/{token}", response_model=ApiResponse)
def activate_user(
    token: str,
    password_data: UserActivate,
    db: Session = Depends(get_db)
):
    """
    Active le compte en définissant le mot de passe.
    """
    user = activate_user_account(db, token, password_data)

    return {
        "success": True,
        "message": "Compte activé avec succès. Vous pouvez maintenant vous connecter.",
        "data": {
            "email": user.email,
            "nom": user.nom,
            "prenom": user.prenom
        }
    }