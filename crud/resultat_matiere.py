
# crud/resultat_matiere.py - Opérations CRUD pour ResultatMatier

from models.enums import StatutValidation
from typing import Optional, List
from sqlalchemy.orm import Session
from models.resultat_matiere import ResultatMatiere


# ---------- Récupération par ID ----------
def get_by_id(db: Session, resultat_id: int) -> Optional[ResultatMatiere]:
    """Récupère une ligne de résultat par son ID."""
    return db.query(ResultatMatiere).filter(ResultatMatiere.id == resultat_id).first()


# ---------- Récupération exacte (étudiant + matière + semestre + année) ----------
def get_by_etudiant_matiere_semestre_annee(
    db: Session,
    etudiant_id: int,
    matiere_id: int,
    semestre: str,
    annee_universitaire: str
) -> Optional[ResultatMatiere]:
    """
    Récupère la ligne de résultat exacte pour un étudiant, une matière,
    un semestre et une année donnés. Utilisé pour la synchronisation
    après saisie de note, et pour éviter les doublons à la génération.
    """
    return db.query(ResultatMatiere).filter(
        ResultatMatiere.etudiant_id == etudiant_id,
        ResultatMatiere.matiere_id == matiere_id,
        ResultatMatiere.semestre == semestre,
        ResultatMatiere.annee_universitaire == annee_universitaire
    ).first()


# ---------- Récupération de toutes les lignes d'un étudiant ----------
def get_by_etudiant(db: Session, etudiant_id: int) -> List[ResultatMatiere]:
    """Récupère toutes les lignes de résultat d'un étudiant, toutes années confondues."""
    return db.query(ResultatMatiere).filter(ResultatMatiere.etudiant_id == etudiant_id).all()


# ---------- Récupération des lignes d'un étudiant pour un semestre/année précis ----------
def get_by_etudiant_semestre_annee(
    db: Session,
    etudiant_id: int,
    semestre: str,
    annee_universitaire: str
) -> List[ResultatMatiere]:
    """Récupère les lignes de résultat d'un étudiant pour un semestre et une année donnés."""
    return db.query(ResultatMatiere).filter(
        ResultatMatiere.etudiant_id == etudiant_id,
        ResultatMatiere.semestre == semestre,
        ResultatMatiere.annee_universitaire == annee_universitaire
    ).all()


# ---------- Récupération de toutes les lignes d'une matière ----------
def get_by_matiere(db: Session, matiere_id: int) -> List[ResultatMatiere]:
    """Récupère toutes les lignes de résultat pour une matière donnée."""
    return db.query(ResultatMatiere).filter(ResultatMatiere.matiere_id == matiere_id).all()


# ---------- Récupération des lignes en dette (non validées ou sans note) pour une période ----------
def get_dettes_by_semestre_annee(
    db: Session,
    semestre: str,
    annee_universitaire: str
) -> List[ResultatMatiere]:
    """
    Récupère toutes les lignes en dette (statut NON_VALIDE ou NON_NOTE)
    pour un semestre/année donné. Utilisé lors de la clôture d'année pour
    générer les lignes de reprise de l'année suivante.
    """
    return db.query(ResultatMatiere).filter(
        ResultatMatiere.semestre == semestre,
        ResultatMatiere.annee_universitaire == annee_universitaire,
        ResultatMatiere.statut.in_([StatutValidation.NON_VALIDE, StatutValidation.NON_NOTE])
    ).all()


# ---------- Récupération de toutes les lignes (paginé) ----------
def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[ResultatMatiere]:
    """Récupère une liste paginée de toutes les lignes de résultat."""
    return db.query(ResultatMatiere).offset(skip).limit(limit).all()


# ---------- Création d'une ligne ----------
def create(db: Session, resultat_data: dict) -> ResultatMatiere:
    """Crée une nouvelle ligne de résultat."""
    nouveau_resultat = ResultatMatiere(**resultat_data)
    db.add(nouveau_resultat)
    db.commit()
    db.refresh(nouveau_resultat)
    return nouveau_resultat


# ---------- Mise à jour d'une ligne ----------
def update(db: Session, resultat_id: int, update_data: dict) -> Optional[ResultatMatiere]:
    """Met à jour une ligne de résultat existante (utilisé par la synchronisation)."""
    resultat = get_by_id(db, resultat_id)
    if not resultat:
        return None
    for key, value in update_data.items():
        if value is not None:
            setattr(resultat, key, value)
    db.commit()
    db.refresh(resultat)
    return resultat


# ---------- Suppression d'une ligne ----------
def delete(db: Session, resultat_id: int) -> None:
    """Supprime une ligne de résultat par son ID."""
    resultat = get_by_id(db, resultat_id)
    if not resultat:
        return None
    db.delete(resultat)
    db.commit()
    return None