# ============================================================
# controllers/note.py - Contrôleur des notes
# ============================================================
from services.note_service import NoteService


class NoteController:
    """
    Contrôleur pour les actions liées aux notes.
    Fait le lien entre la route et le service.
    Ne contient aucune logique métier.
    """
    def __init__(self, db):
        self.db = db
        self.service = NoteService(db)

    def create_note(self, note_data, current_user):
        return self.service.create_note(note_data, current_user)

    def get_notes_by_etudiant(self, etudiant_id, current_user, skip=0, limit=100):
        return self.service.get_notes_by_etudiant(etudiant_id, current_user, skip, limit)

    def get_notes_by_matiere(self, matiere_id, current_user, filiere_id=None, skip=0, limit=100):
        return self.service.get_notes_by_matiere(matiere_id, current_user, filiere_id, skip, limit)

    def get_all_notes(self, skip=0, limit=100):
        return self.service.get_all_notes(skip, limit)

    def get_note_by_id(self, note_id):
        return self.service.get_note_by_id(note_id)

    def update_note(self, note_id, note_data, current_user):
        return self.service.update_note(note_id, note_data, current_user)

    def delete_note(self, note_id):
        return self.service.delete_note(note_id)

    def get_notes_by_professeur(self, professeur_id, current_user, skip=0, limit=100):
        return self.service.get_notes_by_professeur(professeur_id, current_user, skip, limit)