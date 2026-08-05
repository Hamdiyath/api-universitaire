from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    # Identifiant
    id = Column(Integer, primary_key=True, index=True)

    # Informations de connexion
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # Identité
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    date_naissance = Column(Date, nullable=True)
    telephone = Column(String(20), nullable=True)

    # Champs spécifiques (selon le rôle)
    matricule = Column(String(50), unique=True, nullable=True)  # Étudiant
    specialite = Column(String(255), nullable=True)  # Professeur


    # Statut du compte
    statut = Column(String(20), default="actif", nullable=False)

    # Horodatage
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)