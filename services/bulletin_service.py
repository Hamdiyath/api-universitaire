# ============================================================
# services/bulletin_service.py - Service de calcul des bulletins
# ============================================================

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from crud.note import get_by_etudiant_and_matiere
from crud.matiere import get_by_id as get_matiere_by_id
from crud.user import get_by_id as get_user_by_id
from crud.resultat_semestre import get_by_etudiant_semestre, create as create_resultat, update as update_resultat
from models.enums import SessionNote
from schemas.resultat_semestre import ResultatSemestreCreate, ResultatSemestreRead


# ============================================================
# FONCTIONS DE CALCUL
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


def calculer_moyenne_matiere(db: Session, etudiant_id: int, matiere_id: int) -> Dict[str, Any]:
    """
    Calcule la moyenne d'un étudiant pour une matière donnée.
    """
    notes = get_by_etudiant_and_matiere(db, etudiant_id, matiere_id)

    if not notes:
        return {
            "matiere_id": matiere_id,
            "moyenne": None,
            "notes": {},
            "statut": "NON_NOTÉ"
        }

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
        statut = "NON_NOTÉ"
    else:
        moyenne = sum(notes_valides) / len(notes_valides)
        statut = "ADMIS" if moyenne >= 10 else "AJOURNÉ"

    return {
        "matiere_id": matiere_id,
        "moyenne": round(moyenne, 2) if moyenne is not None else None,
        "notes": meilleures_notes,
        "statut": statut
    }


def calculer_moyenne_semestre(db: Session, etudiant_id: int, semestre: str, annee_universitaire: str) -> Dict[str, Any]:
    """
    Calcule la moyenne d'un semestre pour un étudiant.
    """
    from crud.matiere import get_all as get_all_matieres

    toutes_matieres = get_all_matieres(db)
    matieres_semestre = [m for m in toutes_matieres if m.semestre == semestre]

    if not matieres_semestre:
        return {
            "etudiant_id": etudiant_id,
            "semestre": semestre,
            "annee_universitaire": annee_universitaire,
            "matieres": [],
            "moyenne_semestre": None,
            "statut": "AUCUNE_MATIERE",
            "a_passe_rattrapage": False
        }

    resultats_matieres = []
    somme_moyennes_ponderees = 0
    somme_coefficients = 0
    a_passe_rattrapage = False

    for matiere in matieres_semestre:
        resultat = calculer_moyenne_matiere(db, etudiant_id, matiere.id)
        resultat["matiere_nom"] = matiere.nom
        resultat["coefficient"] = matiere.coefficient if hasattr(matiere, 'coefficient') else 1.0

        if resultat["moyenne"] is not None:
            coeff = resultat["coefficient"]
            somme_moyennes_ponderees += resultat["moyenne"] * coeff
            somme_coefficients += coeff

            if resultat.get("notes", {}).get("Rattrapage") is not None:
                a_passe_rattrapage = True

        resultats_matieres.append(resultat)

    if somme_coefficients > 0:
        moyenne_semestre = somme_moyennes_ponderees / somme_coefficients
    else:
        moyenne_semestre = None

    if moyenne_semestre is None:
        statut = "NON_NOTÉ"
    elif moyenne_semestre >= 10:
        statut = "VALIDÉ"
    else:
        statut = "AJOURNÉ"

    return {
        "etudiant_id": etudiant_id,
        "semestre": semestre,
        "annee_universitaire": annee_universitaire,
        "matieres": resultats_matieres,
        "moyenne_semestre": round(moyenne_semestre, 2) if moyenne_semestre is not None else None,
        "statut": statut,
        "a_passe_rattrapage": a_passe_rattrapage
    }


# ============================================================
# FONCTIONS DE GÉNÉRATION DE BULLETIN
# ============================================================

def generer_bulletin_etudiant(db: Session, etudiant_id: int, semestre: str, annee_universitaire: str) -> Dict[str, Any]:
    """
    Génère le bulletin complet d'un étudiant pour un semestre donne.
    """
    etudiant = get_user_by_id(db, etudiant_id)
    if not etudiant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Etudiant non trouve"
        )

    resultats = calculer_moyenne_semestre(db, etudiant_id, semestre, annee_universitaire)

    return {
        "etudiant_id": etudiant_id,
        "nom": etudiant.nom,
        "prenom": etudiant.prenom,
        "semestre": semestre,
        "annee_universitaire": annee_universitaire,
        "matieres": resultats["matieres"],
        "moyenne_semestre": resultats["moyenne_semestre"],
        "statut_semestre": resultats["statut"],
        "a_passe_rattrapage": resultats["a_passe_rattrapage"]
    }


def sauvegarder_resultat_semestre(db: Session, etudiant_id: int, semestre: str, annee_universitaire: str) -> Dict[str, Any]:
    """
    Sauvegarde le resultat d'un semestre dans la table resultats_semestre.
    Retourne un schéma Pydantic pour la sérialisation.
    """
    etudiant = get_user_by_id(db, etudiant_id)
    if not etudiant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Etudiant non trouve"
        )

    resultats = calculer_moyenne_semestre(db, etudiant_id, semestre, annee_universitaire)

    existing = get_by_etudiant_semestre(db, etudiant_id, semestre, annee_universitaire)

    if existing:
        update_data = {
            "moyenne_semestre": resultats["moyenne_semestre"],
            "statut": resultats["statut"],
            "a_passe_rattrapage": resultats["a_passe_rattrapage"],
            "est_officiel": True,
            "date_validation": datetime.now(timezone.utc)
        }
        updated = update_resultat(db, existing.id, update_data)
        # Retourner un schéma Pydantic
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
            commentaire="Cloture officielle du semestre"
        )
        new_resultat = create_resultat(db, resultat_data.model_dump())
        # Retourner un schéma Pydantic
        return {
            "action": "cree",
            "resultat": ResultatSemestreRead.model_validate(new_resultat)
        }


def calculer_moyenne_matiere_etudiant(db: Session, etudiant_id: int, matiere_id: int) -> Dict[str, Any]:
    """
    Calcule la moyenne d'un étudiant pour une matière donnée.
    """
    from crud.note import get_by_etudiant_and_matiere
    from crud.matiere import get_by_id as get_matiere_by_id

    # Vérifier que la matière existe
    matiere = get_matiere_by_id(db, matiere_id)
    if not matiere:
        raise HTTPException(status_code=404, detail="Matière non trouvée")

    # Récupérer les notes
    notes = get_by_etudiant_and_matiere(db, etudiant_id, matiere_id)

    if not notes:
        return {
            "etudiant_id": etudiant_id,
            "matiere_id": matiere_id,
            "matiere_nom": matiere.nom,
            "notes": {},
            "moyenne": None,
            "statut": "NON_NOTÉ"
        }

    # Séparer les notes par type
    notes_par_type = {}
    for note in notes:
        type_note = note.type_note
        notes_par_type[type_note] = note.valeur

    # Calculer la moyenne
    valeurs = list(notes_par_type.values())
    moyenne = sum(valeurs) / len(valeurs)

    return {
        "etudiant_id": etudiant_id,
        "matiere_id": matiere_id,
        "matiere_nom": matiere.nom,
        "notes": notes_par_type,
        "moyenne": round(moyenne, 2),
        "statut": "ADMIS" if moyenne >= 10 else "AJOURNÉ"
    }


def generer_pv_classe(
    db: Session,
    semestre: str,
    annee_universitaire: str,
    filiere_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Génère le procès-verbal d'une classe pour un semestre donné.
    - Si filiere_id est fourni, filtre par filière
    - Retourne la liste de tous les étudiants avec leurs moyennes
    """
    from crud.user import get_all as get_all_users
    from crud.filiere import get_by_id as get_filiere_by_id

    # 1. Récupérer tous les étudiants
    tous_etudiants = get_all_users(db)
    etudiants = [u for u in tous_etudiants if "etudiant" in [r.name for r in u.roles]]

    # 2. Filtrer par filière si demandé
    if filiere_id is not None:
        filiere = get_filiere_by_id(db, filiere_id)
        if not filiere:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Filière non trouvée"
            )
        etudiants = [u for u in etudiants if u.filiere_id == filiere_id]

    # 3. Calculer les résultats pour chaque étudiant
    resultats_etudiants = []
    for etudiant in etudiants:
        # Calculer la moyenne du semestre
        resultats = calculer_moyenne_semestre(db, etudiant.id, semestre, annee_universitaire)

        # Si l'étudiant n'a pas de notes, on l'ignore ou on le garde avec des valeurs vides
        if resultats["moyenne_semestre"] is not None:
            resultats_etudiants.append({
                "etudiant_id": etudiant.id,
                "nom": etudiant.nom,
                "prenom": etudiant.prenom,
                "matricule": etudiant.matricule,
                "filiere_id": etudiant.filiere_id,
                "matieres": resultats["matieres"],
                "moyenne_generale": resultats["moyenne_semestre"],
                "statut": resultats["statut"]
            })

    return {
        "semestre": semestre,
        "annee_universitaire": annee_universitaire,
        "filiere_id": filiere_id,
        "total_etudiants": len(resultats_etudiants),
        "etudiants": resultats_etudiants
    }