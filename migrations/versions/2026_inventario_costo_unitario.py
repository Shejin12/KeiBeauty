"""agregar costo_unitario a inventario_movimientos para reporte ganancias

Revision ID: 2026_inventario_costo_unitario
Revises: 2026_notificaciones_alerta
Create Date: 2026-09-17
"""
from alembic import op
import sqlalchemy as sa

revision = '2026_inventario_costo_unitario'
down_revision = '2026_notificaciones_alerta'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('inventario_movimientos', sa.Column('costo_unitario', sa.Numeric(precision=10, scale=2), nullable=True))

def downgrade():
    op.drop_column('inventario_movimientos', 'costo_unitario')
