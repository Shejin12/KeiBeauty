"""agrega campo tamano a productos

Revision ID: 2026_tamano_producto
Revises: 2fa_migracion_2026
Create Date: 2026-09-16 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '2026_tamano_producto'
down_revision = '2fa_migracion_2026'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('productos', sa.Column('tamano', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('productos', 'tamano')
