# models/resultat_matiere.py - Modèle ResultatMatiere
# Table de liaison many-to-many entre User (étudiant
#et Matiere,
# contextualisée par semestre et année universitaire.
# Sert à la fois à déclarer qu'un étudiant doit suivre une matière
# (généré à l'inscription/démarrage de semestre) et à stocker le
# résultat calculé (synchronisé à chaque saisie de note).

from sqlalchemy import Column, Integer, Float, String, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base
from models.enums import SessionNote, StatutValidation


class ResultatMatiere(Base):
    __tablename__ = "resultats_matieres"

    id = Column(Integer, primary_key=True, index=True)

    etudiant_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    matiere_id = Column(Integer, ForeignKey("matieres.id", ondelete="CASCADE"), nullable=False)
    semestre = Column(String(20), nullable=False)
    annee_universitaire = Column(String(20), nullable=False)

    moyenne = Column(Float, nullable=True)
    session_actuelle = Column(SQLEnum(SessionNote), nullable=False, default=SessionNote.NORMALE)
    statut = Column(SQLEnum(StatutValidation), nullable=False, default=StatutValidation.NON_NOTE)

    __table_args__ = (
        UniqueConstraint(
            "etudiant_id", "matiere_id", "semestre", "annee_universitaire",
            name="uq_resultat_matiere_etudiant_matiere_semestre_annee"
        ),
    )

    # Relations
    etudiant = relationship("User", backref="resultats_matieres")
    matiere = relationship("Matiere", backref="resultats_matieres")