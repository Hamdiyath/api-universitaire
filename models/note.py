from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from database import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)

    # Clés étrangères (tout le monde est dans users)
    etudiant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    matiere_id = Column(Integer, ForeignKey("matieres.id"), nullable=False)
    professeur_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # La note
    valeur = Column(Float, nullable=False)  # ← Changé en Float

    # Contexte
    type_note = Column(String(20), nullable=False)  # CC, TD, TP, Examen, Rattrapage
    semestre = Column(String(20), nullable=False)  # S1, S2, etc.
    annee_universitaire = Column(String(20), nullable=False)


    # Dates
    date_saisie = Column(DateTime, server_default=func.now(), nullable=False)


    # Commentaires
    commentaire = Column(String(255), nullable=True)