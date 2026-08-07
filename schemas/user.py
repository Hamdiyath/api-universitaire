# ============================================================
# schemas/user.py - Schémas Pydantic pour User
# ============================================================

from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import date, datetime
from typing import Optional, List, Any


class UserBase(BaseModel):
    """Attributs communs à tous les schémas User"""
    email: EmailStr
    nom: str = Field(..., min_length=2, max_length=100)
    prenom: str = Field(..., min_length=2, max_length=100)
    date_naissance: Optional[date] = None
    telephone: Optional[str] = Field(None, max_length=20)
    adresse: Optional[str] = Field(None, max_length=255)
    photo: Optional[str] = Field(None, max_length=255)
    matricule: Optional[str] = Field(None, max_length=50)
    specialite: Optional[str] = Field(None, max_length=255)


class UserCreate(BaseModel):
    """
    Données requises pour créer un compte (par Admin/Scolarité).
    Le mot de passe n'est pas inclus, il sera défini lors de l'activation.
    """
    email: EmailStr
    nom: str = Field(..., min_length=2, max_length=100)
    prenom: str = Field(..., min_length=2, max_length=100)
    date_naissance: Optional[date] = None
    telephone: Optional[str] = Field(None, max_length=20)
    adresse: Optional[str] = Field(None, max_length=255)
    photo: Optional[str] = Field(None, max_length=255)
    matricule: Optional[str] = Field(None, max_length=50)
    specialite: Optional[str] = Field(None, max_length=255)
    role_name: str = Field(..., min_length=2, max_length=50, description="Nom du rôle (ex: etudiant, professeur, admin, scolarite)")


# ---------- UNE SEULE DÉFINITION DE UserRead ----------
class UserRead(UserBase):
    """Données retournées par l'API (sans le mot de passe)"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    roles: Optional[List[str]] = []

    class UserRead(UserBase):
        id: int
        is_active: bool
        created_at: datetime
        updated_at: datetime
        roles: Optional[List[str]] = []
        activation_token: Optional[str] = None  # ← DOIT ÊTRE PRÉSENT


    class Config:
        from_attributes = True

    @field_validator('roles', mode='before')
    @classmethod
    def transform_roles(cls, v: Any) -> List[str]:
        if isinstance(v, list):
            return [item.name if hasattr(item, 'name') else str(item) for item in v]
        return v


class UserUpdate(BaseModel):
    """
    Champs modifiables par Admin/Scolarité.
    Permet la modification complète d'un compte utilisateur.
    """
    email: Optional[EmailStr] = None
    nom: Optional[str] = Field(None, min_length=2, max_length=100)
    prenom: Optional[str] = Field(None, min_length=2, max_length=100)
    date_naissance: Optional[date] = None
    telephone: Optional[str] = Field(None, max_length=20)
    adresse: Optional[str] = Field(None, max_length=255)
    photo: Optional[str] = Field(None, max_length=255)
    matricule: Optional[str] = Field(None, max_length=50)
    specialite: Optional[str] = Field(None, max_length=255)
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class UserUpdateSelf(BaseModel):
    """
    Champs qu'un utilisateur peut modifier sur son propre profil.
    Les champs officiels (nom, prenom, email, matricule, specialite) sont protégés.
    """
    telephone: Optional[str] = Field(None, max_length=20)
    adresse: Optional[str] = Field(None, max_length=255)
    photo: Optional[str] = Field(None, max_length=255)


class UserActivate(BaseModel):
    """
    Données pour l'activation du compte (définition du mot de passe).
    Le token est passé dans l'URL, pas dans le body.
    """
    password: str = Field(..., min_length=8, max_length=128)
    password_confirm: str = Field(..., min_length=8, max_length=128)


class UserLogin(BaseModel):
    """Données requises pour l'authentification"""
    email: EmailStr
    password: str