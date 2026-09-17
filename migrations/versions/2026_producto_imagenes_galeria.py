"""galeria multiple imagenes por producto con principal

Revision ID: 2026_producto_imagenes_galeria
Revises: 2026_inventario_movimientos
Create Date: 2026-09-17
"""
from alembic import op
import sqlalchemy as sa

revision = '2026_producto_imagenes_galeria'
down_revision = '2026_inventario_movimientos'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'producto_imagenes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('producto_id', sa.Integer(), sa.ForeignKey('productos.id', ondelete='CASCADE'), nullable=False),
        sa.Column('imagen_url', sa.String(length=500), nullable=False),
        sa.Column('es_principal', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('orden', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_producto_imagenes_producto_id', 'producto_imagenes', ['producto_id'])
    # Migrar imagen_url existente a galeria como principal
    op.execute("""
        INSERT INTO producto_imagenes (producto_id, imagen_url, es_principal, orden, fecha_creacion)
        SELECT id, imagen_url, true, 0, NOW()
        FROM productos
        WHERE imagen_url IS NOT NULL AND imagen_url <> ''
    """)
    # Asegurar solo una principal por producto (índice parcial)
    op.execute("""
        CREATE UNIQUE INDEX uq_producto_imagen_principal
        ON producto_imagenes (producto_id)
        WHERE es_principal = true
    """)


def downgrade():
    op.drop_index('uq_producto_imagen_principal', table_name='producto_imagenes')
    op.drop_index('ix_producto_imagenes_producto_id', table_name='producto_imagenes')
    op.drop_table('producto_imagenes')
