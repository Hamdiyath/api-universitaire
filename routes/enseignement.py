# ============================================================
# routes/enseignements.py - Routes pour les enseignements
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from schemas.enseignement import EnseignementCreate, EnseignementRead
from services.enseignement_service import (
    assigner_enseignement,
    get_enseignements_by_professeur,
    get_enseignements_by_matiere,
    get_all_enseignements,
    supprimer_enseignement
)
from core.dependencies import get_current_user, require_role
from core.handlers import handle_request
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
    """
    Assigner un professeur à une matière.
    Réservé à l'administrateur.
    """
    return handle_request(
        assigner_enseignement,
        "Professeur assigné à la matière avec succès",
        db,
        enseignement_data
    )


# ---------- 2. Récupérer les enseignements d'un professeur ----------
# Permission : Admin, Professeur (soi-même)
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
    user_roles = [role.name for role in current_user.roles]

    if current_user.id != professeur_id and "admin" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas l'autorisation de voir ces enseignements"
        )

    return handle_request(
        get_enseignements_by_professeur,
        "Enseignements récupérés avec succès",
        db,
        professeur_id
    )


# ---------- 3. Récupérer les professeurs d'une matière ----------
# Permission : Admin, Professeur
@router.get("/matiere/{matiere_id}", response_model=ApiResponse[List[EnseignementRead]])
def get_enseignements_by_matiere_route(
    matiere_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "professeur"]))
):
    """
    Récupère tous les professeurs qui enseignent une matière.
    Réservé à l'admin et aux professeurs.
    """
    return handle_request(
        get_enseignements_by_matiere,
        "Enseignements récupérés avec succès",
        db,
        matiere_id
    )


# ---------- 4. Récupérer tous les enseignements ----------
# Permission : Admin uniquement
@router.get("/", response_model=ApiResponse[List[EnseignementRead]])
def get_all_enseignements_route(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Récupère tous les enseignements (paginé).
    Réservé à l'administrateur.
    """
    return handle_request(
        get_all_enseignements,
        "Enseignements récupérés avec succès",
        db,
        skip,
        limit
    )


# ---------- 5. Supprimer un enseignement ----------
# Permission : Admin uniquement
@router.delete("/{enseignement_id}", response_model=ApiResponse[None])
def delete_enseignement(
    enseignement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Supprime un enseignement (désassigner un professeur d'une matière).
    Réservé à l'administrateur.
    """
    return handle_request(
        supprimer_enseignement,
        "Enseignement supprimé avec succès",
        db,
        enseignement_id
    )