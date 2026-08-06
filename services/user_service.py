
# services/user_service.py - Logique métier pour User

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from crud.user import get_by_email, create
from core.security import hash_password, verify_password
from schemas.user import UserCreate


def register_user(db: Session, user_data: UserCreate):
    """
    Logique d'inscription d'un nouvel utilisateur.

    Étapes :
        1. Vérifier que l'email n'est pas déjà utilisé
        2. Vérifier que les mots de passe correspondent
        3. Hacher le mot de passe
        4. Créer l'utilisateur en base
        5. Retourner l'utilisateur créé
    """
    # 1. Vérifier si l'email existe déjà
    existing_user = get_by_email(db, user_data.email)
    if existing_user:
       raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé"
        )

    # 2. Vérifier que les mots de passe correspondent
    if user_data.password != user_data.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Les mots de passe ne correspondent pas"
        )

    # 3. Hacher le mot de passe
    hashed_password = hash_password(user_data.password)

    # 4. Préparer les données pour la création
    user_dict = user_data.model_dump()
    user_dict.pop("password")
    user_dict.pop("password_confirm")
    user_dict["password_hash"] = hashed_password

    # 5. Créer l'utilisateur
    new_user = create(db, user_dict)

    return new_user


def authenticate_user(db: Session, email: str, password: str):
    """
    Logique de connexion d'un utilisateur.

    Étapes :
        1. Récupérer l'utilisateur par son email
        2. Vérifier que l'utilisateur existe
        3. Vérifier que le mot de passe correspond
        4. Retourner l'utilisateur
    """
    # 1. Récupérer l'utilisateur
    user = get_by_email(db, email)

    # 2. Vérifier que l'utilisateur existe
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )

    # 3. Vérifier le mot de passe
    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )

    return user