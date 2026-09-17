"""hace usuario_id nullable en pedidos

Revision ID: 2026_usuario_id_nullable_pedido
Revises: 2026_email_telefono_pedido
Create Date: 2026-09-16 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '2026_usuario_id_nullable_pedido'
down_revision = '2026_email_telefono_pedido'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('pedidos', 'usuario_id', existing_type=sa.Integer(), nullable=True)


def downgrade():
    op.alter_column('pedidos', 'usuario_id', existing_type=sa.Integer(), nullable=False)
