# ============================================================
# routes/bulletins.py - Routes pour les bulletins et résultats
# ============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models.user import User
from schemas.bulletin import CloturerSemestreRequest
from controllers.bulletin import BulletinController
from core.dependencies import get_current_user, require_role
from schemas.response import ApiResponse

router = APIRouter(prefix="/bulletins", tags=["Bulletins"])


# ---------- 1. Générer le bulletin d'un étudiant ----------
@router.get("/etudiant/{etudiant_id}", response_model=ApiResponse)
def get_bulletin_etudiant(
    etudiant_id: int,
    semestre: str,
    annee_universitaire: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Génère le bulletin d'un étudiant pour un semestre donné."""
    controller = BulletinController(db)
    result = controller.generer_bulletin_etudiant(etudiant_id, semestre, annee_universitaire, current_user)
    return ApiResponse(success=True, message="Bulletin généré avec succès", data=result)


# ---------- 2. Clôturer un semestre ----------
@router.post("/cloturer", response_model=ApiResponse)
def cloturer_semestre(
    data: CloturerSemestreRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    """Clôture le semestre pour un étudiant. Réservé à l'Admin et à la Scolarité."""
    controller = BulletinController(db)
    result = controller.sauvegarder_resultat_semestre(data.etudiant_id, data.semestre, data.annee_universitaire)
    return ApiResponse(success=True, message="Semestre clôturé avec succès", data=result)


# ---------- 3. Récupérer les résultats officiels d'un étudiant ----------
@router.get("/resultats/{etudiant_id}", response_model=ApiResponse)
def get_resultats_etudiant(
    etudiant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère tous les résultats officiels enregistrés d'un étudiant."""
    controller = BulletinController(db)
    result = controller.get_resultats_etudiant(etudiant_id, current_user)
    return ApiResponse(success=True, message="Résultats récupérés avec succès", data=result)


# ---------- 4. Calculer la moyenne d'un semestre (sans sauvegarder) ----------
@router.get("/calcul/semestre", response_model=ApiResponse)
def get_calcul_semestre(
    etudiant_id: int,
    semestre: str,
    annee_universitaire: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calcule la moyenne d'un semestre pour un étudiant (aperçu, non sauvegardé)."""
    controller = BulletinController(db)
    result = controller.get_calcul_semestre(etudiant_id, semestre, annee_universitaire, current_user)
    return ApiResponse(success=True, message="Calcul effectué avec succès", data=result)


# ---------- 5. Calculer la moyenne d'une matière pour un étudiant ----------
@router.get("/matiere/{matiere_id}/etudiant/{etudiant_id}", response_model=ApiResponse)
def get_moyenne_matiere_etudiant(
    matiere_id: int,
    etudiant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calcule la moyenne d'un étudiant pour une matière spécifique."""
    controller = BulletinController(db)
    result = controller.get_moyenne_matiere_etudiant(etudiant_id, matiere_id, current_user)
    return ApiResponse(success=True, message="Moyenne calculée avec succès", data=result)


# ---------- 6. Procès-verbal de la classe (Admin/Scolarité) ----------
@router.get("/pv/classe", response_model=ApiResponse)
def get_pv_classe(
    semestre: str,
    annee_universitaire: str,
    filiere_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    """Génère le procès-verbal d'une classe. Réservé à l'Admin et à la Scolarité."""
    controller = BulletinController(db)
    result = controller.generer_pv_classe(semestre, annee_universitaire, filiere_id)
    return ApiResponse(success=True, message="PV généré avec succès", data=result)


# ---------- 7. Procès-verbal d'une matière ----------
@router.get("/pv/matiere/{matiere_id}", response_model=ApiResponse)
def get_pv_matiere_route(
    matiere_id: int,
    semestre: str,
    annee_universitaire: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["professeur", "admin", "scolarite"]))
):
    """
    Génère le procès-verbal d'une matière.
    - Professeur : voit uniquement les étudiants de sa matière
    - Admin et Scolarité : voient tous les étudiants de la matière
    """
    controller = BulletinController(db)
    result = controller.generer_pv_matiere(matiere_id, semestre, annee_universitaire, current_user)
    return ApiResponse(success=True, message="PV récupéré avec succès", data=result)