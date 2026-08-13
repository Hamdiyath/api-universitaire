# ============================================================
# controllers/matiere.py - Contrôleur des matières
# ============================================================
from services.matiere_service import MatiereService


class MatiereController:
    """
    Contrôleur pour les actions liées aux matières.
    Fait le lien entre la route et le service.
    Ne contient aucune logique métier.
    """
    def __init__(self, db):
        self.db = db
        self.service = MatiereService(db)

    def create_matiere(self, matiere_data):
        return self.service.create_matiere(matiere_data)

    def get_matiere_by_id(self, matiere_id):
        return self.service.get_matiere_by_id(matiere_id)

    def update_matiere(self, matiere_id, matiere_data):
        return self.service.update_matiere(matiere_id, matiere_data)

    def delete_matiere(self, matiere_id):
        return self.service.delete_matiere(matiere_id)

    def get_all_matieres(self, skip=0, limit=100):
        return self.service.get_all_matieres(skip, limit)