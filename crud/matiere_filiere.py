# ============================================================
# crud/matiere_filiere.py - Opérations CRUD pour la table MatiereFiliere
# ============================================================

from typing import Optional, List
from sqlalchemy.orm import Session

from models.matiere_filiere import MatiereFiliere


# ---------- Récupération d'une association par ID (matiere_id, filiere_id, semestre) ----------
def get_by_id(
    db: Session,
    matiere_id: int,
    filiere_id: int,
    semestre: str
) -> Optional[MatiereFiliere]:
    """
    Récupère une association matière-filière par son ID composite.
    """
    return db.query(MatiereFiliere).filter(
        MatiereFiliere.matiere_id == matiere_id,
        MatiereFiliere.filiere_id == filiere_id,
        MatiereFiliere.semestre == semestre
    ).first()


# ---------- Récupération des associations par matière ----------
def get_by_matiere(db: Session, matiere_id: int) -> List[MatiereFiliere]:
    """
    Récupère toutes les associations d'une matière.
    """
    return db.query(MatiereFiliere).filter(MatiereFiliere.matiere_id == matiere_id).all()


# ---------- Récupération des associations par filière ----------
def get_by_filiere(db: Session, filiere_id: int) -> List[MatiereFiliere]:
    """
    Récupère toutes les associations d'une filière.
    """
    return db.query(MatiereFiliere).filter(MatiereFiliere.filiere_id == filiere_id).all()


# ---------- Récupération de toutes les associations ----------
def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[MatiereFiliere]:
    """
    Récupère une liste paginée de toutes les associations.
    """
    return db.query(MatiereFiliere).offset(skip).limit(limit).all()


# ---------- Création d'une association ----------
def create(db: Session, matiere_filiere_data: dict) -> MatiereFiliere:
    """
    Crée une nouvelle association matière-filière.
    """
    nouvelle_association = MatiereFiliere(**matiere_filiere_data)
    db.add(nouvelle_association)
    db.commit()
    db.refresh(nouvelle_association)
    return nouvelle_association


# ---------- Suppression d'une association ----------
def delete(
    db: Session,
    matiere_id: int,
    filiere_id: int,
    semestre: str
) -> None:
    """
    Supprime une association matière-filière.
    """
    association = get_by_id(db, matiere_id, filiere_id, semestre)
    if association:
        db.delete(association)
        db.commit()
    return None