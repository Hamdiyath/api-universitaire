
# models/inscription.py - Modèle Inscription

# Table de liaison entre les étudiants et les matières qu'ils suivent.
# Un étudiant peut être inscrit à plusieurs matières.
# Une matière peut avoir plusieurs étudiants inscrits.
# Un étudiant peut être inscrit à la même matière/semestre sur des
# années universitaires différentes (cas du redoublement).


from sqlalchemy import Column, Integer, ForeignKey, String, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
from models.enums import TypeInscription


class Inscription(Base):
    __tablename__ = "inscriptions"

    id = Column(Integer, primary_key=True, index=True)

    etudiant_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    matiere_id = Column(Integer, ForeignKey("matieres.id"), nullable=False)
    semestre = Column(String(20), nullable=False)
    annee_universitaire = Column(String(20), nullable=False)
    type_inscription = Column(
        SQLEnum(TypeInscription),
        nullable=False,
        default=TypeInscription.NORMALE
    )

    # Empêche un vrai doublon : même étudiant, même matière, même semestre, même année
    __table_args__ = (
        UniqueConstraint(
            "etudiant_id", "matiere_id", "semestre", "annee_universitaire",
            name="uq_inscription_etudiant_matiere_semestre_annee"
        ),
    )

    # Relations
    etudiant = relationship("User", backref="inscriptions")
    matiere = relationship("Matiere", backref="inscriptions")