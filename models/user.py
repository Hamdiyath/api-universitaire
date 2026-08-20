# models/user.py - Modèle User
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"
    # ---------- Identifiant ----------
    id = Column(Integer, primary_key=True, index=True)

    # ---------- Informations de connexion ----------
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # NULL avant activation

    # ---------- Identité ----------
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    date_naissance = Column(Date, nullable=True)
    telephone = Column(String(20), nullable=True)
    adresse = Column(String(255), nullable=True)
    photo = Column(String(255), nullable=True)

    # ---------- Champs spécifiques selon le rôle ----------
    matricule = Column(String(50), unique=True, nullable=True)  # Étudiant
    specialite = Column(String(255), nullable=True)
    # Professeur
    # ---------- Statut du compte ----------
    statut = Column(String(20), default="actif", nullable=False)

    # ---------- Activation du compte ----------
    is_active = Column(Boolean, default=False, nullable=False)
    activation_token = Column(String(255), nullable=True, unique=True)
    activation_token_expires = Column(DateTime, nullable=True)

    # ---------- Horodatage ----------
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # ---------- Relations ----------
    roles = relationship("Role", secondary="user_role", back_populates="users")
    # Filière de l'utilisateur (uniquement pour les étudiants)
    filiere_id = Column(Integer, ForeignKey("filieres.id"), nullable=True)
    filiere = relationship("Filiere", back_populates="etudiants")
    # Niveau académique actuel de l'étudiant (L1, L2, L3...).
    # NULL pour les admins, professeurs et scolarité.
    # Mis à jour uniquement lors d'une décision de passage (PASSE/ENJAMBEMENT).
    niveau_actuel = Column(String(10), nullable=True)