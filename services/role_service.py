
# services/role_service.py - Logique métier pour Role


from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from crud.role import get_by_name, get_by_id, create, update, delete
from schemas.role import RoleCreate, RoleUpdate, RoleRead


# ---------- Création d'un rôle ----------
def create_role(db: Session, role_data: RoleCreate):
    """
    Crée un nouveau rôle.
    Vérifie que le nom n'existe pas déjà.
    """
    # 1. Vérifier si le nom existe déjà
    existing_role = get_by_name(db, role_data.name)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce rôle existe déjà"
        )

    # 2. Créer le rôle
    new_role = create(db, role_data.model_dump())
    return RoleRead.model_validate(new_role)


# ---------- Récupération d'un rôle par ID ----------
def get_role_by_id(db: Session, role_id: int):
    """
    Récupère un rôle par son ID.
    Lève une exception si le rôle n'existe pas.
    """
    role = get_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ce rôle n'existe pas"
        )
    return role


# ---------- Mise à jour d'un rôle ----------
def update_role(db: Session, role_id: int, role_data: RoleUpdate):
    """
    Met à jour un rôle existant.
    Vérifie que le rôle existe.
    Vérifie que le nouveau nom n'est pas déjà utilisé (si le nom est modifié).
    """
    # 1. Vérifier que le rôle existe
    existing_role = get_by_id(db, role_id)
    if not existing_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ce rôle n'existe pas"
        )

    # 2. Convertir en dict et filtrer les champs None
    update_data = role_data.model_dump(exclude_unset=True)

    # 3. Si le nom est modifié, vérifier qu'il n'est pas déjà utilisé
    if "name" in update_data and update_data["name"] != existing_role.name:
        name_exists = get_by_name(db, update_data["name"])
        if name_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce nom est déjà utilisé par un autre rôle"
            )

    # 4. Mettre à jour le rôle
    updated_role = update(db, role_id, update_data)
    return updated_role


# ---------- Suppression d'un rôle ----------
def delete_role(db: Session, role_id: int):
    """
    Supprime un rôle.
    Vérifie que le rôle existe.
    """
    # 1. Vérifier que le rôle existe
    existing_role = get_by_id(db, role_id)
    if not existing_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rôle non trouvé"
        )

    # 2. Supprimer le rôle
    delete(db, role_id)
    return None