# ============================================================
# models/enseignement.py - Modèle Enseignement
# ============================================================
# Table de liaison entre les professeurs et les matières qu'ils enseignent.
# Un professeur peut enseigner plusieurs matières.
# Une matière peut être enseignée par plusieurs professeurs.
# ============================================================

from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from database import Base


class Enseignement(Base):
    __tablename__ = "enseignements"

    # Clé primaire composite (professeur_id, matiere_id, semestre)
    professeur_id = Column(Integer, ForeignKey("users.id"), primary_key=True, nullable=False)
    matiere_id = Column(Integer, ForeignKey("matieres.id"), primary_key=True, nullable=False)
    semestre = Column(String(20), primary_key=True, nullable=False)
    annee_universitaire = Column(String(20), nullable=False)

    # Relations
    professeur = relationship("User", backref="enseignements")
    matiere = relationship("Matiere", backref="enseignements")