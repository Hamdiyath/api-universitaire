# ============================================================
# models/inscription.py - Modèle Inscription
# ============================================================
# Table de liaison entre les étudiants et les matières qu'ils suivent.
# Un étudiant peut être inscrit à plusieurs matières.
# Une matière peut avoir plusieurs étudiants inscrits.
# ============================================================

from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from database import Base


class Inscription(Base):
    __tablename__ = "inscriptions"

    # Clé primaire composite (etudiant_id, matiere_id, semestre)
    etudiant_id = Column(Integer, ForeignKey("users.id"), primary_key=True, nullable=False)
    matiere_id = Column(Integer, ForeignKey("matieres.id"), primary_key=True, nullable=False)
    semestre = Column(String(20), primary_key=True, nullable=False)
    annee_universitaire = Column(String(20), nullable=False)

    # Relations
    etudiant = relationship("User", backref="inscriptions")
    matiere = relationship("Matiere", backref="inscriptions")