# controllers/inscription.py - Contrôleur des inscriptions
from services.inscription_service import InscriptionService


class InscriptionController:
    """
    Contrôleur pour les actions liées aux inscriptions.
    Fait le lien entre la route et le service.
    Ne contient aucune logique métier.
    """
    def __init__(self, db):
        self.db = db
        self.service = InscriptionService(db)

    def inscrire_etudiant(self, inscription_data):
        return self.service.inscrire_etudiant(inscription_data)

    def get_inscription_by_id(self, inscription_id):
        return self.service.get_inscription_by_id(inscription_id)

    def get_inscriptions_by_etudiant(self, etudiant_id):
        return self.service.get_inscriptions_by_etudiant(etudiant_id)

    def get_inscriptions_by_matiere(self, matiere_id):
        return self.service.get_inscriptions_by_matiere(matiere_id)

    def get_all_inscriptions(self, skip=0, limit=100):
        return self.service.get_all_inscriptions(skip, limit)

    def update_inscription(self, inscription_id, update_data):
        return self.service.update_inscription(inscription_id, update_data)

    def supprimer_inscription(self, inscription_id):
        return self.service.supprimer_inscription(inscription_id)

