import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher
from jose import jwt

# Chargement des variables d'environnement
load_dotenv()

# Récupération des variables d'environnement
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Initialisation du contexte de hachage (bcrypt)
password_hash = PasswordHash((BcryptHasher(),))


def hash_password(password: str) -> str:
    """Hache un mot de passe en clair."""
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe en clair contre un hash."""
    #Vérifie si le mot de passe en clair correspond au hash enregistré
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Génère un token JWT."""
    to_encode = data.copy()
    #Tu appelles la fonction en passant une durée personnalisée :
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
    #Tu appelles la fonction sans le paramètre :
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)