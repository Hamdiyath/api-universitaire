"""restructure inscriptions table

Revision ID: fc2900647f6e
Revises: 6099b023c877
Create Date: 2026-08-17 13:11:26.709090

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fc2900647f6e'
down_revision: Union[str, Sequence[str], None] = '6099b023c877'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 🔥 ÉTAPE 1 : Créer le type ENUM AVANT d'ajouter la colonne
    op.execute("CREATE TYPE typeinscription AS ENUM ('NORMALE', 'REDOUBLEMENT', 'ENJAMBEMENT', 'OPTIONNEL')")

    # ÉTAPE 2 : Ajouter les colonnes
    op.add_column('inscriptions', sa.Column('id', sa.Integer(), nullable=False))
    op.add_column('inscriptions', sa.Column('type_inscription', sa.Enum('NORMALE', 'REDOUBLEMENT', 'ENJAMBEMENT', 'OPTIONNEL', name='typeinscription'), nullable=False))

    # ÉTAPE 3 : Index et contraintes
    op.create_index(op.f('ix_inscriptions_id'), 'inscriptions', ['id'], unique=False)
    op.create_unique_constraint('uq_inscription_etudiant_matiere_semestre_annee', 'inscriptions', ['etudiant_id', 'matiere_id', 'semestre', 'annee_universitaire'])


def downgrade() -> None:
    """Downgrade schema."""

    # ÉTAPE 1 : Supprimer les contraintes/index
    op.drop_constraint('uq_inscription_etudiant_matiere_semestre_annee', 'inscriptions', type_='unique')
    op.drop_index(op.f('ix_inscriptions_id'), table_name='inscriptions')

    # ÉTAPE 2 : Supprimer les colonnes (l'ordre n'a pas d'importance ici)
    op.drop_column('inscriptions', 'type_inscription')
    op.drop_column('inscriptions', 'id')

    # 🔥 ÉTAPE 3 : Supprimer le type ENUM APRÈS avoir supprimé les colonnes qui l'utilisent
    op.execute("DROP TYPE typeinscription")