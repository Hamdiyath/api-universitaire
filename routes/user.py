# ============================================================
# routes/users.py - Routes pour la gestion des utilisateurs
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Union

from database import get_db
from models.user import User
from schemas.user import (
    UserRead,
    UserReadAdmin,
    UserUpdate,
    UserUpdateSelf,
    UserCreate
)
from services.user_service import (
    create_user_account,
    get_all_users,
    get_user_by_id,
    update_user,
    delete_user,
    update_user_self
)
from core.dependencies import get_current_user, require_role
from core.handlers import handle_request
from schemas.response import ApiResponse

router = APIRouter(prefix="/users", tags=["Utilisateurs"])


# ============================================
# ROUTES FIXES (sans paramètre variable)
# ============================================

# ---------- 1. Récupérer son propre profil ----------
@router.get("/me", response_model=ApiResponse[UserRead])
def get_self_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = get_user_by_id(db, current_user.id)
    return ApiResponse(
        success=True,
        message="Profil récupéré",
        data=user
    )


# ---------- 2. Modifier son propre profil ----------
@router.put("/me", response_model=ApiResponse[UserRead])
def update_self(
    user_data: UserUpdateSelf,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return handle_request(update_user_self, "Profil mis à jour", db, current_user.id, user_data)


# ============================================
# ROUTES AVEC PARAMÈTRE VARIABLE
# ============================================

# ---------- 3. Récupérer un utilisateur par ID ----------
@router.get("/{user_id}", response_model=ApiResponse)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_roles = [role.name for role in current_user.roles]

    if current_user.id != user_id and "admin" not in user_roles and "scolarite" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas l'autorisation de voir ce profil"
        )

    user_data = get_user_by_id(db, user_id)

    # Si l'utilisateur est admin, retourner avec token
    if "admin" in user_roles:
        return ApiResponse(
            success=True,
            message="Utilisateur récupéré",
            data=user_data
        )
    else:
        # Sinon, retourner sans token
        return ApiResponse(
            success=True,
            message="Utilisateur récupéré",
            data=UserRead.model_validate(user_data)
        )


# ---------- 4. Modifier un utilisateur (Admin/Scolarité) ----------
@router.put("/{user_id}", response_model=ApiResponse[UserRead])
def update_existing_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_roles = [role.name for role in current_user.roles]
    if "admin" not in user_roles and "scolarite" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul l'administrateur ou la scolarité peut modifier les comptes"
        )
    return handle_request(update_user, "Utilisateur modifié avec succès", db, user_id, user_data)


# ---------- 5. Supprimer un utilisateur ----------
@router.delete("/{user_id}", response_model=ApiResponse[None])
def delete_existing_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    return handle_request(delete_user, "Utilisateur supprimé avec succès", db, user_id)


# ============================================
# ROUTES GÉNÉRALES
# ============================================

# ---------- 6. Lister tous les utilisateurs ----------
@router.get("/", response_model=ApiResponse[List[UserRead]])
def read_all_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    return handle_request(get_all_users, "Liste des utilisateurs récupérée", db, skip, limit)


# ---------- 7. Créer un utilisateur ----------
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[UserReadAdmin])
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    return handle_request(create_user_account, "Compte créé avec succès", db, user_data)