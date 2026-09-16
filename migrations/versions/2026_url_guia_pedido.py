"""agrega url_guia a pedidos

Revision ID: 2026_url_guia_pedido
Revises: 2026_tamano_producto
Create Date: 2026-09-16 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '2026_url_guia_pedido'
down_revision = '2026_tamano_producto'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('pedidos', sa.Column('url_guia', sa.String(length=500), nullable=True))


def downgrade():
    op.drop_column('pedidos', 'url_guia')
