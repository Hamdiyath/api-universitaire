from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class NoteBase(BaseModel):
    valeur: float = Field(..., ge=0, le=20)
    type_note: str = Field(..., min_length=2, max_length=20)
    semestre: str = Field(..., min_length=2, max_length=20)
    annee_universitaire: str = Field(..., min_length=4, max_length=20)
    commentaire: Optional[str] = Field(None, max_length=255)


class NoteCreate(NoteBase):
    etudiant_id: int
    matiere_id: int
    professeur_id: int


class NoteRead(NoteBase):
    id: int
    etudiant_id: int
    matiere_id: int
    professeur_id: int
    date_saisie: datetime

    class Config:
        from_attributes = True