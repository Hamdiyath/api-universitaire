
from pydantic import BaseModel, Field
from typing import Optional


class FiliereBase(BaseModel):
    """Attributs communs à tous les schémas Filiere"""
    nom: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=255)


class FiliereCreate(FiliereBase):
    """Données requises pour créer une filière"""
    pass


class FiliereRead(FiliereBase):
    """Données retournées par l'API"""
    id: int

    class Config:
        from_attributes = True