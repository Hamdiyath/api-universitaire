# routes/auth.py - Routes d'authentification

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.user import UserCreate, UserRead, UserLogin
from services.user_service import register_user, authenticate_user
from core.security import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentification"]
)


# ---------- Endpoint d'inscription ----------
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
        user_data: UserCreate,
        db: Session = Depends(get_db)
):
    """
    Inscription d'un nouvel utilisateur.

    - Vérifie que l'email n'est pas déjà utilisé
    - Vérifie que les mots de passe correspondent
    - Crée l'utilisateur en base
    - Retourne l'utilisateur filtré (sans hash de mot de passe)
    """
    new_user = register_user(db, user_data)

    # On passe new_user dans UserRead pour filtrer le password_hash
    user_schema = UserRead.model_validate(new_user)

    return {
        "success": True,
        "message": "Utilisateur créé avec succès",
        "data": user_schema
    }


# ---------- Endpoint de connexion ----------
@router.post("/login")
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