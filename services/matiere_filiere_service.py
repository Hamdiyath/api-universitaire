
# services/matiere_filiere_service.py - Logique métier pour MatiereFiliere


from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

from crud.matiere_filiere import (
    get_by_id,
    get_by_matiere,
    get_by_filiere,
    get_all,
    create,
    delete
)
from crud.matiere import get_by_id as get_matiere_by_id
from crud.filiere import get_by_id as get_filiere_by_id
from schemas.matiere_filiere import MatiereFiliereCreate, MatiereFiliereRead


# ---------- Création d'une association ----------
def associer_matiere_filiere(db: Session, association_data: MatiereFiliereCreate):
    """
    Associe une matière à une filière pour un semestre donné.
    Vérifie que la matière et la filière existent.
    Vérifie que l'association n'existe pas déjà.
    """
    # 1. Vérifier que la matière existe
    matiere = get_matiere_by_id(db, association_data.matiere_id)
    if not matiere:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matière non trouvée"
        )

    # 2. Vérifier que la filière existe
    filiere = get_filiere_by_id(db, association_data.filiere_id)
    if not filiere:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filière non trouvée"
        )

    # 3. Vérifier que l'association n'existe pas déjà
    existing = get_by_id(
        db,
        association_data.matiere_id,
        association_data.filiere_id,
        association_data.semestre
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette matière est déjà associée à cette filière pour ce semestre"
        )

    # 4. Créer l'association
    new_association = create(db, association_data.model_dump())
    return MatiereFiliereRead.model_validate(new_association)


# ---------- Récupération des associations par matière ----------
def get_associations_by_matiere(db: Session, matiere_id: int) -> List[MatiereFiliereRead]:
    """
    Récupère toutes les associations d'une matière.
    Vérifie que la matière existe.
    """
    matiere = get_matiere_by_id(db, matiere_id)
    if not matiere:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matière non trouvée"
        )

    associations = get_by_matiere(db, matiere_id)
    return [MatiereFiliereRead.model_validate(a) for a in associations]


# ---------- Récupération des associations par filière ----------
def get_associations_by_filiere(db: Session, filiere_id: int) -> List[MatiereFiliereRead]:
    """
    Récupère toutes les associations d'une filière.
    Vérifie que la filière existe.
    """
    filiere = get_filiere_by_id(db, filiere_id)
    if not filiere:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filière non trouvée"
        )

    associations = get_by_filiere(db, filiere_id)
    return [MatiereFiliereRead.model_validate(a) for a in associations]


# ---------- Récupération de toutes les associations ----------
def get_all_associations(db: Session, skip: int = 0, limit: int = 100) -> List[MatiereFiliereRead]:
    """
    Récupère toutes les associations (paginé).
    """
    associations = get_all(db, skip, limit)
    return [MatiereFiliereRead.model_validate(a) for a in associations]


# ---------- Suppression d'une association ----------
def supprimer_association(
    db: Session,
    matiere_id: int,
    filiere_id: int,
    semestre: str
):
    """
    Supprime une association matière-filière.
    Vérifie que l'association existe.
    """
    existing = get_by_id(db, matiere_id, filiere_id, semestre)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Association non trouvée"
        )

    delete(db, matiere_id, filiere_id, semestre)
    return None