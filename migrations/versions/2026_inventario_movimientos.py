"""crear tabla inventario_movimientos
Revision ID: 2026_inventario_movimientos
Revises: 2026_subtotal_detalle_pedidos
Create Date: 2026-09-16
"""
from alembic import op
import sqlalchemy as sa
revision = '2026_inventario_movimientos'
down_revision = '2026_subtotal_detalle_pedidos'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('inventario_movimientos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('producto_id', sa.Integer(), nullable=False),
        sa.Column('tipo', sa.String(length=20), nullable=False),
        sa.Column('cantidad', sa.Integer(), nullable=False),
        sa.Column('fecha', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['producto_id'], ['productos.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('producto_id', 'fecha')
    )

def downgrade():
    op.drop_table('inventario_movimientos')
