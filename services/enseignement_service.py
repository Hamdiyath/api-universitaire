# ============================================================
# services/enseignement_service.py - Logique métier pour Enseignement
# ============================================================

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

from crud.enseignement import (
    get_by_professeur_and_matiere,
    get_by_professeur,
    get_by_matiere,
    get_all,
    get_by_id,
    create,
    delete_by_id , #← On garde uniquement delete_by_id
    update
)
from crud.user import get_by_id as get_user_by_id
from crud.matiere import get_by_id as get_matiere_by_id
from schemas.enseignement import EnseignementCreate, EnseignementRead , EnseignementUpdate


# ---------- 1. Assigner un professeur à une matière ----------
def assigner_enseignement(db: Session, enseignement_data: EnseignementCreate):
    """
    Assigner un professeur à une matière.
    Vérifie que le professeur et la matière existent.
    Vérifie que l'assignation n'existe pas déjà.
    """
    # 1. Vérifier que le professeur existe
    professeur = get_user_by_id(db, enseignement_data.professeur_id)
    if not professeur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professeur non trouvé"
        )

    # 2. Vérifier que la matière existe
    matiere = get_matiere_by_id(db, enseignement_data.matiere_id)
    if not matiere:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matière non trouvée"
        )

    # 3. Vérifier que l'assignation n'existe pas déjà
    existing = get_by_professeur_and_matiere(
        db,
        enseignement_data.professeur_id,
        enseignement_data.matiere_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce professeur est déjà assigné à cette matière"
        )

    # 4. Créer l'enseignement
    new_enseignement = create(db, enseignement_data.model_dump())
    return EnseignementRead.model_validate(new_enseignement)


# ---------- 2. Récupérer les enseignements d'un professeur ----------
def get_enseignements_by_professeur(db: Session, professeur_id: int) -> List[EnseignementRead]:
    """
    Récupère toutes les matières enseignées par un professeur.
    """
    professeur = get_user_by_id(db, professeur_id)
    if not professeur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professeur non trouvé"
        )

    enseignements = get_by_professeur(db, professeur_id)
    return [EnseignementRead.model_validate(e) for e in enseignements]


# ---------- 3. Récupérer les professeurs d'une matière ----------
def get_enseignements_by_matiere(db: Session, matiere_id: int) -> List[EnseignementRead]:
    """
    Récupère tous les professeurs qui enseignent une matière.
    """
    matiere = get_matiere_by_id(db, matiere_id)
    if not matiere:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matière non trouvée"
        )

    enseignements = get_by_matiere(db, matiere_id)
    return [EnseignementRead.model_validate(e) for e in enseignements]


# ---------- 4. Récupérer tous les enseignements ----------
def get_all_enseignements(db: Session, skip: int = 0, limit: int = 100) -> List[EnseignementRead]:
    """
    Récupère tous les enseignements (paginé).
    """
    enseignements = get_all(db, skip, limit)
    return [EnseignementRead.model_validate(e) for e in enseignements]


# ---------- 5. Récupérer un enseignement par ID ----------
def get_enseignement_by_id(db: Session, enseignement_id: int) -> EnseignementRead:
    """
    Récupère un enseignement par son ID.
    Lève une exception si l'enseignement n'existe pas.
    """
    enseignement = get_by_id(db, enseignement_id)
    if not enseignement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enseignement non trouvé"
        )
    return EnseignementRead.model_validate(enseignement)


# ---------- 6. Supprimer un enseignement ----------
def supprimer_enseignement(db: Session, enseignement_id: int):
    """
    Supprime un enseignement par son ID.
    Vérifie que l'enseignement existe avant de le supprimer.
    """
    # 1. Vérifier que l'enseignement existe
    enseignement = get_by_id(db, enseignement_id)
    if not enseignement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enseignement non trouvé"
        )

    # 2. Supprimer l'enseignement
    delete_by_id(db, enseignement_id)
    return None


def update_enseignement(db: Session, enseignement_id: int, enseignement_data: EnseignementUpdate) -> EnseignementRead:
    """
    Met à jour un enseignement existant.
    Vérifie que l'enseignement existe.
    Si le professeur ou la matière est modifié, vérifie que les nouvelles valeurs existent.
    """
    # 1. Vérifier que l'enseignement existe
    enseignement = get_by_id(db, enseignement_id)
    if not enseignement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enseignement non trouvé"
        )

    # 2. Récupérer les données à mettre à jour
    update_data = enseignement_data.model_dump(exclude_unset=True)

    # 3. Si le professeur est modifié, vérifier qu'il existe
    if "professeur_id" in update_data:
        professeur = get_user_by_id(db, update_data["professeur_id"])
        if not professeur:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Professeur non trouvé"
            )

    # 4. Si la matière est modifiée, vérifier qu'elle existe
    if "matiere_id" in update_data:
        matiere = get_matiere_by_id(db, update_data["matiere_id"])
        if not matiere:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Matière non trouvée"
            )

    # 5. Mettre à jour l'enseignement
    updated_enseignement = update(db, enseignement_id, update_data)
    return EnseignementRead.model_validate(updated_enseignement)