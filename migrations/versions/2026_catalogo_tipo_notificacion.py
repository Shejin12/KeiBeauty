"""catalogo tipo notificacion y migracion de notificaciones.tipo

Revision ID: 2026_catalogo_tipo_notificacion
Revises: 2026_catalogo_estado_pedido
Create Date: 2026-09-21
"""
from alembic import op
import sqlalchemy as sa

revision = '2026_catalogo_tipo_notificacion'
down_revision = '2026_catalogo_estado_pedido'
branch_labels = None
depends_on = None

VALORES = [
    ('pedido_estado', 'Cambio de estado de un pedido'),
    ('pedido_guia', 'Guia de envio agregada al pedido'),
    ('producto_stock', 'Producto con stock disponible'),
]


def upgrade():
    op.create_table(
        'catalogo_tipo_notificacion',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nombre', sa.String(length=50), nullable=False, unique=True),
        sa.Column('descripcion', sa.String(length=200), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=True, server_default='true'),
    )
    tabla = sa.table(
        'catalogo_tipo_notificacion',
        sa.column('nombre', sa.String),
        sa.column('descripcion', sa.String),
        sa.column('activo', sa.Boolean),
    )
    op.bulk_insert(tabla, [{'nombre': n, 'descripcion': d, 'activo': True} for n, d in VALORES])

    # Columna FK nullable para migrar datos existentes
    # (batch para compatibilidad SQLite/PostgreSQL)
    with op.batch_alter_table('notificaciones') as lote:
        lote.add_column(sa.Column('tipo_id', sa.Integer(), sa.ForeignKey('catalogo_tipo_notificacion.id', name='fk_notificaciones_tipo_id'), nullable=True))
    # Migrar: asignar el ID según el valor VARCHAR actual
    op.execute(sa.text(
        'UPDATE notificaciones SET tipo_id = '
        '(SELECT id FROM catalogo_tipo_notificacion WHERE catalogo_tipo_notificacion.nombre = notificaciones.tipo)'
    ))
    # Hacer FK NOT NULL y eliminar la columna VARCHAR original
    with op.batch_alter_table('notificaciones') as lote:
        lote.alter_column('tipo_id', nullable=False)
        lote.drop_column('tipo')
    op.create_index('ix_notificaciones_tipo_id', 'notificaciones', ['tipo_id'])


def downgrade():
    op.add_column('notificaciones', sa.Column('tipo', sa.String(length=50), nullable=True))
    op.execute(sa.text(
        'UPDATE notificaciones SET tipo = '
        '(SELECT nombre FROM catalogo_tipo_notificacion WHERE catalogo_tipo_notificacion.id = notificaciones.tipo_id)'
    ))
    op.drop_index('ix_notificaciones_tipo_id', table_name='notificaciones')
    with op.batch_alter_table('notificaciones') as lote:
        lote.alter_column('tipo', nullable=False)
        lote.drop_constraint('fk_notificaciones_tipo_id', type_='foreignkey')
        lote.drop_column('tipo_id')
    op.drop_table('catalogo_tipo_notificacion')
