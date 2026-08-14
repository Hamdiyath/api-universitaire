# routes/filieres.py - Routes pour les filières

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas.filiere import FiliereCreate, FiliereUpdate, FiliereRead
from controllers.filiere import FiliereController
from schemas.response import ApiResponse
from core.dependencies import require_role , get_current_user
from models.user import User

router = APIRouter(prefix="/filieres", tags=["Filieres"])


# ---------- Créer une filière ----------
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[FiliereRead])
def create_new_filiere(
        filiere_data: FiliereCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_role(["admin"]))
):
    """Créer une nouvelle filière."""
    controller = FiliereController(db)
    result = controller.create_filiere(filiere_data)
    return ApiResponse(success=True, message="Filière créée avec succès", data=result)


# ---------- Lister toutes les filières ----------
@router.get("/", response_model=ApiResponse[List[FiliereRead]])
def get_all_filieres(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Récupérer toutes les filières (paginé)."""
    controller = FiliereController(db)
    result = controller.get_all_filieres(skip, limit)
    return ApiResponse(success=True, message="Filières récupérées avec succès", data=result)


# ---------- Récupérer une filière par ID ----------
@router.get("/{filiere_id}", response_model=ApiResponse[FiliereRead])
def get_filiere_by_id_route(
    filiere_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Récupérer une filière par son ID."""
    controller = FiliereController(db)
    result = controller.get_filiere_by_id(filiere_id)
    return ApiResponse(success=True, message="Filière récupérée avec succès", data=result)


# ---------- Modifier une filière ----------
@router.put("/{filiere_id}", response_model=ApiResponse[FiliereRead])
def update_existing_filiere(
    filiere_id: int,
    filiere_data: FiliereUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Modifier une filière existante."""
    controller = FiliereController(db)
    result = controller.update_filiere(filiere_id, filiere_data)
    return ApiResponse(success=True, message="Filière mise à jour avec succès", data=result)


# ---------- Supprimer une filière ----------
@router.delete("/{filiere_id}", response_model=ApiResponse[None])
def delete_existing_filiere(
    filiere_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))

):
    """Supprimer une filière."""
    controller = FiliereController(db)
    controller.delete_filiere(filiere_id)
    return ApiResponse(success=True, message="Filière supprimée avec succès", data=None)