
# routes/resultat_matiere.py - Routes pour les résultats matière

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from schemas.resultat_matiere import ResultatMatiereRead
from schemas.response import ApiResponse
from controllers.resultat_matiere import ResultatMatiereController
from core.dependencies import get_current_user, require_role

router = APIRouter(prefix="/resultats-matieres", tags=["Résultats Matière"])


# ---------- 1. Générer les résultats d'un étudiant pour un semestre ----------
# Permission : Admin, Scolarité, Professeur (s'il enseigne dans la filière)
@router.post(
    "/etudiant/{etudiant_id}/generer",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[List[ResultatMatiereRead]]
)
def generer_resultats_etudiant_route(
    etudiant_id: int,
    semestre: str,
    annee_universitaire: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Génère les lignes de résultat à blanc pour un étudiant, pour toutes
    les matières de sa filière correspondant au semestre donné.
    Réservé à l'Admin, la Scolarité, et au Professeur (s'il enseigne
    dans la filière de l'étudiant).
    """
    controller = ResultatMatiereController(db)
    result = controller.generer_resultats_etudiant(etudiant_id, semestre, annee_universitaire, current_user)
    return ApiResponse(success=True, message="Résultats générés avec succès", data=result)


# ---------- 2. Récupérer une ligne par ID ----------
# Permission : Admin, Scolarité
@router.get("/{resultat_id}", response_model=ApiResponse[ResultatMatiereRead])
def get_resultat_by_id_route(
    resultat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    """Récupère une ligne de résultat par son ID. Réservé à l'Admin et à la Scolarité."""
    controller = ResultatMatiereController(db)
    result = controller.get_by_id(resultat_id)
    return ApiResponse(success=True, message="Résultat récupéré avec succès", data=result)


# ---------- 3. Récupérer les résultats d'un étudiant ----------
# Permission : Étudiant (soi-même), Admin, Scolarité, Professeur
@router.get("/etudiant/{etudiant_id}", response_model=ApiResponse[List[ResultatMatiereRead]])
def get_resultats_by_etudiant_route(
    etudiant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les résultats d'un étudiant.
    - Étudiant : voit uniquement les siens
    - Admin/Scolarité/Professeur : voient ceux de n'importe quel étudiant
    """
    controller = ResultatMatiereController(db)
    result = controller.get_resultats_by_etudiant(etudiant_id, current_user)
    return ApiResponse(success=True, message="Résultats récupérés avec succès", data=result)


# ---------- 4. Récupérer les résultats d'une matière ----------
# Permission : Admin, Scolarité, Professeur
@router.get("/matiere/{matiere_id}", response_model=ApiResponse[List[ResultatMatiereRead]])
def get_resultats_by_matiere_route(
    matiere_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite", "professeur"]))
):
    """Récupère les résultats d'une matière. Réservé à l'Admin, la Scolarité et aux Professeurs."""
    controller = ResultatMatiereController(db)
    result = controller.get_resultats_by_matiere(matiere_id)
    return ApiResponse(success=True, message="Résultats récupérés avec succès", data=result)


# ---------- 5. Récupérer tous les résultats ----------
# Permission : Admin, Scolarité
@router.get("/", response_model=ApiResponse[List[ResultatMatiereRead]])
def get_all_resultats_route(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    """Récupère tous les résultats (paginé). Réservé à l'Admin et à la Scolarité."""
    controller = ResultatMatiereController(db)
    result = controller.get_all_resultats(skip, limit)
    return ApiResponse(success=True, message="Résultats récupérés avec succès", data=result)


# ---------- 6. Supprimer une ligne ----------
# Permission : Admin, Scolarité
@router.delete("/{resultat_id}", response_model=ApiResponse[None])
def delete_resultat_route(
    resultat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    """Supprime une ligne de résultat. Réservé à l'Admin et à la Scolarité."""
    controller = ResultatMatiereController(db)
    controller.supprimer_resultat(resultat_id)
    return ApiResponse(success=True, message="Résultat supprimé avec succès", data=None)



# ---------- 7. Générer les dettes pour l'année suivante ----------
# Permission : Admin, Scolarité
@router.post("/generer-dettes", response_model=ApiResponse[dict])
def generer_dettes_annee_suivante_route(
    semestre: str,
    annee_universitaire: str,
    nouvelle_annee_universitaire: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    """
    Parcourt les lignes en dette (NON_VALIDE ou NON_NOTE) pour un
    semestre/année donné, et génère les lignes de reprise correspondantes
    pour l'année universitaire suivante. Idempotent.
    Réservé à l'Admin et à la Scolarité.
    """
    controller = ResultatMatiereController(db)
    result = controller.generer_dettes_annee_suivante(semestre, annee_universitaire, nouvelle_annee_universitaire)
    return ApiResponse(success=True, message="Dettes générées avec succès", data=result)