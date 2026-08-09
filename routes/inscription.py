# ============================================================
# routes/inscriptions.py - Routes pour les inscriptions
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from schemas.inscription import InscriptionCreate, InscriptionRead
from services.inscription_service import (
    inscrire_etudiant,
    get_inscriptions_by_etudiant,
    get_inscriptions_by_matiere,
    get_all_inscriptions,
    supprimer_inscription
)
from core.dependencies import get_current_user, require_role
from core.handlers import handle_request
from schemas.response import ApiResponse

router = APIRouter(prefix="/inscriptions", tags=["Inscriptions"])


# ---------- 1. Inscrire un étudiant à une matière ----------
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[InscriptionRead])
def create_inscription(
    inscription_data: InscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    """
    Inscrit un étudiant à une matière.
    """
    return handle_request(
        inscrire_etudiant,
        "Inscription créée avec succès",
        db,
        inscription_data
    )


# ---------- 2. Récupérer les inscriptions d'un étudiant ----------
@router.get("/etudiant/{etudiant_id}", response_model=ApiResponse[List[InscriptionRead]])
def get_inscriptions_by_etudiant_route(
    etudiant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère toutes les inscriptions d'un étudiant.
    """
    user_roles = [role.name for role in current_user.roles]

    if current_user.id != etudiant_id and "admin" not in user_roles and "scolarite" not in user_roles and "professeur" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas l'autorisation de voir ces inscriptions"
        )

    return handle_request(
        get_inscriptions_by_etudiant,
        "Inscriptions récupérées avec succès",
        db,
        etudiant_id
    )


# ---------- 3. Récupérer les inscriptions d'une matière ----------
@router.get("/matiere/{matiere_id}", response_model=ApiResponse[List[InscriptionRead]])
def get_inscriptions_by_matiere_route(
    matiere_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite", "professeur"]))
):
    """
    Récupère toutes les inscriptions d'une matière.
    """
    return handle_request(
        get_inscriptions_by_matiere,
        "Inscriptions récupérées avec succès",
        db,
        matiere_id
    )


# ---------- 4. Récupérer toutes les inscriptions ----------
@router.get("/", response_model=ApiResponse[List[InscriptionRead]])
def get_all_inscriptions_route(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    """
    Récupère toutes les inscriptions.
    """
    return handle_request(
        get_all_inscriptions,
        "Inscriptions récupérées avec succès",
        db,
        skip,
        limit
    )


# ---------- 5. Supprimer une inscription ----------
@router.delete("/{etudiant_id}/{matiere_id}/{semestre}", response_model=ApiResponse[None])
def delete_inscription(
    etudiant_id: int,
    matiere_id: int,
    semestre: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    """
    Supprime une inscription.
    """
    return handle_request(
        supprimer_inscription,
        "Inscription supprimée avec succès",
        db,
        etudiant_id,
        matiere_id,
        semestre
    )