# routes/inscription.py - Routes pures pour les inscriptions


from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas.inscription import InscriptionCreate, InscriptionRead
from schemas.response import ApiResponse
from controllers.inscription import InscriptionController

router = APIRouter(prefix="/inscriptions", tags=["Inscriptions"])


# ---------- 1. Inscrire un étudiant à une matière ----------
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[InscriptionRead])
def create_inscription(
    inscription_data: InscriptionCreate,
    db: Session = Depends(get_db)
):
    controller = InscriptionController(db)
    result = controller.inscrire_etudiant(inscription_data)
    return {"message": "Inscription créée avec succès", "data": result}


# ---------- 2. Récupérer les inscriptions d'un étudiant ----------
@router.get("/etudiant/{etudiant_id}", response_model=ApiResponse[List[InscriptionRead]])
def get_inscriptions_by_etudiant_route(
    etudiant_id: int,
    db: Session = Depends(get_db)
):
    controller = InscriptionController(db)
    result = controller.get_inscriptions_by_etudiant(etudiant_id)
    return {"message": "Inscriptions récupérées avec succès", "data": result}


# ---------- 3. Récupérer les inscriptions d'une matière ----------
@router.get("/matiere/{matiere_id}", response_model=ApiResponse[List[InscriptionRead]])
def get_inscriptions_by_matiere_route(
    matiere_id: int,
    db: Session = Depends(get_db)
):
    controller = InscriptionController(db)
    result = controller.get_inscriptions_by_matiere(matiere_id)
    return {"message": "Inscriptions récupérées avec succès", "data": result}


# ---------- 4. Récupérer toutes les inscriptions ----------
@router.get("/", response_model=ApiResponse[List[InscriptionRead]])
def get_all_inscriptions_route(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    controller = InscriptionController(db)
    result = controller.get_all_inscriptions(skip, limit)
    return {"message": "Inscriptions récupérées avec succès", "data": result}


# ---------- 5. Supprimer une inscription ----------
@router.delete("/{etudiant_id}/{matiere_id}/{semestre}", response_model=ApiResponse[None])
def delete_inscription(
    etudiant_id: int,
    matiere_id: int,
    semestre: str,
    db: Session = Depends(get_db)
):
    controller = InscriptionController(db)
    controller.supprimer_inscription(etudiant_id, matiere_id, semestre)
    return {"message": "Inscription supprimée avec succès", "data": None}
