
# schemas/resultat_semestre.py - Schémas Pydantic pour ResultatSemestre


from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ResultatSemestreBase(BaseModel):
    etudiant_id: int
    semestre: str = Field(..., min_length=2, max_length=20)
    annee_universitaire: str = Field(..., min_length=4, max_length=20)
    moyenne_semestre: float = Field(..., ge=0, le=20)
    statut: str = Field(..., min_length=2, max_length=20)
    a_passe_rattrapage: bool = False
    est_officiel: bool = False
    commentaire: Optional[str] = Field(None, max_length=255)


class ResultatSemestreCreate(ResultatSemestreBase):
    pass


class ResultatSemestreUpdate(BaseModel):
    moyenne_semestre: Optional[float] = Field(None, ge=0, le=20)
    statut: Optional[str] = Field(None, min_length=2, max_length=20)
    a_passe_rattrapage: Optional[bool] = None
    est_officiel: Optional[bool] = None
    commentaire: Optional[str] = Field(None, max_length=255)


class ResultatSemestreRead(ResultatSemestreBase):
    id: int
    date_calcul: datetime
    date_validation: Optional[datetime] = None

    class Config:
        from_attributes = True