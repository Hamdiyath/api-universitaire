
# controllers/filiere.py - Contrôleur des filières

from services.filiere_service import FiliereService


class FiliereController:
    """
    Contrôleur pour les actions liées aux filières.
    Fait le lien entre la route et le service.
    Ne contient aucune logique métier.
    """
    def __init__(self, db):
        self.db = db
        self.service = FiliereService(db)

    def create_filiere(self, filiere_data):
        return self.service.create_filiere(filiere_data)

    def get_filiere_by_id(self, filiere_id):
        return self.service.get_filiere_by_id(filiere_id)

    def update_filiere(self, filiere_id, filiere_data):
        return self.service.update_filiere(filiere_id, filiere_data)

    def delete_filiere(self, filiere_id):
        return self.service.delete_filiere(filiere_id)

    def get_all_filieres(self, skip=0, limit=100):
        return self.service.get_all_filieres(skip, limit)