
# routes/enseignements.py - Routes pour les enseignements

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from schemas.enseignement import EnseignementCreate, EnseignementRead, EnseignementUpdate
from controllers.enseignement import EnseignementController
from core.dependencies import get_current_user, require_role
from schemas.response import ApiResponse

router = APIRouter(prefix="/enseignements", tags=["Enseignements"])


# ---------- 1. Assigner un professeur à une matière ----------
# Permission : Admin uniquement
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[EnseignementRead])
def create_enseignement(
    enseignement_data: EnseignementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Assigner un professeur à une matière. Réservé à l'administrateur."""
    controller = EnseignementController(db)
    result = controller.assigner_enseignement(enseignement_data)
    return ApiResponse(success=True, message="Professeur assigné à la matière avec succès", data=result)


# ---------- 2. Récupérer les enseignements d'un professeur ----------
# Permission : Admin, Professeur (soi-même) — logique gérée dans le service
@router.get("/professeur/{professeur_id}", response_model=ApiResponse[List[EnseignementRead]])
def get_enseignements_by_professeur_route(
    professeur_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère toutes les matières enseignées par un professeur.
    - Un professeur ne peut voir que ses propres enseignements
    - Admin peut voir tous les enseignements
    """
    controller = EnseignementController(db)
    result = controller.get_enseignements_by_professeur(professeur_id,current_user )
    return ApiResponse(success=True, message="Enseignements récupérés avec succès", data=result)


# ---------- 3. Récupérer les professeurs d'une matière ----------
# Permission : Admin, Professeur
@router.get("/matiere/{matiere_id}", response_model=ApiResponse[List[EnseignementRead]])
def get_enseignements_by_matiere_route(
    matiere_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "professeur"]))
):
    """Récupère tous les professeurs qui enseignent une matière. Réservé à l'admin et aux professeurs."""
    controller = EnseignementController(db)
    result = controller.get_enseignements_by_matiere(matiere_id)
    return ApiResponse(success=True, message="Enseignements récupérés avec succès", data=result)


# ---------- 4. Récupérer tous les enseignements ----------
# Permission : Admin uniquement
@router.get("/", response_model=ApiResponse[List[EnseignementRead]])
def get_all_enseignements_route(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Récupère tous les enseignements (paginé). Réservé à l'administrateur."""
    controller = EnseignementController(db)
    result = controller.get_all_enseignements(skip, limit)
    return ApiResponse(success=True, message="Enseignements récupérés avec succès", data=result)


# ---------- 5. Supprimer un enseignement ----------
# Permission : Admin uniquement
@router.delete("/{enseignement_id}", response_model=ApiResponse[None])
def delete_enseignement(
    enseignement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Supprime un enseignement (désassigner un professeur d'une matière). Réservé à l'administrateur."""
    controller = EnseignementController(db)
    controller.supprimer_enseignement(enseignement_id)
    return ApiResponse(success=True, message="Enseignement supprimé avec succès", data=None)


# ---------- 6. Modifier un enseignement ----------
# Permission : Admin uniquement
@router.put("/{enseignement_id}", response_model=ApiResponse[EnseignementRead])
def update_enseignement_route(
    enseignement_id: int,
    enseignement_data: EnseignementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Modifie un enseignement existant.
    Permet de changer le professeur, la matière ou le semestre.
    Réservé à l'administrateur.
    """
    controller = EnseignementController(db)
    result = controller.update_enseignement(enseignement_id, enseignement_data)
    return ApiResponse(success=True, message="Enseignement mis à jour avec succès", data=result)