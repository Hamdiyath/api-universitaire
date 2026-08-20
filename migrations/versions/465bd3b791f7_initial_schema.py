"""initial_schema

Revision ID: 465bd3b791f7
Revises: 
Create Date: 2026-08-19 16:47:52.952239

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '465bd3b791f7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # 1. Création de l'ENUM statutvalidation s'il n'existe pas encore
    statut_validation_enum = postgresql.ENUM('NON_NOTE', 'VALIDE', 'NON_VALIDE', name='statutvalidation', create_type=False)
    statut_validation_enum.create(bind, checkfirst=True)

    # 2. Récupération de l'ENUM sessionnote existant
    session_note_enum = postgresql.ENUM('NORMALE', 'RATTRAPAGE', 'REPRISE', name='sessionnote', create_type=False)

    # 3. Création de la table resultats_matieres
    op.create_table(
        'resultats_matieres',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('etudiant_id', sa.Integer(), nullable=False),
        sa.Column('matiere_id', sa.Integer(), nullable=False),
        sa.Column('semestre', sa.String(length=20), nullable=False),
        sa.Column('annee_universitaire', sa.String(length=20), nullable=False),
        sa.Column('moyenne', sa.Float(), nullable=True),
        sa.Column('session_actuelle', session_note_enum, nullable=False),
        sa.Column('statut', statut_validation_enum, nullable=False),
        sa.ForeignKeyConstraint(['etudiant_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['matiere_id'], ['matieres.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('etudiant_id', 'matiere_id', 'semestre', 'annee_universitaire', name='uq_resultat_matiere_etudiant_matiere_semestre_annee')
    )
    op.create_index(op.f('ix_resultats_matieres_id'), 'resultats_matieres', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_resultats_matieres_id'), table_name='resultats_matieres')
    op.drop_table('resultats_matieres')
    op.execute("DROP TYPE IF EXISTS statutvalidation")