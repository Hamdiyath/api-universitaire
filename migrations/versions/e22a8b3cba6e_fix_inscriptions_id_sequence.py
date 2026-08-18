"""fix inscriptions id sequence and primary key

Revision ID: <nouveau_id>
Revises: fc2900647f6e
Create Date: ...
"""
from alembic import op
import sqlalchemy as sa

revision = '<nouveau_id>'
down_revision = 'fc2900647f6e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Créer la séquence PostgreSQL pour l'auto-incrément
    op.execute("CREATE SEQUENCE IF NOT EXISTS inscriptions_id_seq")

    # 2. Lier la colonne id à cette séquence (valeur par défaut = nextval)
    op.execute("ALTER TABLE inscriptions ALTER COLUMN id SET DEFAULT nextval('inscriptions_id_seq')")

    # 3. Faire en sorte que la séquence appartienne à la colonne (pour qu'elle soit supprimée avec)
    op.execute("ALTER SEQUENCE inscriptions_id_seq OWNED BY inscriptions.id")

    # 4. Si l'ancienne clé primaire composite existe encore, la retirer d'abord
    #    (à vérifier: le nom exact de la contrainte peut varier, voir note ci-dessous)
    op.execute("ALTER TABLE inscriptions DROP CONSTRAINT IF EXISTS inscriptions_pkey")

    # 5. Définir id comme nouvelle clé primaire
    op.create_primary_key('inscriptions_pkey', 'inscriptions', ['id'])

    # 6. Si la table contient déjà des lignes, initialiser la séquence
    #    au max(id) existant pour éviter les collisions futures
    op.execute("SELECT setval('inscriptions_id_seq', COALESCE((SELECT MAX(id) FROM inscriptions), 1))")


def downgrade() -> None:
    op.drop_constraint('inscriptions_pkey', 'inscriptions', type_='primary')
    op.execute("ALTER TABLE inscriptions ALTER COLUMN id DROP DEFAULT")
    op.execute("DROP SEQUENCE IF EXISTS inscriptions_id_seq")