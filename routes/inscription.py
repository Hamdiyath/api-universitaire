# routes/inscription.py - Routes pour les inscriptions=
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from schemas.inscription import InscriptionCreate, InscriptionUpdate, InscriptionRead
from schemas.response import ApiResponse
from controllers.inscription import InscriptionController
from core.dependencies import get_current_user, require_role

router = APIRouter(prefix="/inscriptions", tags=["Inscriptions"])


# ---------- 1. Inscrire un étudiant à une matière ----------
# Permission : Admin, Scolarité
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[InscriptionRead])
def create_inscription(
    inscription_data: InscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    """Inscrit un étudiant à une matière. Réservé à l'Admin et à la Scolarité."""
    controller = InscriptionController(db)
    result = controller.inscrire_etudiant(inscription_data)
    return ApiResponse(success=True, message="Inscription créée avec succès", data=result)


# ---------- 2. Récupérer une inscription par ID ----------
# Permission : Admin, Scolarité
@router.get("/{inscription_id}", response_model=ApiResponse[InscriptionRead])
def get_inscription_by_id_route(
    inscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    """Récupère une inscription par son ID. Réservé à l'Admin et à la Scolarité."""
    controller = InscriptionController(db)
    result = controller.get_inscription_by_id(inscription_id)
    return ApiResponse(success=True, message="Inscription récupérée avec succès", data=result)


# ---------- 3. Récupérer les inscriptions d'un étudiant ----------
# Permission : Étudiant (soi-même), Admin, Scolarité
@router.get("/etudiant/{etudiant_id}", response_model=ApiResponse[List[InscriptionRead]])
def get_inscriptions_by_etudiant_route(
    etudiant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les inscriptions d'un étudiant.
    - Étudiant : voit uniquement ses propres inscriptions
    - Admin/Scolarité : voient celles de n'importe quel étudiant
    - Professeur : aucun accès
    """
    controller = InscriptionController(db)
    result = controller.get_inscriptions_by_etudiant(etudiant_id, current_user)
    return ApiResponse(success=True, message="Inscriptions récupérées avec succès", data=result)


# ---------- 4. Récupérer les inscriptions d'une matière ----------
# Permission : Admin, Scolarité
@router.get("/matiere/{matiere_id}", response_model=ApiResponse[List[InscriptionRead]])
def get_inscriptions_by_matiere_route(
    matiere_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    """Récupère les inscriptions d'une matière. Réservé à l'Admin et à la Scolarité."""
    controller = InscriptionController(db)
    result = controller.get_inscriptions_by_matiere(matiere_id)
    return ApiResponse(success=True, message="Inscriptions récupérées avec succès", data=result)


# ---------- 5. Récupérer toutes les inscriptions ----------
# Permission : Admin, Scolarité
@router.get("/", response_model=ApiResponse[List[InscriptionRead]])
def get_all_inscriptions_route(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    """Récupère toutes les inscriptions (paginé). Réservé à l'Admin et à la Scolarité."""
    controller = InscriptionController(db)
    result = controller.get_all_inscriptions(skip, limit)
    return ApiResponse(success=True, message="Inscriptions récupérées avec succès", data=result)


# ---------- 6. Modifier une inscription ----------
# Permission : Admin, Scolarité
@router.put("/{inscription_id}", response_model=ApiResponse[InscriptionRead])
def update_inscription_route(
    inscription_id: int,
    update_data: InscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    """Modifie une inscription existante. Réservé à l'Admin et à la Scolarité."""
    controller = InscriptionController(db)
    result = controller.update_inscription(inscription_id, update_data)
    return ApiResponse(success=True, message="Inscription mise à jour avec succès", data=result)


# ---------- 7. Supprimer une inscription ----------
# Permission : Admin, Scolarité
@router.delete("/{inscription_id}", response_model=ApiResponse[None])
def delete_inscription_route(
    inscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    """Supprime une inscription. Réservé à l'Admin et à la Scolarité."""
    controller = InscriptionController(db)
    controller.supprimer_inscription(inscription_id)
    return ApiResponse(success=True, message="Inscription supprimée avec succès", data=None)