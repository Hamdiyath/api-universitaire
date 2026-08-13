
# services/matiere_service.py - Logique métier pour Matiere


from sqlalchemy.orm import Session
from crud.matiere import get_by_nom, get_by_id, create, update, delete , get_all
from schemas.matiere import MatiereCreate, MatiereUpdate, MatiereRead
from typing import List

from exceptions.base import MatiereNotFoundError, MatiereAlreadyExistsError


class MatiereService:
    """Service de gestion des matières. Contient toute la logique métier."""

    def __init__(self, db: Session):
        self.db = db

    # ---------- Création ----------
    def create_matiere(self, matiere_data: MatiereCreate) -> MatiereRead:
        """Crée une nouvelle matière. Vérifie que le nom n'existe pas déjà."""
        existing_matiere = get_by_nom(self.db, matiere_data.nom)
        if existing_matiere:
            raise MatiereAlreadyExistsError(matiere_data.nom)

        new_matiere = create(self.db, matiere_data.model_dump())
        return MatiereRead.model_validate(new_matiere)

    # ---------- Lecture ----------
    def get_matiere_by_id(self, matiere_id: int) -> MatiereRead:
        """Récupère une matière par son ID."""
        matiere = get_by_id(self.db, matiere_id)
        if not matiere:
            raise MatiereNotFoundError(matiere_id)
        return MatiereRead.model_validate(matiere)

    # ---------- Mise à jour ----------
    def update_matiere(self, matiere_id: int, matiere_data: MatiereUpdate) -> MatiereRead:
        """Met à jour une matière existante."""
        existing_matiere = get_by_id(self.db, matiere_id)
        if not existing_matiere:
            raise MatiereNotFoundError(matiere_id)

        update_data = matiere_data.model_dump(exclude_unset=True)

        if "nom" in update_data and update_data["nom"] != existing_matiere.nom:
            nom_exists = get_by_nom(self.db, update_data["nom"])
            if nom_exists:
                raise MatiereAlreadyExistsError(update_data["nom"])

        updated_matiere = update(self.db, matiere_id, update_data)
        return MatiereRead.model_validate(updated_matiere)

    # ---------- Suppression ----------
    def delete_matiere(self, matiere_id: int) -> None:
        """Supprime une matière."""
        existing_matiere = get_by_id(self.db, matiere_id)
        if not existing_matiere:
            raise MatiereNotFoundError(matiere_id)
        delete(self.db, matiere_id)

        # ---------- Liste ----------
    def get_all_matieres(self, skip: int = 0, limit: int = 100) -> List[MatiereRead]:
            """Récupère toutes les matières (paginé)."""
            matieres = get_all(self.db, skip, limit)
            return [MatiereRead.model_validate(m) for m in matieres]