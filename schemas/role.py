
from pydantic import BaseModel, Field
from typing import Optional

# ---------- Schéma de base ----------
class RoleBase(BaseModel):
    """Attributs communs à tous les schémas Role"""
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=255)


# ---------- Schéma pour la CRÉATION ----------
class RoleCreate(RoleBase):
    """Données requises pour créer un rôle"""
    pass


# ---------- Schéma pour la LECTURE ----------
class RoleRead(RoleBase):
    """Données retournées par l'API"""
    id: int

    class Config:
        from_attributes = True