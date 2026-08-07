# ============================================================
# services/auth_service.py - Logique métier pour l'authentification
# ============================================================

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import secrets
from datetime import datetime, timedelta

from crud.role import get_by_name
from crud.user import get_by_email, get_by_activation_token, create, update
from core.security import hash_password, verify_password
from schemas.user import UserCreate, UserActivate


# ---------- CONSERVÉ ----------
def authenticate_user(db: Session, email: str, password: str):
    """
    Logique de connexion d'un utilisateur.
    """
    user = get_by_email(db, email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte non activé. Veuillez vérifier vos emails."
        )

    return user


# ---------- NOUVEAU ----------
def generate_activation_token() -> str:
    """
    Génère un token d'activation sécurisé.
    """
    return secrets.token_urlsafe(32)


# ---------- NOUVEAU ----------
def create_user_account(db: Session, user_data: UserCreate, role_name: str):
    """
    Crée un compte utilisateur (Admin/Scolarité).
    - Vérifie que l'email n'existe pas déjà
    - Vérifie que le rôle existe
    - Génère un token d'activation
    - Crée l'utilisateur avec is_active=False
    - Associe le rôle
    """
    # 1. Vérifier si l'email existe déjà
    existing_user = get_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé"
        )

    # 2. Vérifier que le rôle existe
    role_obj = get_by_name(db, role_name)
    if not role_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Le rôle '{role_name}' n'existe pas dans le système"
        )

    # 3. Générer le token d'activation
    activation_token = generate_activation_token()
    activation_token_expires = datetime.utcnow() + timedelta(hours=24)

    # 4. Préparer les données
    user_dict = user_data.model_dump()
    user_dict["password_hash"] = None  # Pas de mot de passe initial
    user_dict["is_active"] = False
    user_dict["activation_token"] = activation_token
    user_dict["activation_token_expires"] = activation_token_expires

    # 5. Créer l'utilisateur
    new_user = create(db, user_dict)

    # 6. Associer le rôle
    new_user.roles.append(role_obj)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ---------- NOUVEAU ----------
def activate_user_account(db: Session, token: str, password_data: UserActivate):
    """
    Active un compte utilisateur.
    - Vérifie que le token est valide
    - Vérifie que le token n'a pas expiré
    - Hache le mot de passe
    - Active le compte (is_active=True)
    """
    # 1. Vérifier que les mots de passe correspondent
    if password_data.password != password_data.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Les mots de passe ne correspondent pas"
        )

    # 2. Récupérer l'utilisateur par le token
    user = get_by_activation_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token d'activation invalide"
        )

    # 3. Vérifier que le token n'a pas expiré
    if user.activation_token_expires and user.activation_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le token d'activation a expiré. Veuillez contacter la scolarité."
        )

    # 4. Vérifier que le compte n'est pas déjà activé
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce compte est déjà activé"
        )

    # 5. Hacher le mot de passe
    hashed_password = hash_password(password_data.password)

    # 6. Mettre à jour l'utilisateur
    update_data = {
        "password_hash": hashed_password,
        "is_active": True,
        "activation_token": None,
        "activation_token_expires": None
    }
    updated_user = update(db, user.id, update_data)

    return updated_user


# ---------- NOUVEAU (à implémenter plus tard) ----------
def send_activation_email(email: str, token: str, nom: str, prenom: str):
    """
    Envoie un email d'activation avec le lien.
    À implémenter avec SMTP ou une API de messagerie.
    """
    # TODO: Implémenter l'envoi d'email
    # Lien d'activation : https://universite.com/auth/activate/{token}
    print(f"📧 Email d'activation pour {nom} {prenom} ({email})")
    print(f"🔗 Lien : /auth/activate/{token}")
    # Pour la version finale, remplacer par un vrai envoi d'email


# ---------- SUPPRIMÉ ----------
# def register_user(): ...  # <-- SUPPRIMÉ