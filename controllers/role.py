# ============================================================
# controllers/role_controller.py - Pure Passerelle pour les Rôles
# ============================================================

from sqlalchemy.orm import Session
from schemas.role import RoleCreate, RoleUpdate
from services.role_service import RoleService

class RoleController:
    def __init__(self, db: Session):
        # Le contrôleur instancie le service en lui injectant la session de BDD
        self.role_service = RoleService(db)

    def create_role(self, role_data: RoleCreate):
        """Transmet la création du rôle au service."""
        return self.role_service.create_role(role_data)

    def get_role_by_id(self, role_id: int):
        """Transmet la récupération du rôle par ID au service."""
        return self.role_service.get_role_by_id(role_id)

    def update_role(self, role_id: int, role_data: RoleUpdate):
        """Transmet la mise à jour du rôle au service."""
        return self.role_service.update_role(role_id, role_data)

    def delete_role(self, role_id: int):
        """Transmet la suppression du rôle au service."""
        return self.role_service.delete_role(role_id)

    def get_all_roles(self):
        return self.role_service.get_all_roles()