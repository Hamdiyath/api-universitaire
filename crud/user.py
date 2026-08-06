#Ce fichier contient toutes les requêtes SQLAlchemy concernant
# le modèle User. Chaque fonction interagit directement avec la base
# de données.
from sqlalchemy.orm import Session
from models.user import User
from typing import Optional


# ---------- Récupération d'un utilisateur par son email ----------
def get_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


# ---------- Récupération de tous les utilisateurs ---------
def create(db: Session, user_data: dict) -> User:
    new_user = User(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user