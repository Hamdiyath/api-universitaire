# ============================================================
# routes/filieres.py - Routes pour les filières
# ============================================================

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas.filiere import FiliereCreate, FiliereUpdate, FiliereRead
from services.filiere_service import create_filiere, update_filiere, delete_filiere, get_filiere_by_id
from crud.filiere import get_all
from core.handlers import handle_request
from schemas.response import ApiResponse

# ---------- Configuration du routeur ----------
router = APIRouter(
    prefix="/filieres",
    tags=["Filieres"]
)


# ---------- Créer une filière ----------
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[FiliereRead]
)
def create_new_filiere(
    filiere_data: FiliereCreate,
    db: Session = Depends(get_db)
):
    """
    Créer une nouvelle filière.
    """
    return handle_request(create_filiere, "Filière créée avec succès", db, filiere_data)


# ---------- Lister toutes les filières ----------
@router.get(
    "/",
    response_model=ApiResponse[List[FiliereRead]]
)
def get_all_filieres(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Récupérer toutes les filières (paginé).
    """
    return handle_request(get_all, "Filières récupérées avec succès", db, skip, limit)


# ---------- Récupérer une filière par ID ----------
@router.get(
    "/{filiere_id}",
    response_model=ApiResponse[FiliereRead]
)
def get_filiere_by_id_route(
    filiere_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupérer une filière par son ID.
    """
    return handle_request(get_filiere_by_id, "Filière récupérée avec succès", db, filiere_id)


# ---------- Modifier une filière ----------
@router.put(
    "/{filiere_id}",
    response_model=ApiResponse[FiliereRead]
)
def update_existing_filiere(
    filiere_id: int,
    filiere_data: FiliereUpdate,
    db: Session = Depends(get_db)
):
    """
    Modifier une filière existante.
    """
    return handle_request(update_filiere, "Filière mise à jour avec succès", db, filiere_id, filiere_data)


# ---------- Supprimer une filière ----------
@router.delete(
    "/{filiere_id}",
    response_model=ApiResponse[None]
)
def delete_existing_filiere(
    filiere_id: int,
    db: Session = Depends(get_db)
):
    """
    Supprimer une filière.
    """
    return handle_request(delete_filiere, "Filière supprimée avec succès", db, filiere_id)