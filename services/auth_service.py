# ============================================================
# services/auth_service.py - Logique métier Authentification
# ============================================================

from sqlalchemy.orm import Session
import secrets
from datetime import datetime, timezone, timedelta

# Import des CRUDs sous un namespace propre
import crud.user as user_crud
import crud.role as role_crud

# Import des Schémas et Utilitaires de sécurité
from core.security import hash_password, verify_password, create_access_token
from schemas.user import UserCreate, UserActivate, UserLogin

# 1. PLUS D'HTTPEXCEPTION : On utilise vos alarmes personnalisées
from exceptions.base import (
    InvalidCredentialsError,
    AccountNotActivatedError,
    EmailAlreadyExistsError,
    RoleNotFoundError,
    PasswordsDoNotMatchError,  # Pensez à l'ajouter à base.py
    TokenNotFoundError,  # Pensez à l'ajouter à base.py
    TokenExpiredError,  # Pensez à l'ajouter à base.py
    AccountAlreadyActiveError
)


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    # ---------- Connexion & Génération du Token JWT ----------
    def login_and_generate_token(self, user_data: UserLogin) -> dict:
        """Valide les identifiants et retourne le token JWT d'une ligne."""
        user = user_crud.get_by_email(self.db, user_data.email)

        # Alarme : Email inexistant ou mot de passe invalide
        if not user or not verify_password(user_data.password, user.password_hash):
            raise InvalidCredentialsError()

        # Alarme : Compte créé par l'admin mais l'étudiant ne l'a pas activé
        if not user.is_active:
            raise AccountNotActivatedError()

        # Génération du token (La logique a migré ici !)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    # ---------- Vérification de validité d'un Token d'Activation ----------
    # Dans app/services/auth_service.py (Ligne 69)

    def check_token_validity(self, token: str):
        user = user_crud.get_by_activation_token(self.db, token)

        if not user:
            raise TokenNotFoundError()

        if user.is_active:
            raise AccountAlreadyActiveError()

        # CORRECTION : Comparaison naive vs naive
        if user.activation_token_expires and user.activation_token_expires < datetime.utcnow():
            raise TokenExpiredError()

        return user

    # ---------- Activation du compte ----------
    def activate_user_account(self, token: str, password_data: UserActivate):
        """Active le compte de l'étudiant/professeur."""
        # 1. Alarme : Faute de frappe dans la confirmation
        if password_data.password != password_data.password_confirm:
            raise PasswordsDoNotMatchError()

        # 2. Récupération et double validation temporelle du token via notre méthode interne
        user = self.check_token_validity(token)

        # 3. Hachage du mot de passe
        hashed_password = hash_password(password_data.password)

        # 4. Préparation et envoi de la mise à jour au CRUD
        update_data = {
            "password_hash": hashed_password,
            "is_active": True,
            "activation_token": None,
            "activation_token_expires": None
        }
        updated_user = user_crud.update(self.db, user.id, update_data)

        return updated_user

    # ---------- Créer un utilisateur (Admin/Scolarité) ----------
    def create_user_account(self, user_data: UserCreate, role_name: str):
        """Inscrit un nouvel utilisateur en attente d'activation."""
        if user_crud.get_by_email(self.db, user_data.email):
            raise EmailAlreadyExistsError(user_data.email)

        role_obj = role_crud.get_by_name(self.db, role_name)
        if not role_obj:
            raise RoleNotFoundError(role_name)

        # Génération du jeton d'activation valable 24h
        activation_token = secrets.token_urlsafe(32)
        activation_token_expires = datetime.now(timezone.utc) + timedelta(hours=24)

        user_dict = user_data.model_dump()
        user_dict["password_hash"] = None
        user_dict["is_active"] = False
        user_dict["activation_token"] = activation_token
        user_dict["activation_token_expires"] = activation_token_expires

        new_user = user_crud.create(self.db, user_dict)
        new_user.roles.append(role_obj)

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        # Simulation asynchrone (À lier plus tard avec send_activation_email)
        return new_user
