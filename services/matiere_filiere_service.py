
# services/matiere_filiere_service.py - Logique métier pour MatiereFiliere


from sqlalchemy.orm import Session
from typing import List

from crud.matiere_filiere import (
    get_by_id,
    get_by_matiere,
    get_by_filiere,
    get_all,
    create,
    delete
)
from crud.matiere import get_by_id as get_matiere_by_id
from crud.filiere import get_by_id as get_filiere_by_id
from schemas.matiere_filiere import MatiereFiliereCreate, MatiereFiliereRead

from exceptions.base import (
    MatiereNotFoundError,
    FiliereNotFoundError,
    MatiereFiliereNotFoundError,
    MatiereFiliereAlreadyExistsError,
    PermissionDeniedError,
    FiliereRequiredError,
)


class MatiereFiliereService:
    """Service de gestion des associations Matière-Filière."""

    def __init__(self, db: Session):
        self.db = db

    # ---------- Création ----------
    def associer_matiere_filiere(self, association_data: MatiereFiliereCreate) -> MatiereFiliereRead:
        """
        Associe une matière à une filière pour un semestre donné.
        Vérifie que la matière et la filière existent, et que l'association n'existe pas déjà.
        """
        matiere = get_matiere_by_id(self.db, association_data.matiere_id)
        if not matiere:
            raise MatiereNotFoundError(association_data.matiere_id)

        filiere = get_filiere_by_id(self.db, association_data.filiere_id)
        if not filiere:
            raise FiliereNotFoundError(association_data.filiere_id)

        existing = get_by_id(
            self.db,
            association_data.matiere_id,
            association_data.filiere_id,
            association_data.semestre
        )
        if existing:
            raise MatiereFiliereAlreadyExistsError()

        new_association = create(self.db, association_data.model_dump())
        return MatiereFiliereRead.model_validate(new_association)

    # ---------- Lecture par matière ----------
    def get_associations_by_matiere(self, matiere_id: int) -> List[MatiereFiliereRead]:
        """Récupère toutes les associations d'une matière."""
        matiere = get_matiere_by_id(self.db, matiere_id)
        if not matiere:
            raise MatiereNotFoundError(matiere_id)

        associations = get_by_matiere(self.db, matiere_id)
        return [MatiereFiliereRead.model_validate(a) for a in associations]

    # ---------- Lecture par filière (avec permissions) ----------
    def get_associations_by_filiere(self, filiere_id: int, current_user) -> List[MatiereFiliereRead]:
        """
        Récupère toutes les associations d'une filière.
        - Admin, Scolarité, Professeur : voient toutes les filières
        - Étudiant : voit uniquement sa propre filière
        - Autres : accès refusé
        """
        user_roles = [role.name for role in current_user.roles]

        if "etudiant" in user_roles:
            if current_user.filiere_id is None:
                raise FiliereRequiredError()
            if current_user.filiere_id != filiere_id:
                raise PermissionDeniedError("Vous ne pouvez voir que les matières de votre propre filière")
        elif not any(role in user_roles for role in ["admin", "scolarite", "professeur"]):
            raise PermissionDeniedError("Vous n'avez pas l'autorisation de voir cette filière")

        filiere = get_filiere_by_id(self.db, filiere_id)
        if not filiere:
            raise FiliereNotFoundError(filiere_id)

        associations = get_by_filiere(self.db, filiere_id)
        return [MatiereFiliereRead.model_validate(a) for a in associations]

    # ---------- Lecture globale ----------
    def get_all_associations(self, skip: int = 0, limit: int = 100) -> List[MatiereFiliereRead]:
        """Récupère toutes les associations (paginé)."""
        associations = get_all(self.db, skip, limit)
        return [MatiereFiliereRead.model_validate(a) for a in associations]

    # ---------- Suppression ----------
    def supprimer_association(self, matiere_id: int, filiere_id: int, semestre: str) -> None:
        """Supprime une association matière-filière."""
        existing = get_by_id(self.db, matiere_id, filiere_id, semestre)
        if not existing:
            raise MatiereFiliereNotFoundError()
        delete(self.db, matiere_id, filiere_id, semestre)