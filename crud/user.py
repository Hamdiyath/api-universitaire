# ============================================================
# crud/user.py - Opérations CRUD pour la table User
# ============================================================

from sqlalchemy.orm import Session
from models.user import User
from typing import Optional, List
import secrets
from datetime import datetime, timedelta


# ---------- Récupération par email ----------
def get_by_email(db: Session, email: str) -> Optional[User]:
    """
    Récupère un utilisateur par son email.
    """
    return db.query(User).filter(User.email == email).first()


# ---------- Récupération par ID ----------
def get_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Récupère un utilisateur par son ID.
    """
    return db.query(User).filter(User.id == user_id).first()


# ---------- Récupération par token d'activation ----------
def get_by_activation_token(db: Session, token: str) -> Optional[User]:
    """
    Récupère un utilisateur par son token d'activation.
    """
    return db.query(User).filter(User.activation_token == token).first()


# ---------- Récupération de tous les utilisateurs ----------
def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Récupère une liste paginée d'utilisateurs.
    """
    return db.query(User).offset(skip).limit(limit).all()


# ---------- Création d'un utilisateur ----------
def create(db: Session, user_data: dict) -> User:
    """
    Crée un nouvel utilisateur.
    - Génère un token d'activation
    - Définit is_active = False
    - Définit une date d'expiration pour le token (24h)
    """
    # Génération du token d'activation
    activation_token = secrets.token_urlsafe(32)
    activation_token_expires = datetime.utcnow() + timedelta(hours=24)

    # Préparation des données
    user_data["is_active"] = False
    user_data["activation_token"] = activation_token
    user_data["activation_token_expires"] = activation_token_expires

    # Création de l'utilisateur
    new_user = User(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# ---------- Mise à jour d'un utilisateur ----------
def update(db: Session, user_id: int, update_data: dict) -> Optional[User]:
    """
    Met à jour un utilisateur existant.
    """
    user = get_by_id(db, user_id)
    if not user:
        return None

    for key, value in update_data.items():
        if value is not None:
            setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


# ---------- Suppression d'un utilisateur ----------
def delete(db: Session, user_id: int) -> bool:
    """
    Supprime un utilisateur.
    """
    user = get_by_id(db, user_id)
    if not user:
        return False

    db.delete(user)
    db.commit()
    return True