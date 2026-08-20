
# services/resultat_matiere_service.py - Logique métier ResultatMatiere

from sqlalchemy.orm import Session
from typing import List

import crud.resultat_matiere as resultat_crud
import crud.user as user_crud
from crud.matiere_filiere import get_by_filiere as get_matieres_by_filiere

from schemas.resultat_matiere import ResultatMatiereRead
from models.enums import SessionNote, StatutValidation

from exceptions.base import (
    UserNotFoundError,
    FiliereRequiredError,
    PermissionDeniedError,
    ResultatMatiereNotFoundError,  # à créer dans exceptions/base.py
)


class ResultatMatiereService:
    """Service de gestion des lignes de résultat par matière."""

    def __init__(self, db: Session):
        self.db = db

    # ---------- Génération en bloc ----------
    def generer_resultats_etudiant(
        self,
        etudiant_id: int,
        semestre: str,
        annee_universitaire: str,
        current_user
    ) -> List[ResultatMatiereRead]:
        """
        Génère les lignes de résultat à blanc pour un étudiant, pour toutes
        les matières de sa filière correspondant au semestre donné.
        N'écrase pas les lignes déjà existantes (idempotent).

        Permissions :
        - Admin/Scolarité : n'importe quel étudiant
        - Professeur : uniquement les étudiants dont la filière comprend
          au moins une matière qu'il enseigne
        - Étudiant : aucun accès (acte purement administratif)
        """
        etudiant = user_crud.get_by_id(self.db, etudiant_id)
        if not etudiant:
            raise UserNotFoundError(etudiant_id)

        if not etudiant.filiere_id:
            raise FiliereRequiredError()

        user_roles = [role.name for role in current_user.roles]

        if not any(r in user_roles for r in ["admin", "scolarite"]):
            if "professeur" in user_roles:
                from crud.enseignement import get_by_professeur
                enseignements = get_by_professeur(self.db, current_user.id)
                matiere_ids_prof = [e.matiere_id for e in enseignements]

                associations_filiere = get_matieres_by_filiere(self.db, etudiant.filiere_id)
                matiere_ids_filiere = [a.matiere_id for a in associations_filiere]

                if not any(mid in matiere_ids_filiere for mid in matiere_ids_prof):
                    raise PermissionDeniedError(
                        "Vous n'enseignez aucune matière de la filière de cet étudiant"
                    )
            else:
                raise PermissionDeniedError(
                    "Vous n'avez pas l'autorisation de générer ces résultats"
                )

        associations = get_matieres_by_filiere(self.db, etudiant.filiere_id)
        matiere_ids = [a.matiere_id for a in associations if a.semestre == semestre]

        lignes_creees = []
        for matiere_id in matiere_ids:
            existing = resultat_crud.get_by_etudiant_matiere_semestre_annee(
                self.db, etudiant_id, matiere_id, semestre, annee_universitaire
            )
            if existing:
                continue

            nouvelle_ligne = resultat_crud.create(self.db, {
                "etudiant_id": etudiant_id,
                "matiere_id": matiere_id,
                "semestre": semestre,
                "annee_universitaire": annee_universitaire,
                "session_actuelle": SessionNote.NORMALE,
                "statut": StatutValidation.NON_NOTE,
                "moyenne": None
            })
            lignes_creees.append(nouvelle_ligne)

        return [ResultatMatiereRead.model_validate(r) for r in lignes_creees]

    # ---------- Lecture ----------
    def get_by_id(self, resultat_id: int) -> ResultatMatiereRead:
        """Récupère une ligne de résultat par son ID."""
        resultat = resultat_crud.get_by_id(self.db, resultat_id)
        if not resultat:
            raise ResultatMatiereNotFoundError()
        return ResultatMatiereRead.model_validate(resultat)

    def get_resultats_by_etudiant(self, etudiant_id: int, current_user) -> List[ResultatMatiereRead]:
        """
        Récupère toutes les lignes de résultat d'un étudiant.
        - Étudiant : uniquement les siennes
        - Admin/Scolarité/Professeur : n'importe lequel
        """
        user_roles = [role.name for role in current_user.roles]
        if current_user.id != etudiant_id and not any(r in user_roles for r in ["admin", "scolarite", "professeur"]):
            raise PermissionDeniedError("Vous n'avez pas l'autorisation de voir ces résultats")

        etudiant = user_crud.get_by_id(self.db, etudiant_id)
        if not etudiant:
            raise UserNotFoundError(etudiant_id)

        resultats = resultat_crud.get_by_etudiant(self.db, etudiant_id)
        return [ResultatMatiereRead.model_validate(r) for r in resultats]

    def get_resultats_by_matiere(self, matiere_id: int) -> List[ResultatMatiereRead]:
        """Récupère toutes les lignes de résultat pour une matière (vue professeur/admin)."""
        resultats = resultat_crud.get_by_matiere(self.db, matiere_id)
        return [ResultatMatiereRead.model_validate(r) for r in resultats]

    def get_all_resultats(self, skip: int = 0, limit: int = 100) -> List[ResultatMatiereRead]:
        """Récupère toutes les lignes de résultat (paginé)."""
        resultats = resultat_crud.get_all(self.db, skip, limit)
        return [ResultatMatiereRead.model_validate(r) for r in resultats]

    # ---------- Suppression ----------
    def supprimer_resultat(self, resultat_id: int) -> None:
        """Supprime une ligne de résultat par son ID."""
        existing = resultat_crud.get_by_id(self.db, resultat_id)
        if not existing:
            raise ResultatMatiereNotFoundError()
        resultat_crud.delete(self.db, resultat_id)