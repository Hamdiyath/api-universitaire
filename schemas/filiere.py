from pydantic import BaseModel, Field
from typing import Optional


class FiliereBase(BaseModel):
    """Attributs communs à tous les schémas Filiere"""
    nom: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=255)


class FiliereCreate(FiliereBase):
    """Données requises pour créer une filière"""
    pass


class FiliereUpdate(BaseModel):
    """Données requises pour mettre à jour une filière (tous les champs sont optionnels)"""
    nom: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=255)


class FiliereRead(FiliereBase):
    """Données retournées par l'API"""
    id: int

    class Config:
        from_attributes = True