# ============================================================
# services/bulletin_service.py - Service de calcul des bulletins
# ============================================================

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from crud.note import get_by_etudiant_and_matiere
from crud.matiere import get_by_id as get_matiere_by_id
from crud.user import get_by_id as get_user_by_id, get_by_filiere
from crud.resultat_semestre import get_by_etudiant_semestre, create as create_resultat, update as update_resultat
from crud.matiere_filiere import get_by_filiere as get_matieres_by_filiere, get_by_matiere as get_filieres_by_matiere
from crud.enseignement import get_by_professeur_and_matiere
from models.enums import SessionNote
from schemas.resultat_semestre import ResultatSemestreCreate, ResultatSemestreRead

# ---------- Constante pour le seuil de validation ----------
SEUIL_VALIDATION = 12


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
    Règles de Lokossa :
    - Seuil de validation = 12
    - Pas de compensation : chaque matière est validée individuellement
    - Rattrapage écrase la matière (si présent)
    - Reprise écrase aussi (si présent)
    """
    notes = get_by_etudiant_and_matiere(db, etudiant_id, matiere_id)

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
    # Séparer les notes par type (CC, Examen, etc.)
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

    # Prendre la meilleure note pour chaque type
    meilleures_notes = {}
    for type_note, notes_list in notes_par_type.items():
        meilleures_notes[type_note] = get_meilleure_note(notes_list)

    # Calculer la moyenne
    notes_valides = [v for v in meilleures_notes.values() if v is not None]
    if not notes_valides:
        moyenne = None
        statut = "NON NOTÉ"
    else:
        moyenne = sum(notes_valides) / len(notes_valides)
        # Seuil de validation = 12 (règle de Lokossa)
        statut = "VALIDÉ" if moyenne >= SEUIL_VALIDATION else "NON VALIDE"

    return {
        "matiere_id": matiere_id,
        "moyenne": round(moyenne, 2) if moyenne is not None else None,
        "notes": meilleures_notes,
        "statut": statut
    }


def calculer_moyenne_semestre(db: Session, etudiant_id: int, semestre: str, annee_universitaire: str) -> Dict[str, Any]:
    """
    Calcule la moyenne d'un semestre pour un étudiant.
    Règles de Lokossa :
    - Pas de compensation : le semestre n'est validé que si TOUTES les matières sont validées
    - Chaque matière est validée si sa moyenne ≥ 12
    """
    # 1. Récupérer l'étudiant
    etudiant = get_user_by_id(db, etudiant_id)
    if not etudiant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Étudiant non trouvé"
        )

    # 2. Vérifier que l'étudiant a une filière
    if not etudiant.filiere_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'étudiant n'est pas assigné à une filière"
        )

    # 3. Récupérer les matières de la filière de l'étudiant pour ce semestre
    associations = get_matieres_by_filiere(db, etudiant.filiere_id)
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

    # 4. Récupérer les détails des matières
    from crud.matiere import get_by_id as get_matiere_by_id
    matieres = []
    for matiere_id in matiere_ids:
        matiere = get_matiere_by_id(db, matiere_id)
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

    # 5. Calculer les résultats par matière
    resultats_matieres = []
    toutes_validees = True
    a_passe_rattrapage = False
    somme_moyennes_ponderees = 0
    somme_coefficients = 0
    credits_obtenus = 0
    credits_total = 0

    for matiere in matieres:
        resultat = calculer_moyenne_matiere(db, etudiant_id, matiere.id)
        resultat["matiere_nom"] = matiere.nom
        resultat["coefficient"] = matiere.coefficient if hasattr(matiere, 'coefficient') else 1.0
        resultat["credits"] = matiere.credits if hasattr(matiere, 'credits') else 0

        credits_total += resultat["credits"]

        if resultat["moyenne"] is not None:
            # Vérifier si la matière est validée
            if resultat["statut"] == "VALIDÉ":
                credits_obtenus += resultat["credits"]
            else:
                toutes_validees = False

            # Détecter si l'étudiant a utilisé le rattrapage
            if resultat.get("notes", {}).get("Rattrapage") is not None:
                a_passe_rattrapage = True

            coeff = resultat["coefficient"]
            somme_moyennes_ponderees += resultat["moyenne"] * coeff
            somme_coefficients += coeff

        resultats_matieres.append(resultat)

    # 6. Calculer la moyenne du semestre (pour information)
    if somme_coefficients > 0:
        moyenne_semestre = somme_moyennes_ponderees / somme_coefficients
    else:
        moyenne_semestre = None

    # 7. Déterminer le statut du semestre (règle de Lokossa)
    # Pas de compensation : le semestre n'est validé que si TOUTES les matières sont validées
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

def generer_bulletin_etudiant(db: Session, etudiant_id: int, semestre: str, annee_universitaire: str) -> Dict[str, Any]:
    """
    Génère le bulletin complet d'un étudiant pour un semestre donné.
    """
    etudiant = get_user_by_id(db, etudiant_id)
    if not etudiant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Étudiant non trouvé"
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
        "a_passe_rattrapage": resultats["a_passe_rattrapage"],
        "credits_obtenus": resultats.get("credits_obtenus", 0),
        "credits_total": resultats.get("credits_total", 0)
    }


def sauvegarder_resultat_semestre(db: Session, etudiant_id: int, semestre: str, annee_universitaire: str) -> Dict[str, Any]:
    """
    Sauvegarde le résultat d'un semestre dans la table resultats_semestre.
    """
    etudiant = get_user_by_id(db, etudiant_id)
    if not etudiant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Étudiant non trouvé"
        )

    resultats = calculer_moyenne_semestre(db, etudiant_id, semestre, annee_universitaire)

    existing = get_by_etudiant_semestre(db, etudiant_id, semestre, annee_universitaire)

    if existing:
        update_data = {
            "moyenne_semestre": resultats["moyenne_semestre"],
            "statut": resultats["statut"],
            "a_passe_rattrapage": resultats["a_passe_rattrapage"],
            "est_officiel": True,
            "date_validation": datetime.now(timezone.utc),
            "credits_obtenus": resultats.get("credits_obtenus", 0)
        }
        updated = update_resultat(db, existing.id, update_data)
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
        new_resultat = create_resultat(db, resultat_data.model_dump())
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

    matiere = get_matiere_by_id(db, matiere_id)
    if not matiere:
        raise HTTPException(status_code=404, detail="Matière non trouvée")

    notes = get_by_etudiant_and_matiere(db, etudiant_id, matiere_id)

    if not notes:
        return {
            "etudiant_id": etudiant_id,
            "matiere_id": matiere_id,
            "matiere_nom": matiere.nom,
            "notes": {},
            "moyenne": None,
            "statut": "NON NOTÉ"
        }

    # Séparer les notes par type
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
    db: Session,
    semestre: str,
    annee_universitaire: str,
    filiere_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Génère le procès-verbal d'une classe pour un semestre donné.
    """
    from crud.user import get_all as get_all_users
    from crud.filiere import get_by_id as get_filiere_by_id

    tous_etudiants = get_all_users(db)
    etudiants = [u for u in tous_etudiants if "etudiant" in [r.name for r in u.roles]]

    if filiere_id is not None:
        filiere = get_filiere_by_id(db, filiere_id)
        if not filiere:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Filière non trouvée"
            )
        etudiants = [u for u in etudiants if u.filiere_id == filiere_id]

    resultats_etudiants = []
    for etudiant in etudiants:
        if not etudiant.filiere_id:
            continue

        resultats = calculer_moyenne_semestre(db, etudiant.id, semestre, annee_universitaire)

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
    db: Session,
    matiere_id: int,
    semestre: str,
    annee_universitaire: str,
    current_user
) -> Dict[str, Any]:
    """
    Génère le procès-verbal d'une matière pour un professeur.
    """
    user_roles = [role.name for role in current_user.roles]

    # Vérification pour les professeurs (admin et scolarité passent)
    if "professeur" in user_roles and "admin" not in user_roles and "scolarite" not in user_roles:
        enseignement = get_by_professeur_and_matiere(db, current_user.id, matiere_id)
        if not enseignement:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous n'enseignez pas cette matière"
            )

    matiere = get_matiere_by_id(db, matiere_id)
    if not matiere:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matière non trouvée"
        )

    filieres = get_filieres_by_matiere(db, matiere_id)
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
        etudiants_filiere = get_by_filiere(db, filiere_id)
        etudiants.extend(etudiants_filiere)

    etudiants = [u for u in etudiants if "etudiant" in [r.name for r in u.roles]]

    resultats_etudiants = []
    for etudiant in etudiants:
        resultat = calculer_moyenne_matiere(db, etudiant.id, matiere_id)

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