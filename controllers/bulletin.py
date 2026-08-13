# ============================================================
# controllers/bulletin.py - Contrôleur des bulletins
# ============================================================
from services.bulletin_service import BulletinService


class BulletinController:
    """
    Contrôleur pour les actions liées aux bulletins.
    Fait le lien entre la route et le service.
    Ne contient aucune logique métier.
    """
    def __init__(self, db):
        self.db = db
        self.service = BulletinService(db)

    def generer_bulletin_etudiant(self, etudiant_id, semestre, annee_universitaire, current_user):
        return self.service.generer_bulletin_etudiant(etudiant_id, semestre, annee_universitaire, current_user)

    def sauvegarder_resultat_semestre(self, etudiant_id, semestre, annee_universitaire):
        return self.service.sauvegarder_resultat_semestre(etudiant_id, semestre, annee_universitaire)

    def get_resultats_etudiant(self, etudiant_id, current_user):
        return self.service.get_resultats_etudiant(etudiant_id, current_user)

    def get_calcul_semestre(self, etudiant_id, semestre, annee_universitaire, current_user):
        return self.service.get_calcul_semestre(etudiant_id, semestre, annee_universitaire, current_user)

    def get_moyenne_matiere_etudiant(self, etudiant_id, matiere_id, current_user):
        return self.service.get_moyenne_matiere_etudiant(etudiant_id, matiere_id, current_user)

    def generer_pv_classe(self, semestre, annee_universitaire, filiere_id=None):
        return self.service.generer_pv_classe(semestre, annee_universitaire, filiere_id)

    def generer_pv_matiere(self, matiere_id, semestre, annee_universitaire, current_user):
        return self.service.generer_pv_matiere(matiere_id, semestre, annee_universitaire, current_user)