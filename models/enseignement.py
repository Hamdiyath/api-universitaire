# ============================================================
# models/enseignement.py - Modèle Enseignement
# ============================================================
# Table de liaison entre les professeurs et les matières qu'ils enseignent.
# Un professeur peut enseigner plusieurs matières.
# Une matière peut être enseignée par plusieurs professeurs.
# ============================================================

from sqlalchemy import Column, Integer, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class Enseignement(Base):
    __tablename__ = "enseignements"

    # Clé primaire simple (AUTO_INCREMENT)
    id = Column(Integer, primary_key=True, index=True)

    # Clés étrangères (sans primary_key=True)
    professeur_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    matiere_id = Column(Integer, ForeignKey("matieres.id"), nullable=False)
    semestre = Column(String(20), nullable=False)
    annee_universitaire = Column(String(20), nullable=False)

    # Contrainte d'unicité pour éviter les doublons
    __table_args__ = (
        UniqueConstraint('professeur_id', 'matiere_id', 'semestre', name='uq_enseignement'),
    )

    # Relations
    professeur = relationship("User", backref="enseignements")
    matiere = relationship("Matiere", backref="enseignements")



