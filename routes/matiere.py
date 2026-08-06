
# routes/matiere.py - Routes pour les matières

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas.matiere import MatiereCreate, MatiereUpdate, MatiereRead
from services.matiere_service import create_matiere, update_matiere, delete_matiere, get_matiere_by_id
from crud.matiere import get_all
from core.handlers import handle_request
from schemas.response import ApiResponse


# ---------- Configuration du routeur ----------
router = APIRouter(
    prefix="/matieres",
    tags=["Matieres"]
)


# ---------- Créer une matière ----------
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[MatiereRead]
)
def create_new_matiere(
    matiere_data: MatiereCreate,
    db: Session = Depends(get_db)
):
    """Créer une nouvelle matière."""
    return handle_request(create_matiere, "Matière créée avec succès", db, matiere_data)


# ---------- Lister toutes les matières ----------
@router.get(
    "/",
    response_model=ApiResponse[List[MatiereRead]]
)
def get_all_matieres(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Récupérer toutes les matières (paginé)."""
    return handle_request(get_all, "Matières récupérées avec succès", db, skip, limit)


# ---------- Récupérer une matière par ID ----------
@router.get(
    "/{matiere_id}",
    response_model=ApiResponse[MatiereRead]
)
def get_matiere_by_id_route(
    matiere_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer une matière par son ID."""
    return handle_request(get_matiere_by_id, "Matière récupérée avec succès", db, matiere_id)


# ---------- Modifier une matière ----------
@router.put(
    "/{matiere_id}",
    response_model=ApiResponse[MatiereRead]
)
def update_existing_matiere(
    matiere_id: int,
    matiere_data: MatiereUpdate,
    db: Session = Depends(get_db)
):
    """Modifier une matière existante."""
    return handle_request(update_matiere, "Matière mise à jour avec succès", db, matiere_id, matiere_data)


# ---------- Supprimer une matière ----------
@router.delete(
    "/{matiere_id}",
    response_model=ApiResponse[None]
)
def delete_existing_matiere(
    matiere_id: int,
    db: Session = Depends(get_db)
):
    """Supprimer une matière."""
    return handle_request(delete_matiere, "Matière supprimée avec succès", db, matiere_id)