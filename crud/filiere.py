# ============================================================
# crud/filiere.py - Opérations CRUD pour la table Filiere
# ============================================================

from typing import Optional, List
from sqlalchemy.orm import Session

from models.filiere import Filiere


# ---------- Récupération par ID ----------
def get_by_id(db: Session, filiere_id: int) -> Optional[Filiere]:
    """
    Récupère une filière par son ID.
    """
    return db.query(Filiere).filter(Filiere.id == filiere_id).first()


# ---------- Récupération par nom ----------
def get_by_nom(db: Session, nom: str) -> Optional[Filiere]:
    """
    Récupère une filière par son nom.
    """
    return db.query(Filiere).filter(Filiere.nom == nom).first()


# ---------- Récupération de toutes les filières ----------
def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Filiere]:
    """
    Récupère une liste paginée de filières.
    """
    return db.query(Filiere).offset(skip).limit(limit).all()


# ---------- Création d'une filière ----------
def create(db: Session, filiere_data: dict) -> Filiere:
    """
    Crée une nouvelle filière.
    """
    nouvelle_filiere = Filiere(**filiere_data)
    db.add(nouvelle_filiere)
    db.commit()
    db.refresh(nouvelle_filiere)
    return nouvelle_filiere


# ---------- Mise à jour d'une filière ----------
def update(db: Session, filiere_id: int, filiere_data: dict) -> Optional[Filiere]:
    """
    Met à jour une filière existante.
    """
    filiere = get_by_id(db, filiere_id)
    if not filiere:
        return None

    for key, value in filiere_data.items():
        if value is not None:
            setattr(filiere, key, value)

    db.commit()
    db.refresh(filiere)
    return filiere


# ---------- Suppression d'une filière ----------
def delete(db: Session, filiere_id: int) -> bool:
    """
    Supprime une filière.
    """
    filiere = get_by_id(db, filiere_id)
    if not filiere:
        return False

    db.delete(filiere)
    db.commit()
    return True