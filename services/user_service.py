# ============================================================
# services/user_service.py - Logique métier pour la gestion des utilisateurs (hors auth)
# ============================================================

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
import secrets
from datetime import datetime, timedelta

from crud.user import get_all, get_by_id, update, delete, get_by_email, create
from crud.role import get_by_name
from schemas.user import UserUpdate, UserRead, UserUpdateSelf, UserCreate, UserReadAdmin


# ---------- Créer un utilisateur (Admin/Scolarité) ----------
def create_user_account(db: Session, user_data: UserCreate):
    """
    Crée un compte utilisateur (Admin/Scolarité).
    - Vérifie que l'email n'existe pas déjà
    - Vérifie que le rôle existe
    - Vérifie que filiere_id est fourni pour les étudiants
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
    role_obj = get_by_name(db, user_data.role_name)
    if not role_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Le rôle '{user_data.role_name}' n'existe pas"
        )

    # 3. Vérifier que filiere_id est fourni pour les étudiants
    if user_data.role_name == "etudiant" and user_data.filiere_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le champ filiere_id est obligatoire pour un étudiant"
        )

    # 4. Générer le token d'activation
    activation_token = secrets.token_urlsafe(32)
    activation_token_expires = datetime.utcnow() + timedelta(hours=24)

    # 5. Préparer les données
    user_dict = user_data.model_dump()
    user_dict.pop("role_name")
    user_dict["password_hash"] = None
    user_dict["is_active"] = False
    user_dict["activation_token"] = activation_token
    user_dict["activation_token_expires"] = activation_token_expires

    # 6. Créer l'utilisateur
    new_user = create(db, user_dict)

    # 7. Associer le rôle
    new_user.roles.append(role_obj)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 8. Retourner un schéma Pydantic (pas un objet SQLAlchemy)
    return UserReadAdmin.model_validate(new_user)


# ---------- Récupérer tous les utilisateurs ----------
def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[UserRead]:
    users = get_all(db, skip, limit)
    return [UserRead.model_validate(user) for user in users]


# ---------- Récupérer un utilisateur par son ID ----------
def get_user_by_id(db: Session, user_id: int) -> dict:
    user = get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    return UserRead.model_validate(user).model_dump()


# ---------- Mettre à jour un utilisateur (Admin/Scolarité) ----------
def update_user(db: Session, user_id: int, user_data: UserUpdate) -> UserRead:
    user = get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )

    update_data = user_data.model_dump(exclude_unset=True)

    if "email" in update_data:
        existing = get_by_email(db, update_data["email"])
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cet email est déjà utilisé par un autre compte"
            )

    updated_user = update(db, user_id, update_data)
    return UserRead.model_validate(updated_user)


# ---------- Mettre à jour son propre profil (Utilisateur connecté) ----------
def update_user_self(db: Session, user_id: int, user_data: UserUpdateSelf) -> UserRead:
    user = get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )

    update_data = user_data.model_dump(exclude_unset=True)
    updated_user = update(db, user_id, update_data)
    return UserRead.model_validate(updated_user)


# ---------- Supprimer un utilisateur ----------
def delete_user(db: Session, user_id: int):
    user = get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    delete(db, user_id)
    return None