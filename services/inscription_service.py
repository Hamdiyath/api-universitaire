# ============================================================
# services/inscription_service.py - Logique métier Inscription
# ============================================================

from sqlalchemy.orm import Session
from typing import List

# Import des CRUDs sous namespaces distincts pour la clarté
import crud.inscription as inscription_crud
import crud.user as user_crud
import crud.matiere as matiere_crud

# Import des Schémas
from schemas.inscription import InscriptionCreate, InscriptionRead

# 1. PLUS D'HTTPEXCEPTION : Utilisation exclusive des alarmes métiers
from exceptions.base import (
    UserNotFoundError,
    MatiereNotFoundError,
    InscriptionAlreadyExistsError,
    InscriptionNotFoundError
)

class InscriptionService:
    def __init__(self, db: Session):
        self.db = db

    def inscrire_etudiant(self, inscription_data: InscriptionCreate) -> InscriptionRead:
        """
        Inscrit un étudiant à une matière universitaire.
        """
        # 1. Alarme : L'étudiant n'existe pas
        etudiant = user_crud.get_by_id(self.db, inscription_data.etudiant_id)
        if not etudiant:
            raise UserNotFoundError(inscription_data.etudiant_id)

        # 2. Alarme : La matière n'existe pas
        matiere = matiere_crud.get_by_id(self.db, inscription_data.matiere_id)
        if not matiere:
            raise MatiereNotFoundError(inscription_data.matiere_id)

        # 3. Alarme : Doublon d'inscription
        existing = inscription_crud.get_by_etudiant_and_matieres(
            self.db,
            inscription_data.etudiant_id,
            [inscription_data.matiere_id]
        )
        if existing:
            raise InscriptionAlreadyExistsError()

        # 4. Création via la couche CRUD
        new_inscription = inscription_crud.create(self.db, inscription_data.model_dump())
        return InscriptionRead.model_validate(new_inscription)

    def get_inscriptions_by_etudiant(self, etudiant_id: int) -> List[InscriptionRead]:
        """
        Récupère toutes les inscriptions d’un étudiant spécifique.
        """
        etudiant = user_crud.get_by_id(self.db, etudiant_id)
        if not etudiant:
            raise UserNotFoundError(etudiant_id)

        inscriptions = inscription_crud.get_by_etudiant(self.db, etudiant_id)
        return [InscriptionRead.model_validate(i) for i in inscriptions]

    def get_inscriptions_by_matiere(self, matiere_id: int) -> List[InscriptionRead]:
        """
        Récupère toutes les inscriptions d’une matière spécifique.
        """
        matiere = matiere_crud.get_by_id(self.db, matiere_id)
        if not matiere:
            raise MatiereNotFoundError(matiere_id)

        inscriptions = inscription_crud.get_by_matiere(self.db, matiere_id)
        return [InscriptionRead.model_validate(i) for i in inscriptions]

    def get_all_inscriptions(self, skip: int = 0, limit: int = 100) -> List[InscriptionRead]:
        """
        Récupère toutes les inscriptions du système (paginé).
        """
        inscriptions = inscription_crud.get_all(self.db, skip, limit)
        return [InscriptionRead.model_validate(i) for i in inscriptions]

    def supprimer_inscription(self, etudiant_id: int, matiere_id: int, semestre: str) -> None:
        """
        Supprime l'inscription d'un étudiant.
        """
        # Vérification de l'existence de l'inscription
        inscriptions = inscription_crud.get_by_etudiant_and_matieres(self.db, etudiant_id, [matiere_id])
        if not inscriptions:
            raise InscriptionNotFoundError()

        inscription_crud.delete(self.db, etudiant_id, matiere_id, semestre)
        return None
