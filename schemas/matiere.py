from pydantic import BaseModel, Field
from typing import Optional


class MatiereBase(BaseModel):
    code: str = Field(..., min_length=3, max_length=20)
    nom: str = Field(..., min_length=2, max_length=100)
    credits: int = Field(..., gt=0)
    semestre: str = Field(..., min_length=2, max_length=20)
    niveau: str = Field(..., min_length=2, max_length=20)


class MatiereCreate(MatiereBase):
    pass

class MatiereUpdate(BaseModel):
    """Données requises pour mettre à jour une matiere (tous les champs sont optionnels)"""
    nom: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=255)



class MatiereRead(MatiereBase):
    id: int

    class Config:
        from_attributes = True