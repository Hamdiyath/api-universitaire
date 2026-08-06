
# services/filiere_service.py - Logique métier pour Filiere


from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from crud.filiere import get_by_nom, get_by_id, create, update, delete
from schemas.filiere import FiliereCreate, FiliereUpdate, FiliereRead


# ---------- Création d'une filière ----------
def create_filiere(db: Session, filiere_data: FiliereCreate):
    """
    Crée une nouvelle filière.
    Vérifie que le nom n'existe pas déjà.
    """
    # 1. Vérifier si le nom existe déjà
    existing_filiere = get_by_nom(db, filiere_data.nom)
    if existing_filiere:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette filière existe déjà"
        )

    # 2. Créer la filière
    new_filiere = create(db, filiere_data.model_dump())
    return FiliereRead.model_validate(new_filiere)


# ---------- Récupération d'une filière par ID ----------
def get_filiere_by_id(db: Session, filiere_id: int):
    """
    Récupère une filière par son ID.
    Lève une exception si la filière n'existe pas.
    """
    filiere = get_by_id(db, filiere_id)
    if not filiere:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filière non trouvée"
        )
    return filiere


# ---------- Mise à jour d'une filière ----------
def update_filiere(db: Session, filiere_id: int, filiere_data: FiliereUpdate):
    """
    Met à jour une filière existante.
    Vérifie que la filière existe.
    Vérifie que le nouveau nom n'est pas déjà utilisé (si le nom est modifié).
    """
    # 1. Vérifier que la filière existe
    existing_filiere = get_by_id(db, filiere_id)
    if not existing_filiere:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filière non trouvée"
        )

    # 2. Convertir en dict et filtrer les champs None
    update_data = filiere_data.model_dump(exclude_unset=True)

    # 3. Si le nom est modifié, vérifier qu'il n'est pas déjà utilisé
    if "nom" in update_data and update_data["nom"] != existing_filiere.nom:
        nom_exists = get_by_nom(db, update_data["nom"])
        if nom_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce nom est déjà utilisé par une autre filière"
            )

    # 4. Mettre à jour la filière
    updated_filiere = update(db, filiere_id, update_data)
    return updated_filiere


# ---------- Suppression d'une filière ----------
def delete_filiere(db: Session, filiere_id: int):
    """
    Supprime une filière.
    Vérifie que la filière existe.
    """
    # 1. Vérifier que la filière existe
    existing_filiere = get_by_id(db, filiere_id)
    if not existing_filiere:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filière non trouvée"
        )

    # 2. Supprimer la filière
    delete(db, filiere_id)
    return None