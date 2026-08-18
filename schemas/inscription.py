# schemas/inscription.py - Schémas Pydantic pour Inscription
from pydantic import BaseModel, Field
from models.enums import TypeInscription
from typing import Optional

class InscriptionBase(BaseModel):
    """Attributs communs à tous les schémas Inscription"""
    etudiant_id: int
    matiere_id: int
    semestre: str = Field(..., min_length=2, max_length=20)
    annee_universitaire: str = Field(..., min_length=4, max_length=20)
    type_inscription: TypeInscription = TypeInscription.NORMALE


class InscriptionCreate(InscriptionBase):
    """Données requises pour créer une inscription"""
    pass


class InscriptionRead(InscriptionBase):
    """Données retournées par l'API"""
    id: int

class InscriptionUpdate(BaseModel):
    """
    Champs modifiables sur une inscription existante.
    etudiant_id n'est jamais modifiable : pour changer d'étudiant,
    il faut supprimer l'inscription et en créer une nouvelle.
    """
    matiere_id: Optional[int] = None
    semestre: Optional[str] = Field(None, min_length=2, max_length=20)
    annee_universitaire: Optional[str] = Field(None, min_length=4, max_length=20)
    type_inscription: Optional[TypeInscription] = None

class Config:
    from_attributes = True