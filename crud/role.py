
# crud/role.py - Opérations CRUD pour la table Role
from typing import Optional, List
from sqlalchemy.orm import Session

from models.role import Role


# ---------- Récupération par ID ----------
def get_by_id(db: Session, role_id: int) -> Optional[Role]:
    """
    Récupère un rôle par son ID.
    """
    return db.query(Role).filter(Role.id == role_id).first()


# ---------- Récupération par nom ----------
def get_by_name(db: Session, name: str) -> Optional[Role]:
    """
    Récupère un rôle par son nom.
    """
    return db.query(Role).filter(Role.name == name).first()


# ---------- Récupération de tous les rôles ----------
def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
    """
    Récupère une liste paginée de rôles.
    """
    return db.query(Role).offset(skip).limit(limit).all()


# ---------- Création d'un rôle ----------
def create(db: Session, role_data: dict) -> Role:
    """
    Crée un nouveau rôle.
    """
    nouveau_role = Role(**role_data)
    db.add(nouveau_role)
    db.commit()
    db.refresh(nouveau_role)
    return nouveau_role


# ---------- Mise à jour d'un rôle ----------
def update(db: Session, role_id: int, role_data: dict) -> Optional[Role]:
    """
    Met à jour un rôle existant.
    """
    role = get_by_id(db, role_id)
    if not role:
        return None

    for key, value in role_data.items():
        if value is not None:
            setattr(role, key, value)

    db.commit()
    db.refresh(role)
    return role


# ---------- Suppression d'un rôle ----------
def delete(db: Session, role_id: int) -> None:
    """
    Supprime un rôle.
    """
    role = get_by_id(db, role_id)
    if not role:
        return None

    db.delete(role)
    db.commit()
    return None