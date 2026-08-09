from sqlalchemy import Column, Integer, String
from database import Base
from sqlalchemy.orm import relationship
class Filiere(Base):
    __tablename__ = "filieres"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    etudiants = relationship("User", back_populates="filiere")