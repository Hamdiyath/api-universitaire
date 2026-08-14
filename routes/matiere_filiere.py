# routes/matieres_filieres.py - Routes pour les associations Matière-Filière


from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from schemas.matiere_filiere import MatiereFiliereCreate, MatiereFiliereRead
from controllers.matiere_filiere import MatiereFiliereController
from core.dependencies import get_current_user, require_role
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
    controller = MatiereFiliereController(db)
    result = controller.associer_matiere_filiere(association_data)
    return ApiResponse(success=True, message="Association créée avec succès", data=result)


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
    controller = MatiereFiliereController(db)
    result = controller.get_associations_by_matiere(matiere_id)
    return ApiResponse(success=True, message="Associations récupérées avec succès", data=result)


# ---------- 3. Récupérer les associations d'une filière ----------
# Permission : Admin, Scolarité, Professeur (toutes les filières)
#              Étudiant (uniquement sa propre filière)
@router.get("/filiere/{filiere_id}", response_model=ApiResponse[List[MatiereFiliereRead]])
def get_associations_by_filiere_route(
    filiere_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère toutes les matières associées à une filière.
    - Admin, Scolarité, Professeur : voient toutes les filières
    - Étudiant : voit uniquement sa propre filière
    - Autres : accès refusé
    La logique de permission est gérée dans le service.
    """
    controller = MatiereFiliereController(db)
    result = controller.get_associations_by_filiere(filiere_id, current_user)
    return ApiResponse(success=True, message="Associations récupérées avec succès", data=result)


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
    controller = MatiereFiliereController(db)
    result = controller.get_all_associations(skip, limit)
    return ApiResponse(success=True, message="Associations récupérées avec succès", data=result)


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
    controller = MatiereFiliereController(db)
    controller.supprimer_association(matiere_id, filiere_id, semestre)
    return ApiResponse(success=True, message="Association supprimée avec succès", data=None)