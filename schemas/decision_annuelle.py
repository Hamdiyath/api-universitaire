
# schemas/decision_annuelle.py - Schémas Pydantic pour DecisionAnnuelle
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.decision_annuelle import DecisionPassage


class DecisionAnnuelleRead(BaseModel):
    """Données retournées par l'API"""
    id: int
    etudiant_id: int
    annee_universitaire: str
    credits_valides: int
    credits_total: int
    decision: DecisionPassage
    date_decision: datetime
    commentaire: Optional[str] = None

    class Config:
        from_attributes = True


class DecisionAnnuelleUpdate(BaseModel):
    """
    Correction manuelle d'une décision annuelle déjà actée.
    Réservé à l'Admin, pour corriger une erreur de jury.
    """
    credits_valides: Optional[int] = None
    decision: Optional[DecisionPassage] = None
    commentaire: Optional[str] = Field(None, max_length=255)