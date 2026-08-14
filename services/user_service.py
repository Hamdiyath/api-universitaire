# ============================================================
# services/user_service.py - Logique métier pour User
# ============================================================

import secrets
from datetime import datetime, timezone, timedelta
from typing import List

from sqlalchemy.orm import Session

from crud import user as user_crud
from crud import role as role_crud

from schemas.user import (
    UserCreate,
    UserRead,
    UserReadAdmin,
    UserUpdate,
    UserUpdateSelf,
    UserChangePassword
)

from exceptions.base import (
    UserNotFoundError,
    EmailAlreadyExistsError,
    RoleNotFoundError,
    FiliereRequiredError,
    AccountAlreadyActiveError,
    InvalidPasswordError,
    MatriculeAlreadyExistsError

)

from core.security import hash_password, verify_password


class UserService:
    """Service de gestion des utilisateurs. Contient toute la logique métier."""

    def __init__(self, db: Session):
        self.db = db


    # ---------- Création ----------
    def create_user_account(self, user_data: UserCreate) -> UserReadAdmin:
        """Crée un nouvel utilisateur."""
        # Vérifier si l'email existe déjà
        if user_crud.get_by_email(self.db, user_data.email):
            raise EmailAlreadyExistsError(user_data.email)

        if user_data.matricule:
            if user_crud.get_by_matricule(self.db, user_data.matricule):
                raise MatriculeAlreadyExistsError(user_data.matricule)  #

        # Vérifier que le rôle existe
        role_obj = role_crud.get_by_name(self.db, user_data.role_name)
        if not role_obj:
            raise RoleNotFoundError(user_data.role_name)

        # Vérifier qu'un étudiant a une filière
        if user_data.role_name == "etudiant" and user_data.filiere_id is None:
            raise FiliereRequiredError()

        # Générer le token d'activation
        activation_token = secrets.token_urlsafe(32)
        activation_token_expires = datetime.now(timezone.utc) + timedelta(hours=24)

        # Préparer les données
        user_dict = user_data.model_dump()
        user_dict.pop("role_name")
        user_dict["password_hash"] = None
        user_dict["is_active"] = False
        user_dict["activation_token"] = activation_token
        user_dict["activation_token_expires"] = activation_token_expires

        # Créer l'utilisateur
        new_user = user_crud.create(self.db, user_dict)

        # Associer le rôle
        new_user.roles.append(role_obj)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        return UserReadAdmin.model_validate(new_user)


    # ---------- Lecture ----------
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserRead]:
        """Récupère tous les utilisateurs."""
        users = user_crud.get_all(self.db, skip, limit)
        return [UserRead.model_validate(user) for user in users]

    def get_user_by_id(self, user_id: int) -> UserRead:
        """Récupère un utilisateur par son ID."""
        user = user_crud.get_by_id(self.db, user_id)
        if not user:
            raise UserNotFoundError(user_id)
        return UserRead.model_validate(user)


    # ---------- Mise à jour ----------
    def update_user(self, user_id: int, user_data: UserUpdate) -> UserRead:
        """Met à jour un utilisateur (Admin/Scolarité)."""
        user = user_crud.get_by_id(self.db, user_id)
        if not user:
            raise UserNotFoundError(user_id)

        update_data = user_data.model_dump(exclude_unset=True)

        # Vérifier l'email si modifié
        if "email" in update_data:
            existing = user_crud.get_by_email(self.db, update_data["email"])
            if existing and existing.id != user_id:
                raise EmailAlreadyExistsError(update_data["email"])

        updated_user = user_crud.update(self.db, user_id, update_data)
        return UserRead.model_validate(updated_user)

    def update_user_self(self, user_id: int, user_data: UserUpdateSelf) -> UserRead:
        """Met à jour son propre profil."""
        user = user_crud.get_by_id(self.db, user_id)
        if not user:
            raise UserNotFoundError(user_id)

        update_data = user_data.model_dump(exclude_unset=True)
        updated_user = user_crud.update(self.db, user_id, update_data)
        return UserRead.model_validate(updated_user)

    def update_password(self, user_id: int, password_data: UserChangePassword) -> UserRead:
        """Met à jour le mot de passe."""
        user = user_crud.get_by_id(self.db, user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # Vérifier l'ancien mot de passe
        if not verify_password(password_data.current_password, user.password_hash):
            raise InvalidPasswordError()

        # Hacher le nouveau mot de passe
        hashed_password = hash_password(password_data.new_password)
        updated_user = user_crud.update(self.db, user_id, {"password_hash": hashed_password})
        return UserRead.model_validate(updated_user)


    # ---------- Suppression ----------
    def delete_user(self, user_id: int) -> None:
        """Supprime un utilisateur."""
        user = user_crud.get_by_id(self.db, user_id)
        if not user:
            raise UserNotFoundError(user_id)
        user_crud.delete(self.db, user_id)


    # ---------- Activation ----------
    def renvoyer_token_activation(self, user_id: int) -> dict:
        """Génère un nouveau token d'activation."""
        user = user_crud.get_by_id(self.db, user_id)
        if not user:
            raise UserNotFoundError(user_id)

        if user.is_active:
            raise AccountAlreadyActiveError()

        new_token = secrets.token_urlsafe(32)
        new_expiry = datetime.now(timezone.utc) + timedelta(hours=24)

        user_crud.update(self.db, user_id, {
            "activation_token": new_token,
            "activation_token_expires": new_expiry
        })

        return {
            "user_id": user_id,
            "activation_token": new_token,
            "expires_at": new_expiry
        }


