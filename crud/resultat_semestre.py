# ============================================================
# crud/resultat_semestre.py - Opérations CRUD pour ResultatSemestre
# ============================================================

from typing import Optional, List
from sqlalchemy.orm import Session

from models.resultat_semestre import ResultatSemestre


def get_by_etudiant(db: Session, etudiant_id: int) -> List[ResultatSemestre]:
    """Récupère tous les résultats d'un étudiant"""
    return db.query(ResultatSemestre).filter(ResultatSemestre.etudiant_id == etudiant_id).all()


def get_by_etudiant_semestre(
    db: Session,
    etudiant_id: int,
    semestre: str,
    annee_universitaire: str
) -> Optional[ResultatSemestre]:
    """Récupère le résultat d'un étudiant pour un semestre donné"""
    return db.query(ResultatSemestre).filter(
        ResultatSemestre.etudiant_id == etudiant_id,
        ResultatSemestre.semestre == semestre,
        ResultatSemestre.annee_universitaire == annee_universitaire
    ).first()


def create(db: Session, resultat_data: dict) -> ResultatSemestre:
    """Crée un résultat semestriel"""
    nouveau_resultat = ResultatSemestre(**resultat_data)
    db.add(nouveau_resultat)
    db.commit()
    db.refresh(nouveau_resultat)
    return nouveau_resultat


def update(db: Session, resultat_id: int, resultat_data: dict) -> Optional[ResultatSemestre]:
    """Met à jour un résultat semestriel"""
    resultat = db.query(ResultatSemestre).filter(ResultatSemestre.id == resultat_id).first()
    if not resultat:
        return None

    for key, value in resultat_data.items():
        if value is not None:
            setattr(resultat, key, value)

    db.commit()
    db.refresh(resultat)
    return resultat