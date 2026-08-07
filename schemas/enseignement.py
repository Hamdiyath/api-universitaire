# ============================================================
# schemas/enseignement.py - Schémas Pydantic pour Enseignement
# ============================================================

from pydantic import BaseModel, Field


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
    class Config:
        from_attributes = True