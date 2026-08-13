# ============================================================
# services/filiere_service.py - Logique métier pour Filiere
# ============================================================

from sqlalchemy.orm import Session
from crud.filiere import get_by_nom, get_by_id, create, update, delete
from schemas.filiere import FiliereCreate, FiliereUpdate, FiliereRead
from typing import List
from crud.filiere import get_by_nom, get_by_id, get_all, create, update, delete

from exceptions.base import FiliereNotFoundError, FiliereAlreadyExistsError


class FiliereService:
    """Service de gestion des filières. Contient toute la logique métier."""

    def __init__(self, db: Session):
        self.db = db

    # ---------- Création ----------
    def create_filiere(self, filiere_data: FiliereCreate) -> FiliereRead:
        """Crée une nouvelle filière. Vérifie que le nom n'existe pas déjà."""
        existing_filiere = get_by_nom(self.db, filiere_data.nom)
        if existing_filiere:
            raise FiliereAlreadyExistsError(filiere_data.nom)

        new_filiere = create(self.db, filiere_data.model_dump())
        return FiliereRead.model_validate(new_filiere)

    # ---------- Lecture ----------
    def get_filiere_by_id(self, filiere_id: int) -> FiliereRead:
        """Récupère une filière par son ID."""
        filiere = get_by_id(self.db, filiere_id)
        if not filiere:
            raise FiliereNotFoundError(filiere_id)
        return FiliereRead.model_validate(filiere)

    # ---------- Mise à jour ----------
    def update_filiere(self, filiere_id: int, filiere_data: FiliereUpdate) -> FiliereRead:
        """Met à jour une filière existante."""
        existing_filiere = get_by_id(self.db, filiere_id)
        if not existing_filiere:
            raise FiliereNotFoundError(filiere_id)

        update_data = filiere_data.model_dump(exclude_unset=True)

        if "nom" in update_data and update_data["nom"] != existing_filiere.nom:
            nom_exists = get_by_nom(self.db, update_data["nom"])
            if nom_exists:
                raise FiliereAlreadyExistsError(update_data["nom"])

        updated_filiere = update(self.db, filiere_id, update_data)
        return FiliereRead.model_validate(updated_filiere)

    # ---------- Suppression ----------
    def delete_filiere(self, filiere_id: int) -> None:
        """Supprime une filière."""
        existing_filiere = get_by_id(self.db, filiere_id)
        if not existing_filiere:
            raise FiliereNotFoundError(filiere_id)
        delete(self.db, filiere_id)


# ---------- Liste ----------
    def get_all_filieres(self, skip: int = 0, limit: int = 100) -> List[FiliereRead]:
        """Récupère toutes les filières (paginé)."""
        filieres = get_all(self.db, skip, limit)
        return [FiliereRead.model_validate(f) for f in filieres]