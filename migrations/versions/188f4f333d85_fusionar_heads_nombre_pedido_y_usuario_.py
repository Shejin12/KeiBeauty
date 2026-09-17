"""fusionar heads nombre_pedido y usuario_id_nullable_pedido

Revision ID: 188f4f333d85
Revises: 2026_nombre_pedido, 2026_usuario_id_nullable_pedido
Create Date: 2026-09-16

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '188f4f333d85'
down_revision = ('2026_nombre_pedido', '2026_usuario_id_nullable_pedido')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass