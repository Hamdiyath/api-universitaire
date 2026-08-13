

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from schemas.user import (
    UserCreate,
    UserRead,
    UserReadAdmin,
    UserUpdate,
    UserUpdateSelf,
    UserChangePassword
)
from schemas.response import ApiResponse
from controllers.user import UserController
from core.dependencies import get_current_user, require_role, can_view_user_profile

router = APIRouter(prefix="/users", tags=["Utilisateurs"])



@router.post("/",response_model=ApiResponse[UserReadAdmin])
def create_user_account(user: UserCreate,db: Session = Depends(get_db),_: User = Depends(require_role(["admin", "scolarite"]))):
    """Créer un utilisateur. Réservé à l'admin et à la scolarité."""
    controller = UserController(db)
    result = controller.create_user_account(user)
    return {"message": "Compte utilisateur créé avec succès", "data": result}



@router.get("/me", response_model=ApiResponse[UserRead])
def get_self_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Voir son propre profil. Accessible à tout utilisateur connecté."""
    controller = UserController(db)
    result = controller.get_self_profile(current_user.id)
    return {"message": "Profil récupéré avec succès", "data": result}


@router.get("/{user_id}", response_model=ApiResponse[UserRead])
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(can_view_user_profile)
):
    """
    Voir un utilisateur par son ID.
    Règle : soi-même, admin ou scolarité.
    """
    controller = UserController(db)
    result = controller.get_user_by_id(user_id)
    return {"message": "Utilisateur récupéré avec succès", "data": result}


@router.get("/", response_model=ApiResponse[List[UserRead]])
def get_all_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    _: User = Depends(require_role(["admin", "scolarite"]))
):
    """Lister tous les utilisateurs. Réservé à l'admin et à la scolarité."""
    controller = UserController(db)
    result = controller.get_all_users(skip, limit)
    return {"message": "Liste des utilisateurs récupérée", "data": result}



@router.put("/{user_id}", response_model=ApiResponse[UserRead])
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(["admin", "scolarite"]))
):
    """Modifier un utilisateur. Réservé à l'admin et à la scolarité."""
    controller = UserController(db)
    result = controller.update_user(user_id, user)
    return {"message": "Utilisateur modifié avec succès", "data": result}


@router.put("/me", response_model=ApiResponse[UserRead])
def update_self_profile(
    user: UserUpdateSelf,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Modifier son propre profil. Accessible à tout utilisateur connecté."""
    controller = UserController(db)
    result = controller.update_user_self(current_user.id, user)
    return {"message": "Profil mis à jour avec succès", "data": result}


@router.put("/me/password", response_model=ApiResponse[UserRead])
def update_password(
    password_data: UserChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Modifier son mot de passe. Accessible à tout utilisateur connecté."""
    controller = UserController(db)
    result = controller.update_password(current_user.id, password_data)
    return {"message": "Mot de passe mis à jour avec succès", "data": result}


@router.delete("/{user_id}", response_model=ApiResponse)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(["admin"]))
):
    """Supprimer un utilisateur. Réservé à l'admin."""
    controller = UserController(db)
    controller.delete_user(user_id)
    return {"message": "Utilisateur supprimé avec succès", "data": None}



@router.post("/{user_id}/renvoyer-activation", response_model=ApiResponse)
def renvoyer_token_activation(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(["admin", "scolarite"]))
):
    """Renvoyer un token d'activation. Réservé à l'admin et à la scolarité."""
    controller = UserController(db)
    result = controller.renvoyer_token_activation(user_id)
    return {"message": "Nouveau token d'activation généré", "data": result}