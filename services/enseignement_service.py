
# services/enseignement_service.py - Logique métier pour Enseignement


from sqlalchemy.orm import Session
from typing import List

from crud.enseignement import (
    get_by_professeur_and_matiere,
    get_by_professeur,
    get_by_matiere,
    get_all,
    get_by_id,
    create,
    delete_by_id,
    update
)
from crud.user import get_by_id as get_user_by_id
from crud.matiere import get_by_id as get_matiere_by_id
from schemas.enseignement import EnseignementCreate, EnseignementRead, EnseignementUpdate

from exceptions.base import (
    UserNotFoundError,
    MatiereNotFoundError,
    EnseignementNotFoundError,
    EnseignementAlreadyExistsError,
    PermissionDeniedError
)


class EnseignementService:
    """Service de gestion des enseignements. Contient toute la logique métier."""

    def __init__(self, db: Session):
        self.db = db

    # ---------- 1. Assigner un professeur à une matière ----------
    def assigner_enseignement(self, enseignement_data: EnseignementCreate) -> EnseignementRead:
        """
        Assigner un professeur à une matière.
        Vérifie que le professeur et la matière existent, et que l'assignation n'existe pas déjà.
        """
        professeur = get_user_by_id(self.db, enseignement_data.professeur_id)
        if not professeur:
            raise UserNotFoundError(enseignement_data.professeur_id)

        matiere = get_matiere_by_id(self.db, enseignement_data.matiere_id)
        if not matiere:
            raise MatiereNotFoundError(enseignement_data.matiere_id)

        existing = get_by_professeur_and_matiere(
            self.db,
            enseignement_data.professeur_id,
            enseignement_data.matiere_id
        )
        if existing:
            raise EnseignementAlreadyExistsError()

        new_enseignement = create(self.db, enseignement_data.model_dump())
        return EnseignementRead.model_validate(new_enseignement)

        # ---------- 2. Récupérer les enseignements d'un professeur ----------
    def get_enseignements_by_professeur(self, professeur_id: int, current_user) -> List[EnseignementRead]:
        """
        Récupère toutes les matières enseignées par un professeur.
        - Un professeur ne peut voir que ses propres enseignements
        - Admin peut voir tous les enseignements
        """
        user_roles = [role.name for role in current_user.roles]

        if current_user.id != professeur_id and "admin" not in user_roles:
            raise PermissionDeniedError("Vous n'avez pas l'autorisation de voir ces enseignements")

        professeur = get_user_by_id(self.db, professeur_id)
        if not professeur:
            raise UserNotFoundError(professeur_id)

        enseignements = get_by_professeur(self.db, professeur_id)
        return [EnseignementRead.model_validate(e) for e in enseignements]

    # ---------- 3. Récupérer les professeurs d'une matière ----------
    def get_enseignements_by_matiere(self, matiere_id: int) -> List[EnseignementRead]:
        """Récupère tous les professeurs qui enseignent une matière."""
        matiere = get_matiere_by_id(self.db, matiere_id)
        if not matiere:
            raise MatiereNotFoundError(matiere_id)

        enseignements = get_by_matiere(self.db, matiere_id)
        return [EnseignementRead.model_validate(e) for e in enseignements]

    # ---------- 4. Récupérer tous les enseignements ----------
    def get_all_enseignements(self, skip: int = 0, limit: int = 100) -> List[EnseignementRead]:
        """Récupère tous les enseignements (paginé)."""
        enseignements = get_all(self.db, skip, limit)
        return [EnseignementRead.model_validate(e) for e in enseignements]

    # ---------- 5. Récupérer un enseignement par ID ----------
    def get_enseignement_by_id(self, enseignement_id: int) -> EnseignementRead:
        """Récupère un enseignement par son ID."""
        enseignement = get_by_id(self.db, enseignement_id)
        if not enseignement:
            raise EnseignementNotFoundError(enseignement_id)
        return EnseignementRead.model_validate(enseignement)

    # ---------- 6. Supprimer un enseignement ----------
    def supprimer_enseignement(self, enseignement_id: int) -> None:
        """Supprime un enseignement par son ID."""
        enseignement = get_by_id(self.db, enseignement_id)
        if not enseignement:
            raise EnseignementNotFoundError(enseignement_id)
        delete_by_id(self.db, enseignement_id)

    # ---------- 7. Mettre à jour un enseignement ----------
    def update_enseignement(self, enseignement_id: int, enseignement_data: EnseignementUpdate) -> EnseignementRead:
        """
        Met à jour un enseignement existant.
        Si le professeur ou la matière est modifié, vérifie que les nouvelles valeurs existent.
        """
        enseignement = get_by_id(self.db, enseignement_id)
        if not enseignement:
            raise EnseignementNotFoundError(enseignement_id)

        update_data = enseignement_data.model_dump(exclude_unset=True)

        if "professeur_id" in update_data:
            professeur = get_user_by_id(self.db, update_data["professeur_id"])
            if not professeur:
                raise UserNotFoundError(update_data["professeur_id"])

        if "matiere_id" in update_data:
            matiere = get_matiere_by_id(self.db, update_data["matiere_id"])
            if not matiere:
                raise MatiereNotFoundError(update_data["matiere_id"])

        updated_enseignement = update(self.db, enseignement_id, update_data)
        return EnseignementRead.model_validate(updated_enseignement)



