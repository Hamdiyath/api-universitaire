from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class MatiereFiliere(Base):
    __tablename__ = "matiere_filiere"

    # Clé primaire composite
    matiere_id = Column(Integer, ForeignKey("matieres.id"), primary_key=True, nullable=False)
    filiere_id = Column(Integer, ForeignKey("filieres.id"), primary_key=True, nullable=False)
    semestre = Column(String(20), primary_key=True, nullable=False)  # S1, S2, etc.