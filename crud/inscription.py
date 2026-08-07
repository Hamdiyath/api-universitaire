# ============================================================
# crud/inscription.py - Opérations CRUD pour la table Inscription
# ============================================================

from typing import Optional, List
from sqlalchemy.orm import Session

from models.inscription import Inscription


# ---------- Récupération des inscriptions d'un étudiant ----------
def get_by_etudiant(db: Session, etudiant_id: int) -> List[Inscription]:
    """
    Récupère toutes les inscriptions d'un étudiant.
    Utilisé pour obtenir toutes les matières suivies par un étudiant.
    """
    return db.query(Inscription).filter(Inscription.etudiant_id == etudiant_id).all()


# ---------- Récupération des inscriptions d'une matière ----------
def get_by_matiere(db: Session, matiere_id: int) -> List[Inscription]:
    """
    Récupère toutes les inscriptions d'une matière.
    Utilisé pour obtenir tous les étudiants inscrits à une matière.
    """
    return db.query(Inscription).filter(Inscription.matiere_id == matiere_id).all()


# ---------- Vérification si un étudiant est inscrit à des matières spécifiques ----------
def get_by_etudiant_and_matieres(db: Session, etudiant_id: int, matiere_ids: List[int]) -> List[Inscription]:
    """
    Récupère les inscriptions d'un étudiant pour une liste de matières.
    Utilisé pour vérifier si un étudiant est inscrit à au moins une des matières enseignées par un professeur.
    """
    return db.query(Inscription).filter(
        Inscription.etudiant_id == etudiant_id,
        Inscription.matiere_id.in_(matiere_ids)
    ).all()


# ---------- Récupération de toutes les inscriptions ----------
def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Inscription]:
    """
    Récupère une liste paginée de toutes les inscriptions.
    """
    return db.query(Inscription).offset(skip).limit(limit).all()


# ---------- Création d'une inscription ----------
def create(db: Session, inscription_data: dict) -> Inscription:
    """
    Crée une nouvelle inscription.
    """
    nouvelle_inscription = Inscription(**inscription_data)
    db.add(nouvelle_inscription)
    db.commit()
    db.refresh(nouvelle_inscription)
    return nouvelle_inscription


# ---------- Suppression d'une inscription ----------
def delete(db: Session, etudiant_id: int, matiere_id: int, semestre: str) -> None:
    """
    Supprime une inscription.
    """
    inscription = db.query(Inscription).filter(
        Inscription.etudiant_id == etudiant_id,
        Inscription.matiere_id == matiere_id,
        Inscription.semestre == semestre
    ).first()

    if inscription:
        db.delete(inscription)
        db.commit()
    return None