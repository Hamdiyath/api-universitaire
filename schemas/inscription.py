
# schemas/inscription.py - Schémas Pydantic pour Inscription


from pydantic import BaseModel, Field


class InscriptionBase(BaseModel):
    """Attributs communs à tous les schémas Inscription"""
    etudiant_id: int
    matiere_id: int
    semestre: str = Field(..., min_length=2, max_length=20)
    annee_universitaire: str = Field(..., min_length=4, max_length=20)


class InscriptionCreate(InscriptionBase):
    """Données requises pour créer une inscription"""
    pass


class InscriptionRead(InscriptionBase):
    """Données retournées par l'API"""
    class Config:
        from_attributes = True