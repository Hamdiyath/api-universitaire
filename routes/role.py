
# routes/role.py - Routes pour les rôles


from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas.role import RoleCreate, RoleUpdate, RoleRead
from services.role_service import create_role, update_role, delete_role, get_role_by_id
from crud.role import get_all
from core.handlers import handle_request
from schemas.response import ApiResponse


# ---------- Configuration du routeur ----------
router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
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
    """Créer un nouveau rôle."""
    return handle_request(create_role, "Rôle créé avec succès", db, role_data)


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
    """Récupérer tous les rôles (paginé)."""
    return handle_request(get_all, "Rôles récupérés avec succès", db, skip, limit)


# ---------- Récupérer un rôle par ID ----------
@router.get(
    "/{role_id}",
    response_model=ApiResponse[RoleRead]
)
def get_role_by_id_route(
    role_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer un rôle par son ID."""
    return handle_request(get_role_by_id, "Rôle récupéré avec succès", db, role_id)


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
    """Modifier un rôle existant."""
    return handle_request(update_role, "Rôle mis à jour avec succès", db, role_id, role_data)


# ---------- Supprimer un rôle ----------
@router.delete(
    "/{role_id}",
    response_model=ApiResponse[None]
)
def delete_existing_role(
    role_id: int,
    db: Session = Depends(get_db)
):
    """Supprimer un rôle."""
    return handle_request(delete_role, "Rôle supprimé avec succès", db, role_id)