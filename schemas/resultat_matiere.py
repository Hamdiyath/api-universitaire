
# schemas/resultat_matiere.py - Schémas Pydantic pour ResultatMatiere
from pydantic import BaseModel, Field
from typing import Optional
from models.enums import SessionNote, StatutValidation


class ResultatMatiereBase(BaseModel):
    """Attributs communs à tous les schémas ResultatMatiere"""
    etudiant_id: int
    matiere_id: int
    semestre: str = Field(..., min_length=2, max_length=20)
    annee_universitaire: str = Field(..., min_length=4, max_length=20)


class ResultatMatiereCreate(ResultatMatiereBase):
    """
       Données requises pour générer une ligne de résultat.
       Utilisé par un mécanisme de génération en bloc (démarrage de semestre
       pour une filière, ou génération initiale après création d'un compte
       étudiant) — jamais saisi manuellement note par note.
       Moyenne et statut prennent leurs valeurs par défaut (None / NON_NOTE).
       """
    session_actuelle: SessionNote = SessionNote.NORMALE


class ResultatMatiereRead(ResultatMatiereBase):
    """Données retournées par l'API"""
    id: int
    moyenne: Optional[float] = None
    session_actuelle: SessionNote
    statut: StatutValidation

    class Config:
        from_attributes = True


class ResultatMatiereUpdate(BaseModel):
    """
    Champs modifiables sur une ligne de résultat.
    Utilisé en interne par la synchronisation (BulletinService) pour
    mettre à jour moyenne/statut après chaque saisie de note.
    """
    moyenne: Optional[float] = None
    session_actuelle: Optional[SessionNote] = None
    statut: Optional[StatutValidation] = None