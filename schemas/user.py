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
    filiere_id: Optional[int] = None


class UserCreate(BaseModel):
    """
    Données requises pour créer un compte (par Admin/Scolarité).
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
    filiere_id: Optional[int] = None


class UserRead(UserBase):
    """Données retournées par l'API (sans le mot de passe)"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    roles: Optional[List[str]] = []

    class Config:
        from_attributes = True

    @field_validator('roles', mode='before')
    @classmethod
    def transform_roles(cls, v: Any) -> List[str]:
        """Transforme une liste d'objets Role en liste de noms"""
        if v is None:
            return []
        if isinstance(v, list):
            result = []
            for item in v:
                if hasattr(item, 'name'):
                    result.append(item.name)
                elif isinstance(item, str):
                    result.append(item)
            return result
        return []


class UserUpdate(BaseModel):
    """Champs modifiables par Admin/Scolarité"""
    email: Optional[EmailStr] = None
    nom: Optional[str] = Field(None, min_length=2, max_length=100)
    prenom: Optional[str] = Field(None, min_length=2, max_length=100)
    date_naissance: Optional[date] = None
    telephone: Optional[str] = Field(None, max_length=20)
    adresse: Optional[str] = Field(None, max_length=255)
    photo: Optional[str] = Field(None, max_length=255)
    matricule: Optional[str] = Field(None, max_length=50)
    specialite: Optional[str] = Field(None, max_length=255)
    filiere_id: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class UserUpdateSelf(BaseModel):
    """Champs qu'un utilisateur peut modifier sur son propre profil"""
    telephone: Optional[str] = Field(None, max_length=20)
    adresse: Optional[str] = Field(None, max_length=255)
    photo: Optional[str] = Field(None, max_length=255)


class UserActivate(BaseModel):
    """Données pour l'activation du compte (définition du mot de passe)"""
    password: str = Field(..., min_length=8, max_length=128)
    password_confirm: str = Field(..., min_length=8, max_length=128)


class UserLogin(BaseModel):
    """Données requises pour l'authentification"""
    email: EmailStr
    password: str


class UserReadAdmin(UserBase):
    """Données retournées à l'admin (avec token d'activation)"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    roles: Optional[List[str]] = []
    activation_token: Optional[str] = None

    class Config:
        from_attributes = True

    @field_validator('roles', mode='before')
    @classmethod
    def transform_roles_admin(cls, v: Any) -> List[str]:
        """Transforme une liste d'objets Role en liste de noms"""
        if v is None:
            return []
        if isinstance(v, list):
            result = []
            for item in v:
                if hasattr(item, 'name'):
                    result.append(item.name)
                elif isinstance(item, str):
                    result.append(item)
            return result
        return []