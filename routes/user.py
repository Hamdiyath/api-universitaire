# ============================================================
# routes/users.py - Routes pour la gestion des utilisateurs
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from schemas.user import (
    UserRead,
    UserReadAdmin,
    UserUpdate,
    UserUpdateSelf,
    UserCreate,
    UserChangePassword

)
from services.user_service import (
    create_user_account,
    get_all_users,
    get_user_by_id,
    update_user,
    delete_user,
    update_user_self,
    update_password
)
from core.dependencies import get_current_user, require_role
from core.handlers import handle_request
from schemas.response import ApiResponse

router = APIRouter(prefix="/users", tags=["Utilisateurs"])


# ============================================
# ROUTES FIXES (sans paramètre variable)
# ============================================

# ---------- 1. Récupérer son propre profil ----------
# Permission : Tout utilisateur connecté
@router.get("/me", response_model=ApiResponse[UserRead])
def get_self_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère le profil de l'utilisateur connecté.
    - Sans token d'activation (UserRead)
    """
    user = get_user_by_id(db, current_user.id)
    return ApiResponse(
        success=True,
        message="Profil récupéré",
        data=user
    )


# ---------- 2. Modifier son propre profil ----------
# Permission : Tout utilisateur connecté (champs restreints)
@router.put("/me", response_model=ApiResponse[UserRead])
def update_self(
    user_data: UserUpdateSelf,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Modifie le profil de l'utilisateur connecté.
    - Seuls téléphone, adresse et photo sont modifiables
    """
    return handle_request(update_user_self, "Profil mis à jour", db, current_user.id, user_data)


# ============================================
# ROUTES AVEC PARAMÈTRE VARIABLE
# ============================================

# ---------- 3. Récupérer un utilisateur par ID ----------
# Permission : Admin, Scolarité, ou soi-même
@router.get("/{user_id}", response_model=ApiResponse)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère un utilisateur par son ID.
    - Admin et Scolarité : voient le token (UserReadAdmin)
    - Autres : ne voient pas le token (UserRead)
    """
    user_roles = [role.name for role in current_user.roles]

    if current_user.id != user_id and "admin" not in user_roles and "scolarite" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas l'autorisation de voir ce profil"
        )

    user_data = get_user_by_id(db, user_id)

    # Si l'utilisateur est admin ou scolarité, retourner avec token
    if "admin" in user_roles or "scolarite" in user_roles:
        return ApiResponse(
            success=True,
            message="Utilisateur récupéré",
            data=UserReadAdmin.model_validate(user_data)
        )
    else:
        # Sinon, retourner sans token
        return ApiResponse(
            success=True,
            message="Utilisateur récupéré",
            data=UserRead.model_validate(user_data)
        )


# ---------- 4. Modifier un utilisateur (Admin/Scolarité) ----------
# Permission : Admin, Scolarité
@router.put("/{user_id}", response_model=ApiResponse[UserRead])
def update_existing_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Modifie un utilisateur existant.
    - Réservé à l'Admin et à la Scolarité
    """
    user_roles = [role.name for role in current_user.roles]
    if "admin" not in user_roles and "scolarite" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul l'administrateur ou la scolarité peut modifier les comptes"
        )
    return handle_request(update_user, "Utilisateur modifié avec succès", db, user_id, user_data)


# ---------- 5. Supprimer un utilisateur ----------
# Permission : Admin uniquement
@router.delete("/{user_id}", response_model=ApiResponse[None])
def delete_existing_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Supprime un utilisateur.
    - Réservé à l'Admin uniquement
    """
    return handle_request(delete_user, "Utilisateur supprimé avec succès", db, user_id)


# ============================================
# ROUTES GÉNÉRALES
# ============================================

# ---------- 6. Lister tous les utilisateurs ----------
# Permission : Admin, Scolarité
@router.get("/", response_model=ApiResponse[List[UserReadAdmin]])
def read_all_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    """
    Liste tous les utilisateurs (paginé).
    - Réservé à l'Admin et à la Scolarité
    - Retourne les tokens d'activation (UserReadAdmin)
    """
    return handle_request(get_all_users, "Liste des utilisateurs récupérée", db, skip, limit)


# ---------- 7. Créer un utilisateur ----------
# Permission : Admin, Scolarité
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[UserReadAdmin])
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    """
    Crée un nouveau compte utilisateur.
    - Réservé à l'Admin et à la Scolarité
    - Retourne le token d'activation (UserReadAdmin)
    """
    return handle_request(create_user_account, "Compte créé avec succès", db, user_data)


# ---------- Modifier son mot de passe ----------
# Permission : Utilisateur connecté (soi-même)
@router.put("/me/password", response_model=ApiResponse[UserRead])
def update_self_password(
    password_data: UserChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return handle_request(
        update_password,
        "Mot de passe mis à jour avec succès",
        db,
        current_user.id,
        password_data
    )