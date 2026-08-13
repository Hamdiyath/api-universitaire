# ============================================================
# routes/role.py - Routes pour la gestion des rôles (Épurées)
# ============================================================

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas.role import RoleCreate, RoleUpdate, RoleRead
from schemas.response import ApiResponse
from controllers.role import RoleController
from core.dependencies import require_role  # <-- Import de votre bouclier

# 🔒 TOUTES les routes de ce fichier exigeront d'être Admin !
router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
    dependencies=[Depends(require_role(["admin"]))]
)


# ---------- Créer un rôle ----------
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[RoleRead]
)
def create_new_role(
        role_data: RoleCreate,
        db: Session = Depends(get_db)
):
    """Créer un nouveau rôle (Réservé à l'Admin)."""
    controller = RoleController(db)
    result = controller.create_role(role_data)

    return {
        "message": "Rôle créé avec succès",
        "data": result
    }


# ---------- Lister tous les rôles ----------
@router.get(
    "/",
    response_model=ApiResponse[List[RoleRead]]
)
def get_all_roles(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """Récupérer tous les rôles (paginé) (Réservé à l'Admin)."""
    # Note: On passe par le contrôleur pour l'accès aux données globales
    controller = RoleController(db)
    result = controller.role_service.role_crud.get_all(db, skip, limit)

    return {
        "message": "Rôles récupérés avec succès",
        "data": result
    }


# ---------- Récupérer un rôle par ID ----------
@router.get(
    "/{role_id}",
    response_model=ApiResponse[RoleRead]
)
def get_role_by_id_route(
        role_id: int,
        db: Session = Depends(get_db)
):
    """Récupérer un rôle par son ID (Réservé à l'Admin)."""
    controller = RoleController(db)
    result = controller.get_role_by_id(role_id)

    return {
        "message": "Rôle récupéré avec succès",
        "data": result
    }


# ---------- Modifier un rôle ----------
@router.put(
    "/{role_id}",
    response_model=ApiResponse[RoleRead]
)
def update_existing_role(
        role_id: int,
        role_data: RoleUpdate,
        db: Session = Depends(get_db)
):
    """Modifier un rôle existant (Réservé à l'Admin)."""
    controller = RoleController(db)
    result = controller.update_role(role_id, role_data)

    return {
        "message": "Rôle mis à jour avec succès",
        "data": result
    }


# ---------- Supprimer un rôle ----------
@router.delete(
    "/{role_id}",
    response_model=ApiResponse[None]
)
def delete_existing_role(
        role_id: int,
        db: Session = Depends(get_db)
):
    """Supprimer un rôle (Réservé à l'Admin)."""
    controller = RoleController(db)
    controller.delete_role(role_id)

    return {
        "message": "Rôle supprimé avec succès",
        "data": None
    }
