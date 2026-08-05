from pydantic import BaseModel, Field, EmailStr
from datetime import   date , datetime
from typing import Optional
class UserBase(BaseModel):
    """Attributs communs à tous les schémas User"""
    email: EmailStr
    nom: str = Field(..., min_length=2, max_length=100)
    prenom: str = Field(..., min_length=2, max_length=100)
    date_naissance: Optional[date] = None
    telephone: Optional[str] = Field(None, max_length=20)
    matricule: Optional[str] = Field(None, max_length=50)
    specialite: Optional[str] = Field(None, max_length=255)
    statut: Optional[str] = "actif"

    # ---------- Schéma pour la CRÉATION (inscription) ----------
class UserCreate(UserBase):
    """Données requises pour créer un utilisateur"""
    password: str = Field(..., min_length=8, max_length=128)
    password_confirm: str = Field(..., min_length=8, max_length=128)

# ---------- Schéma pour la LECTURE ----------
class UserRead(UserBase):
    """Données retournées par l'API (sans le mot de passe)"""
    id: int
    created_at: datetime
    updated_at: datetime
    roles: Optional[list[str]] = []  # Liste des noms de rôles

    class Config:
        from_attributes = True

# ---------- Schéma pour la MISE À JOUR ----------
class UserUpdate(BaseModel):
    """Champs modifiables d'un utilisateur"""
    email: Optional[EmailStr] = None
    nom: Optional[str] = Field(None, min_length=2, max_length=100)
    prenom: Optional[str] = Field(None, min_length=2, max_length=100)
    date_naissance: Optional[date] = None
    telephone: Optional[str] = Field(None, max_length=20)
    matricule: Optional[str] = Field(None, max_length=50)
    specialite: Optional[str] = Field(None, max_length=255)
    statut: Optional[str] = None


# ---------- Schéma pour la CONNEXION (login) ----------
class UserLogin(BaseModel):
    """Données requises pour l'authentification"""
    email: EmailStr
    password: str

