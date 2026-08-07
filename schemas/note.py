from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.enums import SessionNote


class NoteBase(BaseModel):
    valeur: float = Field(..., ge=0, le=20)
    type_note: str = Field(..., min_length=2, max_length=20)
    semestre: str = Field(..., min_length=2, max_length=20)
    annee_universitaire: str = Field(..., min_length=4, max_length=20)
    commentaire: Optional[str] = Field(None, max_length=255)
    coefficient: float = Field(1.0, ge=0.5, le=5.0)
    session: SessionNote = SessionNote.NORMALE  # ← AJOUT


class NoteCreate(NoteBase):
    etudiant_id: int
    matiere_id: int
    professeur_id: int


class NoteUpdate(BaseModel):
    """Données requises pour mettre à jour une note (tous les champs sont optionnels)"""
    valeur: Optional[float] = Field(None, ge=0, le=20)
    type_note: Optional[str] = Field(None, min_length=2, max_length=20)
    semestre: Optional[str] = Field(None, min_length=2, max_length=20)
    annee_universitaire: Optional[str] = Field(None, min_length=4, max_length=20)
    commentaire: Optional[str] = Field(None, max_length=255)
    coefficient: Optional[float] = Field(None, ge=0.5, le=5.0)
    session: Optional[SessionNote] = None  # ← AJOUT


class NoteRead(NoteBase):
    id: int
    etudiant_id: int
    matiere_id: int
    professeur_id: int
    date_saisie: datetime

    class Config:
        from_attributes = True