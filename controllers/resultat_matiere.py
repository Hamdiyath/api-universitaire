# controllers/resultat_matiere.py - Contrôleur des résultats matière
from services.resultat_matiere_service import ResultatMatiereService


class ResultatMatiereController:
    """
    Contrôleur pour les actions liées aux résultats matière.
    Fait le lien entre la route et le service.
    Ne contient aucune logique métier.
    """
    def __init__(self, db):
        self.db = db
        self.service = ResultatMatiereService(db)

    def generer_resultats_etudiant(self, etudiant_id, semestre, annee_universitaire, current_user):
        return self.service.generer_resultats_etudiant(etudiant_id, semestre, annee_universitaire, current_user)

    def get_by_id(self, resultat_id):
        return self.service.get_by_id(resultat_id)

    def get_resultats_by_etudiant(self, etudiant_id, current_user):
        return self.service.get_resultats_by_etudiant(etudiant_id, current_user)

    def get_resultats_by_matiere(self, matiere_id):
        return self.service.get_resultats_by_matiere(matiere_id)

    def get_all_resultats(self, skip=0, limit=100):
        return self.service.get_all_resultats(skip, limit)

    def supprimer_resultat(self, resultat_id):
        return self.service.supprimer_resultat(resultat_id)



    def generer_dettes_annee_suivante(self, semestre, annee_universitaire, nouvelle_annee_universitaire):
        from services.bulletin_service import BulletinService
        return BulletinService(self.db).generer_dettes_annee_suivante(
            semestre, annee_universitaire, nouvelle_annee_universitaire
        )