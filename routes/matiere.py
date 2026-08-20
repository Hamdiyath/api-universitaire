
# routes/matiere.py - Routes pour les matières


from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas.matiere import MatiereCreate, MatiereUpdate, MatiereRead
from controllers.matiere import MatiereController
from schemas.response import ApiResponse
from models.user import User
from core.dependencies import require_role , get_current_user

router = APIRouter(prefix="/matieres", tags=["Matieres"])


# ---------- Créer une matière ----------
@router.post("/",  response_model=ApiResponse[MatiereRead])
def create_new_matiere(
    matiere_data: MatiereCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Créer une nouvelle matière."""
    controller = MatiereController(db)
    result = controller.create_matiere(matiere_data)
    return ApiResponse(success=True, message="Matière créée avec succès", data=result)


# ---------- Lister toutes les matières ----------
@router.get("/", response_model=ApiResponse[List[MatiereRead]])
def get_all_matieres(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Récupérer toutes les matières (paginé)."""
    controller = MatiereController(db)
    result = controller.get_all_matieres(skip, limit)
    return ApiResponse(success=True, message="Matières récupérées avec succès", data=result)


# ---------- Récupérer une matière par ID ----------
@router.get("/{matiere_id}", response_model=ApiResponse[MatiereRead])
def get_matiere_by_id_route(
    matiere_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Récupérer une matière par son ID."""
    controller = MatiereController(db)
    result = controller.get_matiere_by_id(matiere_id)
    return ApiResponse(success=True, message="Matière récupérée avec succès", data=result)


# ---------- Modifier une matière ----------
@router.put("/{matiere_id}", response_model=ApiResponse[MatiereRead])
def update_existing_matiere(
    matiere_id: int,
    matiere_data: MatiereUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Modifier une matière existante."""
    controller = MatiereController(db)
    result = controller.update_matiere(matiere_id, matiere_data)
    return ApiResponse(success=True, message="Matière mise à jour avec succès", data=result)


# ---------- Supprimer une matière ----------
@router.delete("/{matiere_id}", response_model=ApiResponse[None])
def delete_existing_matiere(
    matiere_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Supprimer une matière."""
    controller = MatiereController(db)
    controller.delete_matiere(matiere_id)
    return ApiResponse(success=True, message="Matière supprimée avec succès", data=None)