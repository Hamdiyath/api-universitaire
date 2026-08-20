
# routes/decision_annuelle.py - Routes pour les décisions annuelles

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from schemas.decision_annuelle import DecisionAnnuelleRead, DecisionAnnuelleUpdate
from schemas.response import ApiResponse
from controllers.decision_annuelle import DecisionAnnuelleController
from core.dependencies import require_role, get_current_user
from exceptions.base import PermissionDeniedError

router = APIRouter(prefix="/decisions-annuelles", tags=["Décisions Annuelles"])


# ---------- 1. Générer la décision de passage d'un étudiant ----------
# Permission : Admin, Scolarité
@router.post(
    "/etudiant/{etudiant_id}/generer",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[DecisionAnnuelleRead]
)
def generer_decision_annuelle_route(
    etudiant_id: int,
    annee_universitaire: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    """
    Calcule et enregistre la décision de passage d'un étudiant pour une
    année universitaire. Met à jour son niveau académique en conséquence.
    Réservé à l'Admin et à la Scolarité.
    """
    controller = DecisionAnnuelleController(db)
    result = controller.generer_decision_annuelle(etudiant_id, annee_universitaire)
    return ApiResponse(success=True, message="Décision annuelle générée avec succès", data=result)


# ---------- 2. Récupérer une décision par ID ----------
# Permission : Admin, Scolarité
@router.get("/{decision_id}", response_model=ApiResponse[DecisionAnnuelleRead])
def get_decision_by_id_route(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    """Récupère une décision annuelle par son ID. Réservé à l'Admin et à la Scolarité."""
    controller = DecisionAnnuelleController(db)
    result = controller.get_by_id(decision_id)
    return ApiResponse(success=True, message="Décision récupérée avec succès", data=result)


# ---------- 3. Récupérer l'historique des décisions d'un étudiant ----------
# Permission : Étudiant (soi-même), Admin, Scolarité
@router.get("/etudiant/{etudiant_id}", response_model=ApiResponse[List[DecisionAnnuelleRead]])
def get_decisions_by_etudiant_route(etudiant_id: int,db: Session = Depends(get_db),current_user: User = Depends(get_current_user)
):
    """
    Récupère l'historique des décisions annuelles d'un étudiant.
    - Étudiant : uniquement les siennes
    - Admin/Scolarité : n'importe lequel
    """
    user_roles = [role.name for role in current_user.roles]
    if current_user.id != etudiant_id and not any(r in user_roles for r in ["admin", "scolarite"]):
        raise PermissionDeniedError("Vous n'avez pas l'autorisation de voir ces décisions")

    controller = DecisionAnnuelleController(db)
    result = controller.get_by_etudiant(etudiant_id)
    return ApiResponse(success=True, message="Décisions récupérées avec succès", data=result)


# ---------- 4. Récupérer toutes les décisions ----------
# Permission : Admin, Scolarité
@router.get("/", response_model=ApiResponse[List[DecisionAnnuelleRead]])
def get_all_decisions_route(skip: int = 0,limit: int = 100,db: Session = Depends(get_db),current_user: User = Depends(require_role(["admin", "scolarite"]))):
    """Récupère toutes les décisions annuelles (paginé). Réservé à l'Admin et à la Scolarité."""
    controller = DecisionAnnuelleController(db)
    result = controller.get_all(skip, limit)
    return ApiResponse(success=True, message="Décisions récupérées avec succès", data=result)


# ---------- 5. Corriger manuellement une décision ----------
# Permission : Admin uniquement
@router.put("/{decision_id}", response_model=ApiResponse[DecisionAnnuelleRead])
def update_decision_route(decision_id: int,update_data: DecisionAnnuelleUpdate,db: Session = Depends(get_db),current_user: User = Depends(require_role(["admin"]))):
    """
    Corrige manuellement une décision annuelle déjà actée
    (erreur de jury, recours étudiant accepté...).
    Réservé strictement à l'Admin.
    """
    controller = DecisionAnnuelleController(db)
    result = controller.update_decision(decision_id, update_data)
    return ApiResponse(success=True, message="Décision corrigée avec succès", data=result)