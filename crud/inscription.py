# crud/inscription.py - Opérations CRUD pour la table Inscription
from typing import Optional, List
from sqlalchemy.orm import Session
from models.inscription import Inscription


# ---------- Récupération par ID ----------
def get_by_id(db: Session, inscription_id: int) -> Optional[Inscription]:
    """
    Récupère une inscription par son ID.
    """
    return db.query(Inscription).filter(Inscription.id == inscription_id).first()


# ---------- Récupération des inscriptions d'un étudiant ----------
def get_by_etudiant(db: Session, etudiant_id: int) -> List[Inscription]:
    """
    Récupère toutes les inscriptions d'un étudiant.
    """
    return db.query(Inscription).filter(Inscription.etudiant_id == etudiant_id).all()


# ---------- Récupération des inscriptions d'une matière ----------
def get_by_matiere(db: Session, matiere_id: int) -> List[Inscription]:
    """
    Récupère toutes les inscriptions d'une matière.
    """
    return db.query(Inscription).filter(Inscription.matiere_id == matiere_id).all()


# ---------- Vérification d'existence exacte (doublon strict) ----------
def get_by_etudiant_matiere_semestre_annee(
    db: Session,
    etudiant_id: int,
    matiere_id: int,
    semestre: str,
    annee_universitaire: str
) -> Optional[Inscription]:
    """
    Vérifie si une inscription exacte existe déjà (même étudiant, matière,
    semestre ET année universitaire). Utilisé pour empêcher les vrais doublons
    tout en permettant à un redoublant de se réinscrire une autre année.
    """
    return db.query(Inscription).filter(
        Inscription.etudiant_id == etudiant_id,
        Inscription.matiere_id == matiere_id,
        Inscription.semestre == semestre,
        Inscription.annee_universitaire == annee_universitaire
    ).first()


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


# ---------- Mise à jour d'une inscription ----------
def update(db: Session, inscription_id: int, update_data: dict) -> Optional[Inscription]:
    """
    Met à jour une inscription existante.
    """
    inscription = get_by_id(db, inscription_id)
    if not inscription:
        return None
    for key, value in update_data.items():
        if value is not None:
            setattr(inscription, key, value)
    db.commit()
    db.refresh(inscription)
    return inscription


# ---------- Suppression d'une inscription ----------
def delete(db: Session, inscription_id: int) -> None:
    """
    Supprime une inscription par son ID.
    """
    inscription = get_by_id(db, inscription_id)
    if not inscription:
        return None
    db.delete(inscription)
    db.commit()
    return None