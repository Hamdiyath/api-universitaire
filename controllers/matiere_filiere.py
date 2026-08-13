# ============================================================
# controllers/matiere_filiere.py - Contrôleur des associations Matière-Filière
# ============================================================
from services.matiere_filiere_service import MatiereFiliereService


class MatiereFiliereController:
    """
    Contrôleur pour les actions liées aux associations Matière-Filière.
    Fait le lien entre la route et le service.
    Ne contient aucune logique métier.
    """
    def __init__(self, db):
        self.db = db
        self.service = MatiereFiliereService(db)

    def associer_matiere_filiere(self, association_data):
        return self.service.associer_matiere_filiere(association_data)

    def get_associations_by_matiere(self, matiere_id):
        return self.service.get_associations_by_matiere(matiere_id)

    def get_associations_by_filiere(self, filiere_id, current_user):
        return self.service.get_associations_by_filiere(filiere_id, current_user)

    def get_all_associations(self, skip=0, limit=100):
        return self.service.get_all_associations(skip, limit)

    def supprimer_association(self, matiere_id, filiere_id, semestre):
        return self.service.supprimer_association(matiere_id, filiere_id, semestre)