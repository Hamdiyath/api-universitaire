# ============================================================
# services/note_service.py - Logique métier pour Note
# ============================================================

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime, timezone

from crud.note import get_by_id, get_by_etudiant, get_all, create, update, delete, get_by_professeur, Note
from crud.user import get_by_id as get_user_by_id, get_by_filiere
from crud.matiere import get_by_id as get_matiere_by_id
from crud.matiere_filiere import get_by_matiere as get_filieres_by_matiere
from schemas.note import NoteCreate, NoteUpdate, NoteRead


# ============================================================
# FONCTIONS DE VÉRIFICATION DES PERMISSIONS
# ============================================================

def can_view_etudiant_notes(db: Session, current_user, etudiant_id: int) -> bool:
    """
    Vérifie si l'utilisateur peut voir les notes d'un étudiant.
    - Soi-même : OUI
    - Admin ou Scolarité : OUI
    - Professeur : OUI si l'étudiant est dans la même filière que lui
    """
    user_roles = [role.name for role in current_user.roles]

    # 1. Soi-même
    if current_user.id == etudiant_id:
        return True

    # 2. Admin ou Scolarité
    if any(role in user_roles for role in ["admin", "scolarite"]):
        return True

    # 3. Professeur : vérifier si l'étudiant est dans la même filière
    if "professeur" in user_roles:
        # Récupérer l'étudiant
        etudiant = get_user_by_id(db, etudiant_id)
        if not etudiant or not etudiant.filiere_id:
            return False

        # Récupérer les matières enseignées par le professeur
        from crud.enseignement import get_by_professeur as get_enseignements_prof
        enseignements = get_enseignements_prof(db, current_user.id)
        matiere_ids = [e.matiere_id for e in enseignements]

        if not matiere_ids:
            return False

        # Pour chaque matière enseignée, vérifier si elle est dans la filière de l'étudiant
        for matiere_id in matiere_ids:
            filieres = get_filieres_by_matiere(db, matiere_id)
            filiere_ids = [f.filiere_id for f in filieres]
            if etudiant.filiere_id in filiere_ids:
                return True

    return False


def can_view_matiere_notes(db: Session, current_user, matiere_id: int) -> bool:
    """
    Vérifie si l'utilisateur peut voir les notes d'une matière.
    - Admin ou Scolarité : OUI
    - Professeur : OUI s'il enseigne cette matière
    """
    user_roles = [role.name for role in current_user.roles]

    if any(role in user_roles for role in ["admin", "scolarite"]):
        return True

    if "professeur" in user_roles:
        from crud.enseignement import get_by_professeur_and_matiere
        enseignement = get_by_professeur_and_matiere(db, current_user.id, matiere_id)
        if enseignement:
            return True

    return False


def can_modify_note(db: Session, current_user, note_id: int) -> bool:
    """
    Vérifie si l'utilisateur peut modifier une note.
    - Admin ou Scolarité : OUI
    - Professeur : OUI si c'est sa note ET délai non dépassé (7 jours)
    """
    user_roles = [role.name for role in current_user.roles]

    if any(role in user_roles for role in ["admin", "scolarite"]):
        return True

    if "professeur" in user_roles:
        note = get_by_id(db, note_id)
        if not note:
            return False
        if note.professeur_id != current_user.id:
            return False
        # Délai de modification : 7 jours après la saisie
        if note.date_saisie and (datetime.now(timezone.utc) - note.date_saisie).days > 7:
            return False
        return True

    return False


# ============================================================
# FONCTIONS MÉTIER
# ============================================================

def create_note(db: Session, note_data: NoteCreate, current_user) -> NoteRead:
    """
    Crée une nouvelle note.
    - Vérifie l'existence de l'étudiant, la matière et le professeur
    - Si l'utilisateur est professeur, on impose son ID (évite la fraude)
    """
    user_roles = [role.name for role in current_user.roles]

    # 1. Vérifier que l'étudiant existe
    etudiant = get_user_by_id(db, note_data.etudiant_id)
    if not etudiant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Étudiant non trouvé")

    # 2. Vérifier que la matière existe
    matiere = get_matiere_by_id(db, note_data.matiere_id)
    if not matiere:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matière non trouvée")

    # 3. Si l'utilisateur est professeur (pas admin/scolarité), imposer son ID
    if "professeur" in user_roles and "admin" not in user_roles and "scolarite" not in user_roles:
        professeur_id = current_user.id
        from crud.enseignement import get_by_professeur_and_matiere
        enseignement = get_by_professeur_and_matiere(db, professeur_id, note_data.matiere_id)
        if not enseignement:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous n'enseignez pas cette matière"
            )
    else:
        # Admin ou Scolarité : on utilise l'ID fourni dans la requête
        professeur_id = note_data.professeur_id
        professeur = get_user_by_id(db, professeur_id)
        if not professeur:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professeur non trouvé")

    # 4. Créer la note avec le bon professeur_id
    note_dict = note_data.model_dump()
    note_dict["professeur_id"] = professeur_id
    new_note = create(db, note_dict)
    return NoteRead.model_validate(new_note)


def get_notes_by_etudiant(db: Session, etudiant_id: int, current_user, skip: int = 0, limit: int = 100) -> List[NoteRead]:
    """
    Récupère les notes d'un étudiant avec vérification des permissions.
    """
    if not can_view_etudiant_notes(db, current_user, etudiant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas l'autorisation de voir les notes de cet étudiant"
        )

    etudiant = get_user_by_id(db, etudiant_id)
    if not etudiant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Étudiant non trouvé")

    notes = get_by_etudiant(db, etudiant_id, skip, limit)
    return [NoteRead.model_validate(note) for note in notes]


def get_notes_by_matiere(
    db: Session,
    matiere_id: int,
    current_user,
    filiere_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[NoteRead]:
    """
    Récupère les notes d'une matière avec vérification des permissions.
    Filtré par filière (si fourni).
    """
    if not can_view_matiere_notes(db, current_user, matiere_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas l'autorisation de voir les notes de cette matière"
        )

    matiere = get_matiere_by_id(db, matiere_id)
    if not matiere:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matière non trouvée")

    # 1. Récupérer les étudiants de la filière (ou de toutes les filières)
    if filiere_id is not None:
        etudiants = get_by_filiere(db, filiere_id)
    else:
        # Si pas de filière spécifiée, récupérer tous les étudiants
        from crud.user import get_all as get_all_users
        tous_etudiants = get_all_users(db)
        etudiants = [u for u in tous_etudiants if "etudiant" in [r.name for r in u.roles]]

    etudiant_ids = [u.id for u in etudiants]

    if not etudiant_ids:
        return []

    # 2. Construire la requête de base
    query = db.query(Note).filter(
        Note.matiere_id == matiere_id,
        Note.etudiant_id.in_(etudiant_ids)
    )

    # 3. Appliquer la pagination
    notes = query.offset(skip).limit(limit).all()

    return [NoteRead.model_validate(note) for note in notes]


def get_all_notes(db: Session, skip: int = 0, limit: int = 100) -> List[NoteRead]:
    """
    Récupère toutes les notes (Admin/Scolarité uniquement).
    """
    notes = get_all(db, skip, limit)
    return [NoteRead.model_validate(note) for note in notes]


def get_note_by_id(db: Session, note_id: int) -> NoteRead:
    """
    Récupère une note par son ID.
    """
    note = get_by_id(db, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note non trouvée")
    return NoteRead.model_validate(note)


def update_note(db: Session, note_id: int, note_data: NoteUpdate, current_user) -> NoteRead:
    """
    Met à jour une note avec vérification des permissions et des délais.
    """
    if not can_modify_note(db, current_user, note_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas l'autorisation de modifier cette note"
        )

    update_data = note_data.model_dump(exclude_unset=True)
    updated_note = update(db, note_id, update_data)
    return NoteRead.model_validate(updated_note)


def delete_note(db: Session, note_id: int):
    """
    Supprime une note (Admin/Scolarité uniquement).
    """
    existing_note = get_by_id(db, note_id)
    if not existing_note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note non trouvée")

    delete(db, note_id)
    return None


def get_notes_by_professeur(db: Session, professeur_id: int, current_user, skip: int = 0, limit: int = 100) -> List[NoteRead]:
    """
    Récupère les notes saisies par un professeur avec vérification des permissions.
    """
    user_roles = [role.name for role in current_user.roles]

    if current_user.id != professeur_id and "admin" not in user_roles and "scolarite" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas l'autorisation de voir les notes de ce professeur"
        )

    professeur = get_user_by_id(db, professeur_id)
    if not professeur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professeur non trouvé")

    notes = get_by_professeur(db, professeur_id, skip, limit)
    return [NoteRead.model_validate(note) for note in notes]