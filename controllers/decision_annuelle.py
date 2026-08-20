
# controllers/decision_annuelle.py - Contrôleur des décisions annuelles
from services.bulletin_service import BulletinService
import crud.decision_annuelle as decision_crud
from schemas.decision_annuelle import DecisionAnnuelleRead
from exceptions.base import DecisionAnnuelleNotFoundError


class DecisionAnnuelleController:
    """
    Contrôleur pour les actions liées aux décisions annuelles.
    Fait le lien entre la route et le service.
    Ne contient aucune logique métier.
    """
    def __init__(self, db):
        self.db = db
        self.bulletin_service = BulletinService(db)

    def generer_decision_annuelle(self, etudiant_id, annee_universitaire):
        return self.bulletin_service.generer_decision_annuelle(etudiant_id, annee_universitaire)

    def get_by_id(self, decision_id):
        decision = decision_crud.get_by_id(self.db, decision_id)
        if not decision:
            raise DecisionAnnuelleNotFoundError()
        return DecisionAnnuelleRead.model_validate(decision)

    def get_by_etudiant(self, etudiant_id):
        decisions = decision_crud.get_by_etudiant(self.db, etudiant_id)
        return [DecisionAnnuelleRead.model_validate(d) for d in decisions]

    def get_all(self, skip=0, limit=100):
        decisions = decision_crud.get_all(self.db, skip, limit)
        return [DecisionAnnuelleRead.model_validate(d) for d in decisions]

    def update_decision(self, decision_id, update_data):
        decision = decision_crud.get_by_id(self.db, decision_id)
        if not decision:
            raise DecisionAnnuelleNotFoundError()
        updated = decision_crud.update(self.db, decision_id, update_data.model_dump(exclude_unset=True))
        return DecisionAnnuelleRead.model_validate(updated)

