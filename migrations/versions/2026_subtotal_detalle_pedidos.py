"""agregar subtotal a detalle_pedidos
Revision ID: 2026_subtotal_detalle_pedidos
Revises: 2026_guest_token_carritos
Create Date: 2026-09-16
"""
from alembic import op
import sqlalchemy as sa
revision = '2026_subtotal_detalle_pedidos'
down_revision = '2026_guest_token_carritos'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('detalle_pedidos', sa.Column('subtotal', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0'))
    op.alter_column('detalle_pedidos', 'subtotal', nullable=False, server_default=None)

def downgrade():
    op.drop_column('detalle_pedidos', 'subtotal')
