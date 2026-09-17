"""agrega email_contacto y telefono_contacto a pedidos

Revision ID: 2026_email_telefono_pedido
Revises: 2026_url_guia_pedido
Create Date: 2026-09-16 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '2026_email_telefono_pedido'
down_revision = '2026_url_guia_pedido'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('pedidos', sa.Column('email_contacto', sa.String(length=150), nullable=True))
    op.add_column('pedidos', sa.Column('telefono_contacto', sa.String(length=20), nullable=True))


def downgrade():
    op.drop_column('pedidos', 'telefono_contacto')
    op.drop_column('pedidos', 'email_contacto')
