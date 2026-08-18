# ============================================================
# services/inscription_service.py - Logique métier Inscription
# ============================================================

from sqlalchemy.orm import Session
from typing import List, Optional

import crud.inscription as inscription_crud
import crud.user as user_crud
import crud.matiere as matiere_crud
from crud.note import get_by_etudiant_and_matiere

from schemas.inscription import InscriptionCreate, InscriptionUpdate, InscriptionRead

from exceptions.base import (
    UserNotFoundError,
    MatiereNotFoundError,
    InscriptionAlreadyExistsError,
    InscriptionNotFoundError,
    InscriptionModificationBlockedError,
    PermissionDeniedError
)


class InscriptionService:
    def __init__(self, db: Session):
        self.db = db

    # ---------- Création ----------
    def inscrire_etudiant(self, inscription_data: InscriptionCreate) -> InscriptionRead:
        """
        Inscrit un étudiant à une matière pour un semestre et une année donnés.
        """
        etudiant = user_crud.get_by_id(self.db, inscription_data.etudiant_id)
        if not etudiant:
            raise UserNotFoundError(inscription_data.etudiant_id)

        matiere = matiere_crud.get_by_id(self.db, inscription_data.matiere_id)
        if not matiere:
            raise MatiereNotFoundError(inscription_data.matiere_id)

        existing = inscription_crud.get_by_etudiant_matiere_semestre_annee(
            self.db,
            inscription_data.etudiant_id,
            inscription_data.matiere_id,
            inscription_data.semestre,
            inscription_data.annee_universitaire
        )
        if existing:
            raise InscriptionAlreadyExistsError()

        new_inscription = inscription_crud.create(self.db, inscription_data.model_dump())
        return InscriptionRead.model_validate(new_inscription)

    # ---------- Lecture ----------
    def get_inscription_by_id(self, inscription_id: int) -> InscriptionRead:
        """Récupère une inscription par son ID."""
        inscription = inscription_crud.get_by_id(self.db, inscription_id)
        if not inscription:
            raise InscriptionNotFoundError()
        return InscriptionRead.model_validate(inscription)


    def get_inscriptions_by_matiere(self, matiere_id: int) -> List[InscriptionRead]:
        """Récupère toutes les inscriptions d'une matière."""
        matiere = matiere_crud.get_by_id(self.db, matiere_id)
        if not matiere:
            raise MatiereNotFoundError(matiere_id)

        inscriptions = inscription_crud.get_by_matiere(self.db, matiere_id)
        return [InscriptionRead.model_validate(i) for i in inscriptions]

    def get_all_inscriptions(self, skip: int = 0, limit: int = 100) -> List[InscriptionRead]:
        """Récupère toutes les inscriptions du système (paginé)."""
        inscriptions = inscription_crud.get_all(self.db, skip, limit)
        return [InscriptionRead.model_validate(i) for i in inscriptions]

    # ---------- Mise à jour ----------
    def update_inscription(self, inscription_id: int, update_data: InscriptionUpdate) -> InscriptionRead:
        """
        Met à jour une inscription existante.
        - etudiant_id n'est jamais modifiable (absent du schéma InscriptionUpdate).
        - Si matiere_id ou semestre est modifié alors que des notes existent déjà
          pour cette inscription, la modification est bloquée pour éviter des
          notes orphelines.
        """
        existing_inscription = inscription_crud.get_by_id(self.db, inscription_id)
        if not existing_inscription:
            raise InscriptionNotFoundError()

        data = update_data.model_dump(exclude_unset=True)

        # Si matiere_id ou semestre change, vérifier qu'aucune note n'existe déjà
        if "matiere_id" in data or "semestre" in data:
            notes_existantes = get_by_etudiant_and_matiere(
                self.db,
                existing_inscription.etudiant_id,
                existing_inscription.matiere_id
            )
            if notes_existantes:
                raise InscriptionModificationBlockedError()

        # Si la matière est modifiée, vérifier qu'elle existe
        if "matiere_id" in data:
            matiere = matiere_crud.get_by_id(self.db, data["matiere_id"])
            if not matiere:
                raise MatiereNotFoundError(data["matiere_id"])

        updated_inscription = inscription_crud.update(self.db, inscription_id, data)
        return InscriptionRead.model_validate(updated_inscription)

    # ---------- Suppression ----------
    def supprimer_inscription(self, inscription_id: int) -> None:
        """Supprime une inscription par son ID."""
        existing = inscription_crud.get_by_id(self.db, inscription_id)
        if not existing:
            raise InscriptionNotFoundError()
        inscription_crud.delete(self.db, inscription_id)

    def get_inscriptions_by_etudiant(self, etudiant_id: int, current_user) -> List[InscriptionRead]:
        """
        Récupère toutes les inscriptions d'un étudiant.
        - Étudiant : peut voir uniquement ses propres inscriptions
        - Admin/Scolarité : peuvent voir celles de n'importe quel étudiant
        """
        user_roles = [role.name for role in current_user.roles]
        if current_user.id != etudiant_id and not any(r in user_roles for r in ["admin", "scolarite"]):
            raise PermissionDeniedError("Vous n'avez pas l'autorisation de voir ces inscriptions")

        etudiant = user_crud.get_by_id(self.db, etudiant_id)
        if not etudiant:
            raise UserNotFoundError(etudiant_id)

        inscriptions = inscription_crud.get_by_etudiant(self.db, etudiant_id)
        return [InscriptionRead.model_validate(i) for i in inscriptions]