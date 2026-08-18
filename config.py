
# config.py - Configuration de l'application


from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    # ---------- Configuration de l'API ----------
    app_name: str = "API Universitaire"
    app_description: str = "API de gestion de la scolarité"
    app_version: str = "1.0.0"
    debug: bool = False

    # ---------- Base de données ----------
    database_url: str = Field(..., description="URL de connexion à la base de données")

    # ---------- Authentification JWT ----------
    secret_key: str = Field(..., description="Clé secrète pour JWT (min 32 caractères)")
    algorithm: str = Field(default="HS256", description="Algorithme JWT")
    access_token_expire_minutes: int = Field(
        default=30,
        description="Durée de validité du token en minutes",
        gt=0
    )

    # ---------- Configuration email (Mailtrap) ----------
    mail_host: str = Field(..., description="Hôte SMTP (ex: sandbox.smtp.mailtrap.io)")
    mail_port: int = Field(..., description="Port SMTP (ex: 2525, 587)")
    mail_username: str = Field(..., description="Nom d'utilisateur SMTP")
    mail_password: str = Field(..., description="Mot de passe SMTP")
    mail_from: str = Field(..., description="Email de l'expéditeur (ex: noreply@univ.com)")
    mail_tls: bool = Field(default=True, description="Activer TLS pour la connexion SMTP")

    # ---------- Configuration du fichier .env ----------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---------- Validateurs personnalisés ----------
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY doit faire au moins 32 caractères")
        return v

    @field_validator("access_token_expire_minutes")
    @classmethod
    def validate_token_expiry(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES doit être > 0")
        return v


# ---------- Instance globale ----------
settings = Settings()