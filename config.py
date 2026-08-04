#configuration de la base de donnee et des settings
#ici on declare les potentiels variable qui pourrait change selon ou tourne l'app
#(local, serveur, test) et qu'on ne veut pas avoir en dur dans le code
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    # ---------- Configuration de l'API ----------
    app_name: str = "API Universitaire"
    app_description: str = "API de gestion de la scolarité"
    app_version: str = "1.0.0"
    debug: bool = False  # Mode debug (True en développement)

    # ---------- Base de données ----------
    database_url: str = Field(..., description="URL de connexion à la base de données")
    # Le '...' signifie que le champ est obligatoire

    # ---------- Authentification JWT ----------
    secret_key: str = Field(..., description="Clé secrète pour JWT (min 32 caractères)")
    algorithm: str = Field(default="HS256", description="Algorithme JWT")
    access_token_expire_minutes: int = Field(
        default=30,
        description="Durée de validité du token en minutes",
        gt=0  # Doit être > 0
    )

    # ---------- Configuration du fichier .env ----------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # Les noms de variables sont insensibles à la casse
        extra="ignore",  # Ignore les variables inconnues dans .env
    )

    # ---------- Validateurs personnalisés ----------
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Vérifie que la clé secrète a au moins 32 caractères."""
        if len(v) < 32:
            raise ValueError("SECRET_KEY doit faire au moins 32 caractères")
        return v

#optionnel on pourra le supprimer si on le souhaite
    @field_validator("access_token_expire_minutes")
    @classmethod
    def validate_token_expiry(cls, v: int) -> int:
        """Vérifie que la durée du token est positive."""
        if v <= 0:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES doit être > 0")
        return v


# ---------- Instance globale des settings ----------
# Cette instance est importée dans toute l'application
settings = Settings()
