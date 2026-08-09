# ============================================================
# routes/bulletins.py - Routes pour les bulletins et résultats
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.user import User
from schemas.resultat_semestre import ResultatSemestreRead
from schemas.bulletin import CloturerSemestreRequest
from services.bulletin_service import (
    generer_bulletin_etudiant,
    sauvegarder_resultat_semestre,
    calculer_moyenne_semestre,
    calculer_moyenne_matiere_etudiant,
    generer_pv_classe
)
from core.dependencies import get_current_user, require_role
from core.handlers import handle_request
from schemas.response import ApiResponse

router = APIRouter(prefix="/bulletins", tags=["Bulletins"])


# ---------- 1. Générer le bulletin d'un étudiant ----------
# Permission : Étudiant (soi-même), Professeur, Admin, Scolarité
@router.get("/etudiant/{etudiant_id}", response_model=ApiResponse)
def get_bulletin_etudiant(
    etudiant_id: int,
    semestre: str,
    annee_universitaire: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Génère le bulletin d'un étudiant pour un semestre donné.
    - Un étudiant ne peut voir que son propre bulletin
    - Professeur, Admin et Scolarité peuvent voir tous les bulletins
    """
    user_roles = [role.name for role in current_user.roles]

    # Vérification des permissions
    if current_user.id != etudiant_id and "professeur" not in user_roles and "admin" not in user_roles and "scolarite" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas l'autorisation de voir ce bulletin"
        )

    return handle_request(
        generer_bulletin_etudiant,
        "Bulletin généré avec succès",
        db,
        etudiant_id,
        semestre,
        annee_universitaire
    )


# ---------- 2. Clôturer un semestre ----------
# Permission : Admin, Scolarité
@router.post("/cloturer", response_model=ApiResponse)
def cloturer_semestre(
    data: CloturerSemestreRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    """
    Clôture le semestre pour un étudiant.
    - Calcule la moyenne du semestre
    - Sauvegarde le résultat dans la table resultats_semestre
    - Marque le résultat comme officiel
    - Réservé à l'Admin et à la Scolarité
    """
    return handle_request(
        sauvegarder_resultat_semestre,
        "Semestre clôturé avec succès",
        db,
        data.etudiant_id,
        data.semestre,
        data.annee_universitaire
    )


# ---------- 3. Récupérer les résultats officiels d'un étudiant ----------
# Permission : Étudiant (soi-même), Admin, Scolarité
@router.get("/resultats/{etudiant_id}", response_model=ApiResponse)
def get_resultats_etudiant(
    etudiant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère tous les résultats officiels enregistrés d'un étudiant.
    - Un étudiant ne peut voir que ses propres résultats
    - Admin et Scolarité peuvent voir tous les résultats
    """
    user_roles = [role.name for role in current_user.roles]

    if current_user.id != etudiant_id and "admin" not in user_roles and "scolarite" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas l'autorisation de voir ces résultats"
        )

    from crud.resultat_semestre import get_by_etudiant

    resultats = get_by_etudiant(db, etudiant_id)

    return ApiResponse(
        success=True,
        message="Résultats récupérés avec succès",
        data=[ResultatSemestreRead.model_validate(r) for r in resultats]
    )


# ---------- 4. Calculer la moyenne d'un semestre (sans sauvegarder) ----------
# Permission : Étudiant (soi-même), Professeur, Admin, Scolarité
@router.get("/calcul/semestre", response_model=ApiResponse)
def get_calcul_semestre(
    etudiant_id: int,
    semestre: str,
    annee_universitaire: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Calcule la moyenne d'un semestre pour un étudiant.
    - Résultat non sauvegardé (calcul dynamique)
    - Utile pour un aperçu avant clôture
    """
    user_roles = [role.name for role in current_user.roles]

    if current_user.id != etudiant_id and "professeur" not in user_roles and "admin" not in user_roles and "scolarite" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas l'autorisation de voir ce calcul"
        )

    return handle_request(
        calculer_moyenne_semestre,
        "Calcul effectué avec succès",
        db,
        etudiant_id,
        semestre,
        annee_universitaire
    )


# ---------- 5. Calculer la moyenne d'une matière pour un étudiant ----------
# Permission : Étudiant (soi-même), Professeur, Admin, Scolarité
@router.get("/matiere/{matiere_id}/etudiant/{etudiant_id}", response_model=ApiResponse)
def get_moyenne_matiere_etudiant(
    matiere_id: int,
    etudiant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Calcule la moyenne d'un étudiant pour une matière spécifique.
    """
    user_roles = [role.name for role in current_user.roles]

    if current_user.id != etudiant_id and "professeur" not in user_roles and "admin" not in user_roles and "scolarite" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas l'autorisation de voir cette moyenne"
        )

    return handle_request(
        calculer_moyenne_matiere_etudiant,
        "Moyenne calculée avec succès",
        db,
        etudiant_id,
        matiere_id
    )


# ---------- 6. Procès-verbal de la classe ----------
# Permission : Admin, Scolarité
@router.get("/pv/classe", response_model=ApiResponse)
def get_pv_classe(
    semestre: str,
    annee_universitaire: str,
    filiere_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    """
    Génère le procès-verbal d'une classe.
    - Liste tous les étudiants avec leurs moyennes
    - Peut être filtré par filiere_id
    - Réservé à l'Admin et à la Scolarité
    """
    return handle_request(
        generer_pv_classe,
        "PV généré avec succès",
        db,
        semestre,
        annee_universitaire,
        filiere_id
    )