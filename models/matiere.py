from sqlalchemy import Column, Integer, String
from database import Base

class Matiere(Base):
    __tablename__ = "matieres"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    nom = Column(String(100), nullable=False, index=True)
    credits = Column(Integer, nullable=False)  # ← Changé en Integer
    semestre = Column(String(20), nullable=False, index=True)
    niveau = Column(String(20), nullable=False, index=True)