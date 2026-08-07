# ============================================================
# crud/note.py - Opérations CRUD pour la table Note
# ============================================================

from typing import Optional, List
from sqlalchemy.orm import Session

from models.note import Note


# ---------- Récupération d'une note par son ID ----------
def get_by_id(db: Session, note_id: int) -> Optional[Note]:
    """
    Récupère une note par son ID.
    """
    return db.query(Note).filter(Note.id == note_id).first()


# ---------- Récupération des notes d'un étudiant ----------
def get_by_etudiant(db: Session, etudiant_id: int, skip: int = 0, limit: int = 100) -> List[Note]:
    """
    Récupère toutes les notes d'un étudiant (paginé).
    """
    return db.query(Note).filter(Note.etudiant_id == etudiant_id).offset(skip).limit(limit).all()


# ---------- Récupération des notes d'une matière ----------
def get_by_matiere(db: Session, matiere_id: int, skip: int = 0, limit: int = 100) -> List[Note]:
    """
    Récupère toutes les notes d'une matière (paginé).
    """
    return db.query(Note).filter(Note.matiere_id == matiere_id).offset(skip).limit(limit).all()


# ---------- Récupération des notes saisies par un professeur ----------
def get_by_professeur(db: Session, professeur_id: int, skip: int = 0, limit: int = 100) -> List[Note]:
    """
    Récupère toutes les notes saisies par un professeur (paginé).
    """
    return db.query(Note).filter(Note.professeur_id == professeur_id).offset(skip).limit(limit).all()


# ---------- Récupération de toutes les notes ----------
def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Note]:
    """
    Récupère une liste paginée de toutes les notes.
    """
    return db.query(Note).offset(skip).limit(limit).all()


# ---------- Création d'une note ----------
def create(db: Session, note_data: dict) -> Note:
    """
    Crée une nouvelle note.
    """
    nouvelle_note = Note(**note_data)
    db.add(nouvelle_note)
    db.commit()
    db.refresh(nouvelle_note)
    return nouvelle_note


# ---------- Mise à jour d'une note ----------
def update(db: Session, note_id: int, note_data: dict) -> Optional[Note]:
    """
    Met à jour une note existante.
    """
    note = get_by_id(db, note_id)
    if not note:
        return None

    for key, value in note_data.items():
        if value is not None:
            setattr(note, key, value)

    db.commit()
    db.refresh(note)
    return note


# ---------- Suppression d'une note ----------
def delete(db: Session, note_id: int) -> None:
    """
    Supprime une note.
    """
    note = get_by_id(db, note_id)
    if not note:
        return None

    db.delete(note)
    db.commit()
    return None


# ---------- Récupération des notes d'un étudiant pour une matière ----------
def get_by_etudiant_and_matiere(db: Session, etudiant_id: int, matiere_id: int) -> List[Note]:
    """
    Récupère toutes les notes d'un étudiant pour une matière donnée.
    """
    return db.query(Note).filter(
        Note.etudiant_id == etudiant_id,
        Note.matiere_id == matiere_id
    ).all()