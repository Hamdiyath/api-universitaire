
# crud/matiere.py - Opérations CRUD pour la table Matiere


from typing import Optional, List
from sqlalchemy.orm import Session

from models.matiere import Matiere


# ---------- Récupération par ID ----------
def get_by_id(db: Session, matiere_id: int) -> Optional[Matiere]:
    """
    Récupère une matière par son ID.
    """
    return db.query(Matiere).filter(Matiere.id == matiere_id).first()


# ---------- Récupération par nom ----------
def get_by_nom(db: Session, nom: str) -> Optional[Matiere]:
    """
    Récupère une matière par son nom.
    """
    return db.query(Matiere).filter(Matiere.nom == nom).first()


# ---------- Récupération de toutes les matières ----------
def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Matiere]:
    """
    Récupère une liste paginée de matières.
    """
    return db.query(Matiere).offset(skip).limit(limit).all()


# ---------- Création d'une matière ----------
def create(db: Session, matiere_data: dict) -> Matiere:
    """
    Crée une nouvelle matière.
    """
    nouvelle_matiere = Matiere(**matiere_data)
    db.add(nouvelle_matiere)
    db.commit()
    db.refresh(nouvelle_matiere)
    return nouvelle_matiere


# ---------- Mise à jour d'une matière ----------
def update(db: Session, matiere_id: int, matiere_data: dict) -> Optional[Matiere]:
    """
    Met à jour une matière existante.
    """
    matiere = get_by_id(db, matiere_id)
    if not matiere:
        return None

    for key, value in matiere_data.items():
        if value is not None:
            setattr(matiere, key, value)

    db.commit()
    db.refresh(matiere)
    return matiere


# ---------- Suppression d'une matière ----------
def delete(db: Session, matiere_id: int) -> None:
    """
    Supprime une matière.
    """
    matiere = get_by_id(db, matiere_id)
    if not matiere:
        return None

    db.delete(matiere)
    db.commit()
    return None

