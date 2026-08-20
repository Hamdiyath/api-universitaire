
# models/resultat_semestre.py - Modèle ResultatSemestre

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class ResultatSemestre(Base):
    __tablename__ = "resultats_semestre"

    id = Column(Integer, primary_key=True, index=True)

    etudiant_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    semestre = Column(String(20), nullable=False)
    annee_universitaire = Column(String(20), nullable=False)

    moyenne_semestre = Column(Float, nullable=False)

    statut = Column(String(20), nullable=False)  # VALIDÉ, AJOURNÉ, RATTRAPAGE

    a_passe_rattrapage = Column(Boolean, default=False, nullable=False)

    est_officiel = Column(Boolean, default=False, nullable=False)

    date_calcul = Column(DateTime, server_default=func.now(), nullable=False)
    date_validation = Column(DateTime, nullable=True)

    commentaire = Column(String(255), nullable=True)