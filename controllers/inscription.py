# ============================================================
# controllers/inscription_controller.py - Pure Passerelle
# ============================================================

from sqlalchemy.orm import Session
from schemas.inscription import InscriptionCreate
from services.inscription_service import InscriptionService

class InscriptionController:
    def __init__(self, db: Session):
        # Le contrôleur instancie le service en lui injectant la session de BDD
        self.inscription_service = InscriptionService(db)

    def inscrire_etudiant(self, inscription_data: InscriptionCreate):
        """Transmet l'action d'inscription au service."""
        return self.inscription_service.inscrire_etudiant(inscription_data)

    def get_inscriptions_by_etudiant(self, etudiant_id: int):
        """Transmet la récupération des inscriptions d'un étudiant au service."""
        return self.inscription_service.get_inscriptions_by_etudiant(etudiant_id)

    def get_inscriptions_by_matiere(self, matiere_id: int):
        """Transmet la récupération des inscriptions d'une matière au service."""
        return self.inscription_service.get_inscriptions_by_matiere(matiere_id)

    def get_all_inscriptions(self, skip: int, limit: int):
        """Transmet la récupération globale et paginée des inscriptions au service."""
        return self.inscription_service.get_all_inscriptions(skip, limit)

    def supprimer_inscription(self, etudiant_id: int, matiere_id: int, semestre: str):
        """Transmet la suppression d'une inscription au service."""
        return self.inscription_service.supprimer_inscription(etudiant_id, matiere_id, semestre)
