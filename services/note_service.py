# ============================================================
# services/note_service.py - Logique métier pour Note
# ============================================================

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from crud.note import get_by_id, get_by_etudiant, get_all, create, update, delete, get_by_professeur, Note
from crud.user import get_by_id as get_user_by_id, get_by_filiere, get_all as get_all_users
from crud.matiere import get_by_id as get_matiere_by_id
from crud.matiere_filiere import get_by_matiere as get_filieres_by_matiere
from crud.enseignement import get_by_professeur as get_enseignements_prof, get_by_professeur_and_matiere
from schemas.note import NoteCreate, NoteUpdate, NoteRead

from exceptions.base import (
    UserNotFoundError,
    MatiereNotFoundError,
    NoteNotFoundError,
    EnseignementNotFoundError,
    NoteModificationDeniedError,
    NoteModificationDelayError,
    PermissionDeniedError,  # ⚠️ à créer dans exceptions/base.py (voir note en dessous)
)


class NoteService:
    """Service de gestion des notes. Contient toute la logique métier."""

    def __init__(self, db: Session):
        self.db = db

    # VÉRIFICATIONS DE PERMISSIONS (privées, retournent un bool)


    def _can_view_etudiant_notes(self, current_user, etudiant_id: int) -> bool:
        user_roles = [role.name for role in current_user.roles]

        if current_user.id == etudiant_id:
            return True

        if any(role in user_roles for role in ["admin", "scolarite"]):
            return True

        if "professeur" in user_roles:
            etudiant = get_user_by_id(self.db, etudiant_id)
            if not etudiant or not etudiant.filiere_id:
                return False

            enseignements = get_enseignements_prof(self.db, current_user.id)
            matiere_ids = [e.matiere_id for e in enseignements]
            if not matiere_ids:
                return False

            for matiere_id in matiere_ids:
                filieres = get_filieres_by_matiere(self.db, matiere_id)
                filiere_ids = [f.filiere_id for f in filieres]
                if etudiant.filiere_id in filiere_ids:
                    return True

        return False

    def _can_view_matiere_notes(self, current_user, matiere_id: int) -> bool:
        user_roles = [role.name for role in current_user.roles]

        if any(role in user_roles for role in ["admin", "scolarite"]):
            return True

        if "professeur" in user_roles:
            enseignement = get_by_professeur_and_matiere(self.db, current_user.id, matiere_id)
            if enseignement:
                return True

        return False

    def _can_modify_note(self, current_user, note_id: int) -> bool:
        user_roles = [role.name for role in current_user.roles]

        if any(role in user_roles for role in ["admin", "scolarite"]):
            return True

        if "professeur" in user_roles:
            note = get_by_id(self.db, note_id)
            if not note:
                return False
            if note.professeur_id != current_user.id:
                return False
            if note.date_saisie and (datetime.now(timezone.utc) - note.date_saisie).days > 7:
                return False
            return True

        return False

    # ============================================================
    # FONCTIONS MÉTIER
    # ============================================================

    def create_note(self, note_data: NoteCreate, current_user) -> NoteRead:
        user_roles = [role.name for role in current_user.roles]

        etudiant = get_user_by_id(self.db, note_data.etudiant_id)
        if not etudiant:
            raise UserNotFoundError(note_data.etudiant_id)

        matiere = get_matiere_by_id(self.db, note_data.matiere_id)
        if not matiere:
            raise MatiereNotFoundError(note_data.matiere_id)

        if "professeur" in user_roles and "admin" not in user_roles and "scolarite" not in user_roles:
            professeur_id = current_user.id
            enseignement = get_by_professeur_and_matiere(self.db, professeur_id, note_data.matiere_id)
            if not enseignement:
                raise EnseignementNotFoundError(note_data.matiere_id)
        else:
            professeur_id = note_data.professeur_id
            professeur = get_user_by_id(self.db, professeur_id)
            if not professeur:
                raise UserNotFoundError(professeur_id)

        note_dict = note_data.model_dump()
        note_dict["professeur_id"] = professeur_id
        new_note = create(self.db, note_dict)
        return NoteRead.model_validate(new_note)

    def get_notes_by_etudiant(self, etudiant_id: int, current_user, skip: int = 0, limit: int = 100) -> List[NoteRead]:
        if not self._can_view_etudiant_notes(current_user, etudiant_id):
            raise PermissionDeniedError("Vous n'avez pas l'autorisation de voir les notes de cet étudiant")

        etudiant = get_user_by_id(self.db, etudiant_id)
        if not etudiant:
            raise UserNotFoundError(etudiant_id)

        notes = get_by_etudiant(self.db, etudiant_id, skip, limit)
        return [NoteRead.model_validate(note) for note in notes]

    def get_notes_by_matiere(
        self,
        matiere_id: int,
        current_user,
        filiere_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[NoteRead]:
        if not self._can_view_matiere_notes(current_user, matiere_id):
            raise PermissionDeniedError("Vous n'avez pas l'autorisation de voir les notes de cette matière")

        matiere = get_matiere_by_id(self.db, matiere_id)
        if not matiere:
            raise MatiereNotFoundError(matiere_id)

        if filiere_id is not None:
            etudiants = get_by_filiere(self.db, filiere_id)
        else:
            tous_etudiants = get_all_users(self.db)
            etudiants = [u for u in tous_etudiants if "etudiant" in [r.name for r in u.roles]]

        etudiant_ids = [u.id for u in etudiants]
        if not etudiant_ids:
            return []

        query = self.db.query(Note).filter(
            Note.matiere_id == matiere_id,
            Note.etudiant_id.in_(etudiant_ids)
        )
        notes = query.offset(skip).limit(limit).all()
        return [NoteRead.model_validate(note) for note in notes]

    def get_all_notes(self, skip: int = 0, limit: int = 100) -> List[NoteRead]:
        notes = get_all(self.db, skip, limit)
        return [NoteRead.model_validate(note) for note in notes]

    def get_note_by_id(self, note_id: int) -> NoteRead:
        note = get_by_id(self.db, note_id)
        if not note:
            raise NoteNotFoundError(note_id)
        return NoteRead.model_validate(note)

    def update_note(self, note_id: int, note_data: NoteUpdate, current_user) -> NoteRead:
        note = get_by_id(self.db, note_id)
        if not note:
            raise NoteNotFoundError(note_id)

        if not self._can_modify_note(current_user, note_id):
            # Distinguer refus pur / délai dépassé, comme avant
            if note.professeur_id == current_user.id and note.date_saisie and \
               (datetime.now(timezone.utc) - note.date_saisie).days > 7:
                raise NoteModificationDelayError()
            raise NoteModificationDeniedError()

        update_data = note_data.model_dump(exclude_unset=True)
        updated_note = update(self.db, note_id, update_data)
        return NoteRead.model_validate(updated_note)

    def delete_note(self, note_id: int) -> None:
        existing_note = get_by_id(self.db, note_id)
        if not existing_note:
            raise NoteNotFoundError(note_id)
        delete(self.db, note_id)

    def get_notes_by_professeur(self, professeur_id: int, current_user, skip: int = 0, limit: int = 100) -> List[NoteRead]:
        user_roles = [role.name for role in current_user.roles]

        if current_user.id != professeur_id and "admin" not in user_roles and "scolarite" not in user_roles:
            raise PermissionDeniedError("Vous n'avez pas l'autorisation de voir les notes de ce professeur")

        professeur = get_user_by_id(self.db, professeur_id)
        if not professeur:
            raise UserNotFoundError(professeur_id)

        notes = get_by_professeur(self.db, professeur_id, skip, limit)
        return [NoteRead.model_validate(note) for note in notes]