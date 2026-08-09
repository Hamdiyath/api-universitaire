# ============================================================
# schemas/enseignement.py - Schémas Pydantic pour Enseignement
# ============================================================

from pydantic import BaseModel, Field
from typing import Optional


class EnseignementBase(BaseModel):
    """Attributs communs à tous les schémas Enseignement"""
    professeur_id: int
    matiere_id: int
    semestre: str = Field(..., min_length=2, max_length=20)
    annee_universitaire: str = Field(..., min_length=4, max_length=20)


class EnseignementCreate(EnseignementBase):
    """Données requises pour créer un enseignement"""
    pass


class EnseignementRead(EnseignementBase):
    """Données retournées par l'API"""
    id: int  # ← AJOUTER
    class Config:
        from_attributes = True


class EnseignementUpdate(BaseModel):
    professeur_id: Optional[int] = None
    matiere_id: Optional[int] = None
    semestre: Optional[str] = Field(None, min_length=2, max_length=20)
    annee_universitaire: Optional[str] = Field(None, min_length=4, max_length=20)