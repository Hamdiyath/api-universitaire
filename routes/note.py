# routes/notes.py - Routes pour la gestion des notes


from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.user import User
from schemas.note import NoteCreate, NoteUpdate, NoteRead
from controllers.note import NoteController
from core.dependencies import get_current_user, require_role
from schemas.response import ApiResponse

router = APIRouter(prefix="/notes", tags=["Notes"])


# ---------- 1. Créer une note ----------
# Permission : Professeur, Admin, Scolarité
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[NoteRead])
def create_new_note(
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["professeur", "admin", "scolarite"]))
):
    """
    Crée une nouvelle note.
    - Professeur : ne peut créer que pour ses matières
    - Admin/Scolarité : peuvent créer pour toutes les matières
    """
    controller = NoteController(db)
    result = controller.create_note(note_data, current_user)
    return ApiResponse(success=True, message="Note créée avec succès", data=result)


# ---------- 2. Voir les notes d'un étudiant ----------
# Permission : Étudiant (soi-même), Professeur (même filière), Admin, Scolarité
@router.get("/etudiant/{etudiant_id}", response_model=ApiResponse[List[NoteRead]])
def get_etudiant_notes(
    etudiant_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les notes d'un étudiant.
    - Étudiant : voit uniquement ses propres notes
    - Professeur : voit les notes des étudiants de sa filière
    - Admin/Scolarité : voit toutes les notes
    """
    controller = NoteController(db)
    result = controller.get_notes_by_etudiant(etudiant_id, current_user, skip, limit)
    return ApiResponse(success=True, message="Notes récupérées avec succès", data=result)


# ---------- 3. Voir les notes d'une matière ----------
# Permission : Professeur (s'il enseigne la matière), Admin, Scolarité
@router.get("/matiere/{matiere_id}", response_model=ApiResponse[List[NoteRead]])
def get_matiere_notes(
    matiere_id: int,
    filiere_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["professeur", "admin", "scolarite"]))
):
    """
    Récupère les notes d'une matière.
    - Option : filtrer par filière_id
    - Professeur : ne voit que les étudiants de sa filière
    - Admin/Scolarité : voit tous les étudiants
    """
    controller = NoteController(db)
    result = controller.get_notes_by_matiere(matiere_id, current_user, filiere_id, skip, limit)
    return ApiResponse(success=True, message="Notes récupérées avec succès", data=result)


# ---------- 4. Voir les notes saisies par un professeur ----------
# Permission : Professeur (soi-même), Admin, Scolarité
@router.get("/professeur/{professeur_id}", response_model=ApiResponse[List[NoteRead]])
def get_professeur_notes(
    professeur_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les notes saisies par un professeur.
    - Un professeur ne peut voir que ses propres saisies
    - Admin/Scolarité peuvent voir toutes les saisies
    """
    controller = NoteController(db)
    result = controller.get_notes_by_professeur(professeur_id, current_user, skip, limit)
    return ApiResponse(success=True, message="Notes récupérées avec succès", data=result)


# ---------- 5. Voir toutes les notes ----------
# Permission : Admin, Scolarité
@router.get("/", response_model=ApiResponse[List[NoteRead]])
def get_all_notes_route(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    """
    Récupère toutes les notes (paginé).
    Réservé à l'Admin et à la Scolarité.
    """
    controller = NoteController(db)
    result = controller.get_all_notes(skip, limit)
    return ApiResponse(success=True, message="Notes récupérées avec succès", data=result)


# ---------- 6. Voir une note par ID ----------
# Permission : Professeur, Admin, Scolarité
@router.get("/{note_id}", response_model=ApiResponse[NoteRead])
def get_note_by_id_route(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["professeur", "admin", "scolarite"]))
):
    """
    Récupère une note par son ID.
    Réservé aux professeurs, administrateurs et scolarité.
    """
    controller = NoteController(db)
    result = controller.get_note_by_id(note_id)
    return ApiResponse(success=True, message="Note récupérée avec succès", data=result)


# ---------- 7. Modifier une note ----------
# Permission : Professeur (sa note, délai 7 jours), Admin, Scolarité
@router.put("/{note_id}", response_model=ApiResponse[NoteRead])
def update_existing_note(
    note_id: int,
    note_data: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["professeur", "admin", "scolarite"]))
):
    """
    Modifie une note existante.
    - Professeur : peut modifier ses propres notes (délai 7 jours)
    - Admin/Scolarité : peuvent modifier toutes les notes
    """
    controller = NoteController(db)
    result = controller.update_note(note_id, note_data, current_user)
    return ApiResponse(success=True, message="Note mise à jour avec succès", data=result)


# ---------- 8. Supprimer une note ----------
# Permission : Admin, Scolarité
@router.delete("/{note_id}", response_model=ApiResponse[None])
def delete_existing_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Supprime une note.
    Réservé à l'Admin.
    """
    controller = NoteController(db)
    controller.delete_note(note_id)
    return ApiResponse(success=True, message="Note supprimée avec succès", data=None)