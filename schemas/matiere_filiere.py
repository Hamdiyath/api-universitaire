from pydantic import BaseModel, Field


class MatiereFiliereBase(BaseModel):
    matiere_id: int
    filiere_id: int
    semestre: str = Field(..., min_length=2, max_length=20)


class MatiereFiliereCreate(MatiereFiliereBase):
    pass


class MatiereFiliereRead(MatiereFiliereBase):
    class Config:
        from_attributes = True