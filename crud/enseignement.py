# ============================================================
# crud/enseignement.py - Opérations CRUD pour la table Enseignement
# ============================================================

from typing import Optional, List
from sqlalchemy.orm import Session

from models.enseignement import Enseignement


# ---------- Récupération d'un enseignement par professeur et matière ----------
def get_by_professeur_and_matiere(db: Session, professeur_id: int, matiere_id: int) -> Optional[Enseignement]:
    """
    Récupère un enseignement par professeur_id et matiere_id.
    Utilisé pour vérifier si un professeur enseigne une matière donnée.
    """
    return db.query(Enseignement).filter(
        Enseignement.professeur_id == professeur_id,
        Enseignement.matiere_id == matiere_id
    ).first()


# ---------- Récupération des enseignements d'un professeur ----------
def get_by_professeur(db: Session, professeur_id: int) -> List[Enseignement]:
    """
    Récupère tous les enseignements d'un professeur.
    Utilisé pour obtenir toutes les matières enseignées par un professeur.
    """
    return db.query(Enseignement).filter(Enseignement.professeur_id == professeur_id).all()


# ---------- Récupération des enseignements d'une matière ----------
def get_by_matiere(db: Session, matiere_id: int) -> List[Enseignement]:
    """
    Récupère tous les enseignements d'une matière.
    Utilisé pour obtenir tous les professeurs qui enseignent une matière.
    """
    return db.query(Enseignement).filter(Enseignement.matiere_id == matiere_id).all()


# ---------- Récupération de tous les enseignements ----------
def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Enseignement]:
    """
    Récupère une liste paginée de tous les enseignements.
    """
    return db.query(Enseignement).offset(skip).limit(limit).all()


# ---------- Création d'un enseignement ----------
def create(db: Session, enseignement_data: dict) -> Enseignement:
    """
    Crée un nouvel enseignement.
    """
    nouvel_enseignement = Enseignement(**enseignement_data)
    db.add(nouvel_enseignement)
    db.commit()
    db.refresh(nouvel_enseignement)
    return nouvel_enseignement


# ---------- Suppression d'un enseignement ----------
def delete(db: Session, professeur_id: int, matiere_id: int, semestre: str) -> None:
    """
    Supprime un enseignement.
    """
    enseignement = db.query(Enseignement).filter(
        Enseignement.professeur_id == professeur_id,
        Enseignement.matiere_id == matiere_id,
        Enseignement.semestre == semestre
    ).first()

    if enseignement:
        db.delete(enseignement)
        db.commit()
    return None

# ---------- Récupération d'un enseignement par ID ----------
def get_by_id(db: Session, enseignement_id: int) -> Optional[Enseignement]:
    """
    Récupère un enseignement par son ID.
    """
    return db.query(Enseignement).filter(Enseignement.id == enseignement_id).first()



def delete_by_id(db: Session, enseignement_id: int) -> None:
    """
    Supprime un enseignement par son ID.
    """
    enseignement = db.query(Enseignement).filter(Enseignement.id == enseignement_id).first()
    if enseignement:
        db.delete(enseignement)
        db.commit()
    return None

# ---------- Mise à jour d'un enseignement ----------
def update(db: Session, enseignement_id: int, enseignement_data: dict) -> Optional[Enseignement]:
    """
    Met à jour un enseignement existant.
    """
    enseignement = get_by_id(db, enseignement_id)
    if not enseignement:
        return None

    for key, value in enseignement_data.items():
        if value is not None:
            setattr(enseignement, key, value)

    db.commit()
    db.refresh(enseignement)
    return enseignement