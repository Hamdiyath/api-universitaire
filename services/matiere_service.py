# ============================================================
# services/matiere_service.py - Logique métier pour Matiere
# ============================================================

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from crud.matiere import get_by_nom, get_by_id, create, update, delete
from schemas.matiere import MatiereCreate, MatiereUpdate, MatiereRead


# ---------- Création d'une matière ----------
def create_matiere(db: Session, matiere_data: MatiereCreate):
    """
    Crée une nouvelle matière.
    Vérifie que le nom n'existe pas déjà.
    """
    # 1. Vérifier si le nom existe déjà
    existing_matiere = get_by_nom(db, matiere_data.nom)
    if existing_matiere:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette matière existe déjà"
        )

    # 2. Créer la matière
    new_matiere = create(db, matiere_data.model_dump())
    return MatiereRead.model_validate(new_matiere)


# ---------- Récupération d'une matière par ID ----------
def get_matiere_by_id(db: Session, matiere_id: int):
    """
    Récupère une matière par son ID.
    Lève une exception si la matière n'existe pas.
    """
    matiere = get_by_id(db, matiere_id)
    if not matiere:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cette matière n'existe pas"
        )
    return matiere


# ---------- Mise à jour d'une matière ----------
def update_matiere(db: Session, matiere_id: int, matiere_data: MatiereUpdate):
    """
    Met à jour une matière existante.
    Vérifie que la matière existe.
    Vérifie que le nouveau nom n'est pas déjà utilisé (si le nom est modifié).
    """
    # 1. Vérifier que la matière existe
    existing_matiere = get_by_id(db, matiere_id)
    if not existing_matiere:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cette matière n'existe pas"
        )

    # 2. Convertir en dict et filtrer les champs None
    update_data = matiere_data.model_dump(exclude_unset=True)

    # 3. Si le nom est modifié, vérifier qu'il n'est pas déjà utilisé
    if "nom" in update_data and update_data["nom"] != existing_matiere.nom:
        nom_exists = get_by_nom(db, update_data["nom"])
        if nom_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce nom est déjà utilisé par une autre matière"
            )

    # 4. Mettre à jour la matière
    updated_matiere = update(db, matiere_id, update_data)
    return updated_matiere


# ---------- Suppression d'une matière ----------
def delete_matiere(db: Session, matiere_id: int):
    """
    Supprime une matière.
    Vérifie que la matière existe.
    """
    # 1. Vérifier que la matière existe
    existing_matiere = get_by_id(db, matiere_id)
    if not existing_matiere:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matière non trouvée"
        )

    # 2. Supprimer la matière
    delete(db, matiere_id)
    return None