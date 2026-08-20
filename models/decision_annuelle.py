
# models/decision_annuelle.py - Modèle DecisionAnnuelle
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import enum


class DecisionPassage(str, enum.Enum):
    """Décision de passage en fin d'année universitaire."""
    PASSE = "passe"
    ENJAMBEMENT = "enjambement"
    REDOUBLEMENT = "redoublement"


class DecisionAnnuelle(Base):
    __tablename__ = "decisions_annuelles"

    id = Column(Integer, primary_key=True, index=True)

    etudiant_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    annee_universitaire = Column(String(20), nullable=False)

    credits_valides = Column(Integer, nullable=False)
    credits_total = Column(Integer, nullable=False, default=60)
    decision = Column(SQLEnum(DecisionPassage), nullable=False)

    date_decision = Column(DateTime, server_default=func.now(), nullable=False)
    commentaire = Column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "etudiant_id", "annee_universitaire",
            name="uq_decision_annuelle_etudiant_annee"
        ),
    )

    etudiant = relationship("User", backref="decisions_annuelles")