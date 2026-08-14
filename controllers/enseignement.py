# ============================================================
# controllers/enseignement.py - Contrôleur des enseignements
# ============================================================
from services.enseignement_service import EnseignementService


class EnseignementController:
    """
    Contrôleur pour les actions liées aux enseignements.
    Fait le lien entre la route et le service.
    Ne contient aucune logique métier.
    """
    def __init__(self, db):
        self.db = db
        self.service = EnseignementService(db)

    def assigner_enseignement(self, enseignement_data):
        return self.service.assigner_enseignement(enseignement_data)

    def get_enseignements_by_professeur(self,  professeur_id: int, current_user):
        return self.service.get_enseignements_by_professeur(professeur_id, current_user)

    def get_enseignements_by_matiere(self, matiere_id):
        return self.service.get_enseignements_by_matiere(matiere_id)

    def get_all_enseignements(self, skip=0, limit=100):
        return self.service.get_all_enseignements(skip, limit)

    def get_enseignement_by_id(self, enseignement_id):
        return self.service.get_enseignement_by_id(enseignement_id)

    def supprimer_enseignement(self, enseignement_id):
        return self.service.supprimer_enseignement(enseignement_id)

    def update_enseignement(self, enseignement_id, enseignement_data):
        return self.service.update_enseignement(enseignement_id, enseignement_data)
