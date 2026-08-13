
# services/bulletin_service.py - Service de calcul des bulletins


from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from crud.note import get_by_etudiant_and_matiere
from crud.matiere import get_by_id as get_matiere_by_id
from crud.user import get_by_id as get_user_by_id, get_by_filiere, get_all as get_all_users
from crud.resultat_semestre import get_by_etudiant_semestre, create as create_resultat, update as update_resultat
from crud.matiere_filiere import get_by_filiere as get_matieres_by_filiere, get_by_matiere as get_filieres_by_matiere
from crud.enseignement import get_by_professeur_and_matiere
from crud.filiere import get_by_id as get_filiere_by_id
from models.enums import SessionNote
from schemas.resultat_semestre import ResultatSemestreCreate, ResultatSemestreRead

from exceptions.base import (
    UserNotFoundError,
    FiliereNotFoundError,
    MatiereNotFoundError,
    FiliereRequiredError,
    PermissionDeniedError,
)

# ---------- Constante pour le seuil de validation ----------
SEUIL_VALIDATION = 12


# ============================================================
# FONCTION DE CALCUL PUR (ne touche pas à la base de données)
# ============================================================

def get_meilleure_note(notes: List[Dict]) -> Optional[float]:
    """
    Retourne la meilleure note entre la session normale et le rattrapage.
    Ignore les notes de type 'reprise'.
    """
    notes_filtrees = [n for n in notes if n.get("session") != SessionNote.REPRISE.value]
    if not notes_filtrees:
        return None
    return max(n["valeur"] for n in notes_filtrees)


class BulletinService:
    """Service de calcul et génération des bulletins. Contient toute la logique métier."""

    def __init__(self, db: Session):
        self.db = db

    # ============================================================
    # FONCTIONS DE CALCUL
    # ============================================================

    def calculer_moyenne_matiere(self, etudiant_id: int, matiere_id: int) -> Dict[str, Any]:
        """
        Calcule la moyenne d'un étudiant pour une matière donnée.
        Règles de Lokossa :
        - Seuil de validation = 12
        - Pas de compensation : chaque matière est validée individuellement
        - Rattrapage écrase la matière (si présent)
        - Reprise écrase aussi (si présent)
        """
        notes = get_by_etudiant_and_matiere(self.db, etudiant_id, matiere_id)

        if not notes:
            return {
                "matiere_id": matiere_id,
                "moyenne": None,
                "notes": {},
                "statut": "NON NOTÉ"
            }

        # 1. VÉRIFIER S'IL Y A UNE NOTE DE REPRISE (priorité maximale)
        note_reprise = None
        for note in notes:
            if note.session.value == SessionNote.REPRISE.value:
                note_reprise = note
                break

        if note_reprise:
            return {
                "matiere_id": matiere_id,
                "moyenne": round(note_reprise.valeur, 2),
                "notes": {"Reprise": note_reprise.valeur},
                "statut": "VALIDÉ" if note_reprise.valeur >= SEUIL_VALIDATION else "NON VALIDE"
            }

        # 2. VÉRIFIER S'IL Y A UNE NOTE DE RATTRAPAGE
        note_rattrapage = None
        for note in notes:
            if note.session.value == SessionNote.RATTRAPAGE.value:
                note_rattrapage = note
                break

        if note_rattrapage:
            return {
                "matiere_id": matiere_id,
                "moyenne": round(note_rattrapage.valeur, 2),
                "notes": {"Rattrapage": note_rattrapage.valeur},
                "statut": "VALIDÉ" if note_rattrapage.valeur >= SEUIL_VALIDATION else "NON VALIDE"
            }

        # 3. PAS DE RATTRAPAGE NI DE REPRISE → CALCUL NORMAL
        notes_par_type = {}
        for note in notes:
            type_note = note.type_note
            if type_note not in notes_par_type:
                notes_par_type[type_note] = []
            notes_par_type[type_note].append({
                "valeur": note.valeur,
                "session": note.session.value if hasattr(note.session, 'value') else note.session,
                "id": note.id
            })

        meilleures_notes = {}
        for type_note, notes_list in notes_par_type.items():
            meilleures_notes[type_note] = get_meilleure_note(notes_list)

        notes_valides = [v for v in meilleures_notes.values() if v is not None]
        if not notes_valides:
            moyenne = None
            statut = "NON NOTÉ"
        else:
            moyenne = sum(notes_valides) / len(notes_valides)
            statut = "VALIDÉ" if moyenne >= SEUIL_VALIDATION else "NON VALIDE"

        return {
            "matiere_id": matiere_id,
            "moyenne": round(moyenne, 2) if moyenne is not None else None,
            "notes": meilleures_notes,
            "statut": statut
        }

    def calculer_moyenne_semestre(self, etudiant_id: int, semestre: str, annee_universitaire: str) -> Dict[str, Any]:
        """
        Calcule la moyenne d'un semestre pour un étudiant.
        Règles de Lokossa :
        - Pas de compensation : le semestre n'est validé que si TOUTES les matières sont validées
        - Chaque matière est validée si sa moyenne ≥ 12
        """
        etudiant = get_user_by_id(self.db, etudiant_id)
        if not etudiant:
            raise UserNotFoundError(etudiant_id)

        if not etudiant.filiere_id:
            raise FiliereRequiredError()

        associations = get_matieres_by_filiere(self.db, etudiant.filiere_id)
        matiere_ids = [a.matiere_id for a in associations if a.semestre == semestre]

        if not matiere_ids:
            return {
                "etudiant_id": etudiant_id,
                "semestre": semestre,
                "annee_universitaire": annee_universitaire,
                "matieres": [],
                "moyenne_semestre": None,
                "statut": "AUCUNE MATIERE",
                "a_passe_rattrapage": False
            }

        matieres = []
        for matiere_id in matiere_ids:
            matiere = get_matiere_by_id(self.db, matiere_id)
            if matiere:
                matieres.append(matiere)

        if not matieres:
            return {
                "etudiant_id": etudiant_id,
                "semestre": semestre,
                "annee_universitaire": annee_universitaire,
                "matieres": [],
                "moyenne_semestre": None,
                "statut": "AUCUNE MATIERE",
                "a_passe_rattrapage": False
            }

        resultats_matieres = []
        toutes_validees = True
        a_passe_rattrapage = False
        somme_moyennes_ponderees = 0
        somme_coefficients = 0
        credits_obtenus = 0
        credits_total = 0

        for matiere in matieres:
            resultat = self.calculer_moyenne_matiere(etudiant_id, matiere.id)
            resultat["matiere_nom"] = matiere.nom
            resultat["coefficient"] = matiere.coefficient if hasattr(matiere, 'coefficient') else 1.0
            resultat["credits"] = matiere.credits if hasattr(matiere, 'credits') else 0

            credits_total += resultat["credits"]

            if resultat["moyenne"] is not None:
                if resultat["statut"] == "VALIDÉ":
                    credits_obtenus += resultat["credits"]
                else:
                    toutes_validees = False

                if resultat.get("notes", {}).get("Rattrapage") is not None:
                    a_passe_rattrapage = True

                coeff = resultat["coefficient"]
                somme_moyennes_ponderees += resultat["moyenne"] * coeff
                somme_coefficients += coeff

            resultats_matieres.append(resultat)

        if somme_coefficients > 0:
            moyenne_semestre = somme_moyennes_ponderees / somme_coefficients
        else:
            moyenne_semestre = None

        if not resultats_matieres:
            statut = "AUCUNE MATIERE"
        elif toutes_validees:
            statut = "VALIDÉ"
        else:
            statut = "NON VALIDE"

        return {
            "etudiant_id": etudiant_id,
            "semestre": semestre,
            "annee_universitaire": annee_universitaire,
            "matieres": resultats_matieres,
            "moyenne_semestre": round(moyenne_semestre, 2) if moyenne_semestre is not None else None,
            "statut": statut,
            "a_passe_rattrapage": a_passe_rattrapage,
            "credits_obtenus": credits_obtenus,
            "credits_total": credits_total
        }

    # ============================================================
    # FONCTIONS DE GÉNÉRATION DE BULLETIN
    # ============================================================



    def sauvegarder_resultat_semestre(self, etudiant_id: int, semestre: str, annee_universitaire: str) -> Dict[str, Any]:
        """Sauvegarde le résultat d'un semestre dans la table resultats_semestre."""
        etudiant = get_user_by_id(self.db, etudiant_id)
        if not etudiant:
            raise UserNotFoundError(etudiant_id)

        resultats = self.calculer_moyenne_semestre(etudiant_id, semestre, annee_universitaire)

        existing = get_by_etudiant_semestre(self.db, etudiant_id, semestre, annee_universitaire)

        if existing:
            update_data = {
                "moyenne_semestre": resultats["moyenne_semestre"],
                "statut": resultats["statut"],
                "a_passe_rattrapage": resultats["a_passe_rattrapage"],
                "est_officiel": True,
                "date_validation": datetime.now(timezone.utc),
                "credits_obtenus": resultats.get("credits_obtenus", 0)
            }
            updated = update_resultat(self.db, existing.id, update_data)
            return {
                "action": "mis_a_jour",
                "resultat": ResultatSemestreRead.model_validate(updated)
            }
        else:
            resultat_data = ResultatSemestreCreate(
                etudiant_id=etudiant_id,
                semestre=semestre,
                annee_universitaire=annee_universitaire,
                moyenne_semestre=resultats["moyenne_semestre"] or 0.0,
                statut=resultats["statut"],
                a_passe_rattrapage=resultats["a_passe_rattrapage"],
                est_officiel=True,
                commentaire="Clôture officielle du semestre",
                credits_obtenus=resultats.get("credits_obtenus", 0)
            )
            new_resultat = create_resultat(self.db, resultat_data.model_dump())
            return {
                "action": "cree",
                "resultat": ResultatSemestreRead.model_validate(new_resultat)
            }

    def calculer_moyenne_matiere_etudiant(self, etudiant_id: int, matiere_id: int) -> Dict[str, Any]:
        """Calcule la moyenne d'un étudiant pour une matière donnée (vue simplifiée, sans rattrapage/reprise)."""
        matiere = get_matiere_by_id(self.db, matiere_id)
        if not matiere:
            raise MatiereNotFoundError(matiere_id)

        notes = get_by_etudiant_and_matiere(self.db, etudiant_id, matiere_id)

        if not notes:
            return {
                "etudiant_id": etudiant_id,
                "matiere_id": matiere_id,
                "matiere_nom": matiere.nom,
                "notes": {},
                "moyenne": None,
                "statut": "NON NOTÉ"
            }

        notes_par_type = {}
        for note in notes:
            type_note = note.type_note
            notes_par_type[type_note] = note.valeur

        valeurs = list(notes_par_type.values())
        moyenne = sum(valeurs) / len(valeurs)

        return {
            "etudiant_id": etudiant_id,
            "matiere_id": matiere_id,
            "matiere_nom": matiere.nom,
            "notes": notes_par_type,
            "moyenne": round(moyenne, 2),
            "statut": "VALIDÉ" if moyenne >= SEUIL_VALIDATION else "NON VALIDE"
        }

    def generer_pv_classe(
        self,
        semestre: str,
        annee_universitaire: str,
        filiere_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Génère le procès-verbal d'une classe pour un semestre donné."""
        tous_etudiants = get_all_users(self.db)
        etudiants = [u for u in tous_etudiants if "etudiant" in [r.name for r in u.roles]]

        if filiere_id is not None:
            filiere = get_filiere_by_id(self.db, filiere_id)
            if not filiere:
                raise FiliereNotFoundError(filiere_id)
            etudiants = [u for u in etudiants if u.filiere_id == filiere_id]

        resultats_etudiants = []
        for etudiant in etudiants:
            if not etudiant.filiere_id:
                continue

            resultats = self.calculer_moyenne_semestre(etudiant.id, semestre, annee_universitaire)

            if resultats["moyenne_semestre"] is not None:
                resultats_etudiants.append({
                    "etudiant_id": etudiant.id,
                    "nom": etudiant.nom,
                    "prenom": etudiant.prenom,
                    "matricule": etudiant.matricule,
                    "filiere_id": etudiant.filiere_id,
                    "matieres": resultats["matieres"],
                    "moyenne_generale": resultats["moyenne_semestre"],
                    "statut": resultats["statut"],
                    "credits_obtenus": resultats.get("credits_obtenus", 0),
                    "credits_total": resultats.get("credits_total", 0)
                })

        return {
            "semestre": semestre,
            "annee_universitaire": annee_universitaire,
            "filiere_id": filiere_id,
            "total_etudiants": len(resultats_etudiants),
            "etudiants": resultats_etudiants
        }

    def generer_pv_matiere(
        self,
        matiere_id: int,
        semestre: str,
        annee_universitaire: str,
        current_user
    ) -> Dict[str, Any]:
        """Génère le procès-verbal d'une matière pour un professeur."""
        user_roles = [role.name for role in current_user.roles]

        if "professeur" in user_roles and "admin" not in user_roles and "scolarite" not in user_roles:
            enseignement = get_by_professeur_and_matiere(self.db, current_user.id, matiere_id)
            if not enseignement:
                raise PermissionDeniedError("Vous n'enseignez pas cette matière")

        matiere = get_matiere_by_id(self.db, matiere_id)
        if not matiere:
            raise MatiereNotFoundError(matiere_id)

        filieres = get_filieres_by_matiere(self.db, matiere_id)
        filiere_ids = [f.filiere_id for f in filieres]

        if not filiere_ids:
            return {
                "matiere_id": matiere_id,
                "matiere_nom": matiere.nom,
                "semestre": semestre,
                "annee_universitaire": annee_universitaire,
                "total_etudiants": 0,
                "etudiants": []
            }

        etudiants = []
        for filiere_id in filiere_ids:
            etudiants_filiere = get_by_filiere(self.db, filiere_id)
            etudiants.extend(etudiants_filiere)

        etudiants = [u for u in etudiants if "etudiant" in [r.name for r in u.roles]]

        resultats_etudiants = []
        for etudiant in etudiants:
            resultat = self.calculer_moyenne_matiere(etudiant.id, matiere_id)

            if resultat["moyenne"] is not None:
                resultats_etudiants.append({
                    "etudiant_id": etudiant.id,
                    "nom": etudiant.nom,
                    "prenom": etudiant.prenom,
                    "matricule": etudiant.matricule,
                    "filiere_id": etudiant.filiere_id,
                    "notes": resultat["notes"],
                    "moyenne": resultat["moyenne"],
                    "statut": resultat["statut"]
                })

        return {
            "matiere_id": matiere_id,
            "matiere_nom": matiere.nom,
            "semestre": semestre,
            "annee_universitaire": annee_universitaire,
            "total_etudiants": len(resultats_etudiants),
            "etudiants": resultats_etudiants
        }

    def generer_bulletin_etudiant(self, etudiant_id: int, semestre: str, annee_universitaire: str, current_user) -> \
    Dict[str, Any]:
        """Génère le bulletin complet d'un étudiant pour un semestre donné."""
        user_roles = [role.name for role in current_user.roles]
        if current_user.id != etudiant_id and not any(r in user_roles for r in ["professeur", "admin", "scolarite"]):
            raise PermissionDeniedError("Vous n'avez pas l'autorisation de voir ce bulletin")

        etudiant = get_user_by_id(self.db, etudiant_id)
        if not etudiant:
            raise UserNotFoundError(etudiant_id)

        resultats = self.calculer_moyenne_semestre(etudiant_id, semestre, annee_universitaire)

        return {
            "etudiant_id": etudiant_id,
            "nom": etudiant.nom,
            "prenom": etudiant.prenom,
            "semestre": semestre,
            "annee_universitaire": annee_universitaire,
            "matieres": resultats["matieres"],
            "moyenne_semestre": resultats["moyenne_semestre"],
            "statut_semestre": resultats["statut"],
            "a_passe_rattrapage": resultats["a_passe_rattrapage"],
            "credits_obtenus": resultats.get("credits_obtenus", 0),
            "credits_total": resultats.get("credits_total", 0)
        }

    def get_calcul_semestre(self, etudiant_id: int, semestre: str, annee_universitaire: str, current_user) -> Dict[
        str, Any]:
        """Version avec vérification de permission de calculer_moyenne_semestre, pour exposition directe via route."""
        user_roles = [role.name for role in current_user.roles]
        if current_user.id != etudiant_id and not any(r in user_roles for r in ["professeur", "admin", "scolarite"]):
            raise PermissionDeniedError("Vous n'avez pas l'autorisation de voir ce calcul")

        return self.calculer_moyenne_semestre(etudiant_id, semestre, annee_universitaire)

    def get_moyenne_matiere_etudiant(self, etudiant_id: int, matiere_id: int, current_user) -> Dict[str, Any]:
        """Version avec vérification de permission de calculer_moyenne_matiere_etudiant."""
        user_roles = [role.name for role in current_user.roles]
        if current_user.id != etudiant_id and not any(r in user_roles for r in ["professeur", "admin", "scolarite"]):
            raise PermissionDeniedError("Vous n'avez pas l'autorisation de voir cette moyenne")

        return self.calculer_moyenne_matiere_etudiant(etudiant_id, matiere_id)

    def get_resultats_etudiant(self, etudiant_id: int, current_user) -> List[ResultatSemestreRead]:
        """Récupère tous les résultats officiels enregistrés d'un étudiant."""
        user_roles = [role.name for role in current_user.roles]
        if current_user.id != etudiant_id and not any(r in user_roles for r in ["admin", "scolarite"]):
            raise PermissionDeniedError("Vous n'avez pas l'autorisation de voir ces résultats")

        from crud.resultat_semestre import get_by_etudiant
        resultats = get_by_etudiant(self.db, etudiant_id)
        return [ResultatSemestreRead.model_validate(r) for r in resultats]