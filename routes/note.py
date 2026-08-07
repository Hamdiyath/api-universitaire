# ============================================================
# routes/notes.py - Routes pour la gestion des notes
# ============================================================

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from schemas.note import NoteCreate, NoteUpdate, NoteRead
from services.note_service import (
    create_note,
    get_notes_by_etudiant,
    get_notes_by_matiere,
    get_notes_by_professeur,
    get_all_notes,
    get_note_by_id,
    update_note,
    delete_note
)
from core.dependencies import get_current_user, require_role
from core.handlers import handle_request
from schemas.response import ApiResponse

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[NoteRead])
def create_new_note(
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["professeur", "admin", "scolarite"]))
):
    return handle_request(create_note, "Note créée avec succès", db, note_data, current_user)


@router.get("/etudiant/{etudiant_id}", response_model=ApiResponse[List[NoteRead]])
def get_etudiant_notes(
    etudiant_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return handle_request(get_notes_by_etudiant, "Notes récupérées avec succès", db, etudiant_id, current_user, skip, limit)


@router.get("/matiere/{matiere_id}", response_model=ApiResponse[List[NoteRead]])
def get_matiere_notes(
    matiere_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["professeur", "admin", "scolarite"]))
):
    return handle_request(
        get_notes_by_matiere,
        "Notes récupérées avec succès",
        db,
        matiere_id,
        current_user,  # ← AJOUTER current_user
        skip,
        limit
    )


@router.get("/professeur/{professeur_id}", response_model=ApiResponse[List[NoteRead]])
def get_professeur_notes(
    professeur_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return handle_request(get_notes_by_professeur, "Notes récupérées avec succès", db, professeur_id, current_user, skip, limit)


@router.get("/", response_model=ApiResponse[List[NoteRead]])
def get_all_notes_route(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    return handle_request(get_all_notes, "Notes récupérées avec succès", db, skip, limit)


@router.get("/{note_id}", response_model=ApiResponse[NoteRead])
def get_note_by_id_route(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["professeur", "admin", "scolarite"]))
):
    return handle_request(get_note_by_id, "Note récupérée avec succès", db, note_id)


@router.put("/{note_id}", response_model=ApiResponse[NoteRead])
def update_existing_note(
    note_id: int,
    note_data: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["professeur", "admin", "scolarite"]))
):
    return handle_request(update_note, "Note mise à jour avec succès", db, note_id, note_data)


@router.delete("/{note_id}", response_model=ApiResponse[None])
def delete_existing_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "scolarite"]))
):
    return handle_request(delete_note, "Note supprimée avec succès", db, note_id)