# ============================================================
# services/inscription_service.py - Logique métier pour Inscription
# ============================================================

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

from crud.inscription import (
    get_by_etudiant,
    get_by_matiere,
    get_by_etudiant_and_matieres,
    get_all,
    create,
    delete
)
from crud.user import get_by_id as get_user_by_id
from crud.matiere import get_by_id as get_matiere_by_id
from schemas.inscription import InscriptionCreate, InscriptionRead


def inscrire_etudiant(db: Session, inscription_data: InscriptionCreate):
    """
    Inscrit un étudiant à une matière.
    Vérifie que l'étudiant et la matière existent.
    Vérifie que l'inscription n'existe pas déjà.
    """
    # 1. Vérifier que l'étudiant existe
    etudiant = get_user_by_id(db, inscription_data.etudiant_id)
    if not etudiant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Étudiant non trouvé"
        )

    # 2. Vérifier que la matière existe
    matiere = get_matiere_by_id(db, inscription_data.matiere_id)
    if not matiere:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matière non trouvée"
        )

    # 3. Vérifier que l'inscription n'existe pas déjà
    existing = get_by_etudiant_and_matieres(
        db,
        inscription_data.etudiant_id,
        [inscription_data.matiere_id]
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet étudiant est déjà inscrit à cette matière"
        )

    # 4. Créer l'inscription
    new_inscription = create(db, inscription_data.model_dump())
    return InscriptionRead.model_validate(new_inscription)


def get_inscriptions_by_etudiant(db: Session, etudiant_id: int) -> List[InscriptionRead]:
    """
    Récupère toutes les inscriptions d'un étudiant.
    Vérifie que l'étudiant existe.
    """
    etudiant = get_user_by_id(db, etudiant_id)
    if not etudiant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Étudiant non trouvé"
        )

    inscriptions = get_by_etudiant(db, etudiant_id)
    return [InscriptionRead.model_validate(i) for i in inscriptions]


def get_inscriptions_by_matiere(db: Session, matiere_id: int) -> List[InscriptionRead]:
    """
    Récupère toutes les inscriptions d'une matière.
    Vérifie que la matière existe.
    """
    matiere = get_matiere_by_id(db, matiere_id)
    if not matiere:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matière non trouvée"
        )

    inscriptions = get_by_matiere(db, matiere_id)
    return [InscriptionRead.model_validate(i) for i in inscriptions]


def get_all_inscriptions(db: Session, skip: int = 0, limit: int = 100) -> List[InscriptionRead]:
    """
    Récupère toutes les inscriptions (paginé).
    """
    inscriptions = get_all(db, skip, limit)
    return [InscriptionRead.model_validate(i) for i in inscriptions]


def supprimer_inscription(
    db: Session,
    etudiant_id: int,
    matiere_id: int,
    semestre: str
):
    """
    Supprime une inscription.
    Vérifie que l'inscription existe.
    """
    # Vérifier que l'inscription existe
    inscriptions = get_by_etudiant_and_matieres(db, etudiant_id, [matiere_id])
    if not inscriptions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inscription non trouvée"
        )

    delete(db, etudiant_id, matiere_id, semestre)
    return None