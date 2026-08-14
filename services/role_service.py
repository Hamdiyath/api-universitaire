# ============================================================
# services/role_service.py - Logique métier pour Role (Le Cerveau)
# ============================================================

from sqlalchemy.orm import Session
from typing import List

# Import des CRUDs sous un seul namespace pour éviter les collisions
import crud.role as role_crud

# Import des Schémas
from schemas.role import RoleCreate, RoleUpdate, RoleRead

# Import de vos Alarmes (Exceptions métiers pures)
from exceptions.base import RoleAlreadyExistsError, RoleNotFoundError

class RoleService:
    def __init__(self, db: Session):
        self.db = db

    # ---------- Création d'un rôle ----------
    def create_role(self, role_data: RoleCreate) -> RoleRead:
        """Crée un nouveau rôle universitaire."""
        # 1. Alarme : Le nom existe déjà
        existing_role = role_crud.get_by_name(self.db, role_data.name)
        if existing_role:
            raise RoleAlreadyExistsError(role_data.name)

        # 2. Créer le rôle via la couche CRUD
        new_role = role_crud.create(self.db, role_data.model_dump())
        return RoleRead.model_validate(new_role)

    # ---------- Récupération d'un rôle par ID ----------
    def get_role_by_id(self, role_id: int):
        """Récupère un rôle ou déclenche une alarme si introuvable."""
        role = role_crud.get_by_id(self.db, role_id)
        if not role:
            raise RoleNotFoundError(f"ID {role_id}")
        return role

    # ---------- Mise à jour d'un rôle ----------
    def update_role(self, role_id: int, role_data: RoleUpdate):
        """Met à jour un rôle existant et valide l'unicité du nom."""
        # 1. Alarme : Le rôle à modifier n'existe pas
        existing_role = role_crud.get_by_id(self.db, role_id)
        if not existing_role:
            raise RoleNotFoundError(f"ID {role_id}")

        # 2. Convertir en dict et filtrer les champs non fournis
        update_data = role_data.model_dump(exclude_unset=True)

        # 3. Si le nom change, vérifier qu'il n'écrase pas un autre rôle
        if "name" in update_data and update_data["name"] != existing_role.name:
            name_exists = role_crud.get_by_name(self.db, update_data["name"])
            if name_exists:
                raise RoleAlreadyExistsError(update_data["name"])

        # 4. Mettre à jour via le CRUD
        updated_role = role_crud.update(self.db, role_id, update_data)
        return updated_role

    # ---------- Suppression d'un rôle ----------
    def delete_role(self, role_id: int) -> None:
        """Supprime un rôle après vérification de son existence."""
        existing_role = role_crud.get_by_id(self.db, role_id)
        if not existing_role:
            raise RoleNotFoundError(f"ID {role_id}")

        role_crud.delete(self.db, role_id)
        return None


    def get_all_roles(self) -> List[RoleRead]:
       role = role_crud.get_all(self.db)
       return [RoleRead.model_validate(f) for f in role]