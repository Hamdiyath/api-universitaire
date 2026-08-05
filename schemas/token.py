from pydantic import BaseModel
from typing import Optional
# ---------- Schéma pour le TOKEN JWT ----------
class Token(BaseModel):
    """Réponse après authentification"""
    access_token: str
    token_type: str = "bearer"


# ---------- Schéma pour les données du token ----------
class TokenData(BaseModel):
    """Contenu du token JWT"""
    user_id: Optional[int] = None
    email: Optional[str] = None
    roles: Optional[list[str]] = []