# ============================================================
# routes/matieres_filieres.py - Routes pour les associations Matière-Filière
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from schemas.matiere_filiere import MatiereFiliereCreate, MatiereFiliereRead
from services.matiere_filiere_service import (
    associer_matiere_filiere,
    get_associations_by_matiere,
    get_associations_by_filiere,
    get_all_associations,
    supprimer_association
)
from core.dependencies import get_current_user, require_role
from core.handlers import handle_request
from schemas.response import ApiResponse

router = APIRouter(prefix="/matieres-filieres", tags=["Matières-Filières"])


# ---------- 1. Associer une matière à une filière ----------
# Permission : Admin uniquement
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[MatiereFiliereRead])
def create_association(
    association_data: MatiereFiliereCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Associer une matière à une filière pour un semestre donné.
    Réservé à l'administrateur.
    """
    return handle_request(
        associer_matiere_filiere,
        "Association créée avec succès",
        db,
        association_data
    )


# ---------- 2. Récupérer les associations d'une matière ----------
# Permission : Admin, Scolarité, Professeur
@router.get("/matiere/{matiere_id}", response_model=ApiResponse[List[MatiereFiliereRead]])
def get_associations_by_matiere_route(
    matiere_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite", "professeur"]))
):
    """
    Récupère toutes les filières associées à une matière.
    Réservé à l'admin, la scolarité et les professeurs.
    """
    return handle_request(
        get_associations_by_matiere,
        "Associations récupérées avec succès",
        db,
        matiere_id
    )


# ---------- 3. Récupérer les associations d'une filière ----------
# Permission : Admin, Scolarité, Professeur (toutes les filières)
#              Étudiant (uniquement sa propre filière)
@router.get("/filiere/{filiere_id}", response_model=ApiResponse[List[MatiereFiliereRead]])
def get_associations_by_filiere_route(
    filiere_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ← Plus de require_role
):
    """
    Récupère toutes les matières associées à une filière.
    - Admin, Scolarité, Professeur : voient toutes les filières
    - Étudiant : voit uniquement sa propre filière
    - Autres : accès refusé
    """
    user_roles = [role.name for role in current_user.roles]

    # 1. Si l'utilisateur est étudiant, il ne peut voir que sa propre filière
    if "etudiant" in user_roles:
        # Vérifier que l'étudiant a une filière
        if current_user.filiere_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vous n'êtes pas assigné à une filière"
            )
        # Vérifier que la filière demandée est la sienne
        if current_user.filiere_id != filiere_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez voir que les matières de votre propre filière"
            )

    # 2. Admin, Scolarité, Professeur peuvent voir toutes les filières
    elif "admin" not in user_roles and "scolarite" not in user_roles and "professeur" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas l'autorisation de voir cette filière"
        )

    # 3. Récupérer les associations
    return handle_request(
        get_associations_by_filiere,
        "Associations récupérées avec succès",
        db,
        filiere_id
    )


# ---------- 4. Récupérer toutes les associations ----------
# Permission : Admin uniquement
@router.get("/", response_model=ApiResponse[List[MatiereFiliereRead]])
def get_all_associations_route(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Récupère toutes les associations (paginé).
    Réservé à l'administrateur.
    """
    return handle_request(
        get_all_associations,
        "Associations récupérées avec succès",
        db,
        skip,
        limit
    )


# ---------- 5. Supprimer une association ----------
# Permission : Admin uniquement
@router.delete("/{matiere_id}/{filiere_id}/{semestre}", response_model=ApiResponse[None])
def delete_association(
    matiere_id: int,
    filiere_id: int,
    semestre: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Supprime une association matière-filière.
    Réservé à l'administrateur.
    """
    return handle_request(
        supprimer_association,
        "Association supprimée avec succès",
        db,
        matiere_id,
        filiere_id,
        semestre
    )