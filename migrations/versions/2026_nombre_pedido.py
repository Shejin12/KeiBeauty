"""agrega nombre_producto a detalle_pedidos

Revision ID: 2026_nombre_pedido
Revises: 2026_email_telefono_pedido
Create Date: 2026-09-16 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '2026_nombre_pedido'
down_revision = '2026_email_telefono_pedido'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('detalle_pedidos', sa.Column('nombre_producto', sa.String(length=200), nullable=True))


def downgrade():
    op.drop_column('detalle_pedidos', 'nombre_producto')
