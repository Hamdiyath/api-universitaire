
# models/enums.py - Énumérations pour les modèles


import enum


class SessionNote(str, enum.Enum):
    """Types de session pour une note"""
    NORMALE = "normale"
    RATTRAPAGE = "rattrapage"
    REPRISE = "reprise"



class TypeInscription(str, enum.Enum):
    """Types d'inscription d'un étudiant à une matière."""
    NORMALE = "normale"
    REDOUBLEMENT = "redoublement"
    ENJAMBEMENT = "enjambement"
    OPTIONNEL = "optionnel"

class StatutValidation(str, enum.Enum):
    """Statut de validation d'un étudiant pour une matière donnée."""
    NON_NOTE = "non_note"
    VALIDE = "valide"
    NON_VALIDE = "non_valide"