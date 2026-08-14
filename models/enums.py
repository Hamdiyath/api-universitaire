
# models/enums.py - Énumérations pour les modèles


import enum


class SessionNote(str, enum.Enum):
    """Types de session pour une note"""
    NORMALE = "normale"
    RATTRAPAGE = "rattrapage"
    REPRISE = "reprise"