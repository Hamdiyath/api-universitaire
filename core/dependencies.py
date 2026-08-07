# ============================================================
# core/dependencies.py - Récupération de l'utilisateur courant
# ============================================================

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Optional
from core.security import SECRET_KEY, ALGORITHM
from database import SessionLocal
from models.user import User

# Configuration du schéma OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Récupère l'utilisateur actuel à partir du token JWT.
    Vérifie que le compte existe, est actif et activé.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. Décodage du token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 2. Extraction du user_id
        user_id_str: Optional[str] = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)

        # 3. Récupération de l'email (optionnel)
        email: Optional[str] = payload.get("email")
        if email is None:
            raise credentials_exception

    except (JWTError, ValueError):
        raise credentials_exception

    # 4. Recherche de l'utilisateur en base
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise credentials_exception

        # Vérification du statut
        if user.statut != "actif":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Compte inactif ou suspendu"
            )

        # Vérification que le compte est activé
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Compte non activé. Veuillez vérifier vos emails."
            )

        # Chargement des rôles avant fermeture de la session
        _ = user.roles

        return user
    finally:
        db.close()


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Vérifie que l'utilisateur est actif.
    (Fonction de sécurité supplémentaire pour les routes sensibles)
    """
    if current_user.statut != "actif":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte inactif ou suspendu"
        )
    return current_user


def require_role(required_roles: list[str]):
    """
    Dépendance pour vérifier si l'utilisateur connecté possède un rôle spécifique.

    Args:
        required_roles (list[str]): Liste des rôles autorisés

    Returns:
        Callable: Dépendance FastAPI

    Utilisation:
        current_user: User = Depends(require_role(["admin", "scolarite"]))
    """

    def role_checker(current_user: User = Depends(get_current_user)):
        user_roles = [role.name for role in current_user.roles]
        for role in required_roles:
            if role in user_roles:
                return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Accès refusé. Rôles requis: {required_roles}"
        )

    return role_checker