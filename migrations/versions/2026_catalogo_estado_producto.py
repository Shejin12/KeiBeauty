"""catalogo estado producto y migracion de productos.estado

Revision ID: 2026_catalogo_estado_producto
Revises: 2026_catalogo_rol_usuario
Create Date: 2026-09-21
"""
from alembic import op
import sqlalchemy as sa

revision = '2026_catalogo_estado_producto'
down_revision = '2026_catalogo_rol_usuario'
branch_labels = None
depends_on = None

VALORES = [
    ('activo', 'Producto visible y disponible'),
    ('inactivo', 'Producto oculto del catalogo'),
    ('agotado', 'Producto sin stock'),
]


def upgrade():
    op.create_table(
        'catalogo_estado_producto',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nombre', sa.String(length=50), nullable=False, unique=True),
        sa.Column('descripcion', sa.String(length=200), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=True, server_default='true'),
    )
    tabla = sa.table(
        'catalogo_estado_producto',
        sa.column('nombre', sa.String),
        sa.column('descripcion', sa.String),
        sa.column('activo', sa.Boolean),
    )
    op.bulk_insert(tabla, [{'nombre': n, 'descripcion': d, 'activo': True} for n, d in VALORES])

    # Columna FK nullable para migrar datos existentes
    # (batch para compatibilidad SQLite/PostgreSQL)
    with op.batch_alter_table('productos') as lote:
        lote.add_column(sa.Column('estado_id', sa.Integer(), sa.ForeignKey('catalogo_estado_producto.id', name='fk_productos_estado_id'), nullable=True))
    # Migrar: asignar el ID según el valor VARCHAR actual
    op.execute(sa.text(
        'UPDATE productos SET estado_id = '
        '(SELECT id FROM catalogo_estado_producto WHERE catalogo_estado_producto.nombre = productos.estado)'
    ))
    # Hacer FK NOT NULL y eliminar la columna VARCHAR original
    with op.batch_alter_table('productos') as lote:
        lote.alter_column('estado_id', nullable=False)
        lote.drop_column('estado')
    op.create_index('ix_productos_estado_id', 'productos', ['estado_id'])


def downgrade():
    op.add_column('productos', sa.Column('estado', sa.String(length=20), nullable=True))
    op.execute(sa.text(
        'UPDATE productos SET estado = '
        '(SELECT nombre FROM catalogo_estado_producto WHERE catalogo_estado_producto.id = productos.estado_id)'
    ))
    op.drop_index('ix_productos_estado_id', table_name='productos')
    with op.batch_alter_table('productos') as lote:
        lote.alter_column('estado', nullable=False)
        lote.drop_constraint('fk_productos_estado_id', type_='foreignkey')
        lote.drop_column('estado_id')
    op.drop_table('catalogo_estado_producto')
