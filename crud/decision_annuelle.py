# crud/decision_annuelle.py - Opérations CRUD pour DecisionAnnuelle

from typing import Optional, List
from sqlalchemy.orm import Session
from models.decision_annuelle import DecisionAnnuelle


def get_by_id(db: Session, decision_id: int) -> Optional[DecisionAnnuelle]:
    """Récupère une décision annuelle par son ID."""
    return db.query(DecisionAnnuelle).filter(DecisionAnnuelle.id == decision_id).first()


def get_by_etudiant_annee(db: Session, etudiant_id: int, annee_universitaire: str) -> Optional[DecisionAnnuelle]:
    """Récupère la décision annuelle d'un étudiant pour une année donnée."""
    return db.query(DecisionAnnuelle).filter(
        DecisionAnnuelle.etudiant_id == etudiant_id,
        DecisionAnnuelle.annee_universitaire == annee_universitaire
    ).first()


def get_by_etudiant(db: Session, etudiant_id: int) -> List[DecisionAnnuelle]:
    """Récupère toutes les décisions annuelles d'un étudiant (historique complet)."""
    return db.query(DecisionAnnuelle).filter(DecisionAnnuelle.etudiant_id == etudiant_id).all()


def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[DecisionAnnuelle]:
    """Récupère une liste paginée de toutes les décisions annuelles."""
    return db.query(DecisionAnnuelle).offset(skip).limit(limit).all()


def create(db: Session, decision_data: dict) -> DecisionAnnuelle:
    """Crée une nouvelle décision annuelle."""
    nouvelle_decision = DecisionAnnuelle(**decision_data)
    db.add(nouvelle_decision)
    db.commit()
    db.refresh(nouvelle_decision)
    return nouvelle_decision


def update(db: Session, decision_id: int, update_data: dict) -> Optional[DecisionAnnuelle]:
    """Met à jour une décision annuelle existante (correction manuelle)."""
    decision = get_by_id(db, decision_id)
    if not decision:
        return None
    for key, value in update_data.items():
        if value is not None:
            setattr(decision, key, value)
    db.commit()
    db.refresh(decision)
    return decision