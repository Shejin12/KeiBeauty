"""catalogo rol usuario y migracion de usuarios.rol

Revision ID: 2026_catalogo_rol_usuario
Revises: 2026_inventario_costo_unitario
Create Date: 2026-09-21
"""
from alembic import op
import sqlalchemy as sa

revision = '2026_catalogo_rol_usuario'
down_revision = '2026_inventario_costo_unitario'
branch_labels = None
depends_on = None

VALORES = [
    ('admin', 'Administrador de la tienda'),
    ('cliente', 'Cliente de la tienda'),
]


def upgrade():
    op.create_table(
        'catalogo_rol_usuario',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nombre', sa.String(length=50), nullable=False, unique=True),
        sa.Column('descripcion', sa.String(length=200), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=True, server_default='true'),
    )
    tabla = sa.table(
        'catalogo_rol_usuario',
        sa.column('nombre', sa.String),
        sa.column('descripcion', sa.String),
        sa.column('activo', sa.Boolean),
    )
    op.bulk_insert(tabla, [{'nombre': n, 'descripcion': d, 'activo': True} for n, d in VALORES])

    # Columna FK nullable para migrar datos existentes
    # (batch para compatibilidad SQLite/PostgreSQL)
    with op.batch_alter_table('usuarios') as lote:
        lote.add_column(sa.Column('rol_id', sa.Integer(), sa.ForeignKey('catalogo_rol_usuario.id', name='fk_usuarios_rol_id'), nullable=True))
    # Migrar: asignar el ID según el valor VARCHAR actual
    op.execute(sa.text(
        'UPDATE usuarios SET rol_id = '
        '(SELECT id FROM catalogo_rol_usuario WHERE catalogo_rol_usuario.nombre = usuarios.rol)'
    ))
    # Hacer FK NOT NULL y eliminar la columna VARCHAR original
    with op.batch_alter_table('usuarios') as lote:
        lote.alter_column('rol_id', nullable=False)
        lote.drop_column('rol')
    op.create_index('ix_usuarios_rol_id', 'usuarios', ['rol_id'])


def downgrade():
    op.add_column('usuarios', sa.Column('rol', sa.String(length=20), nullable=True))
    op.execute(sa.text(
        'UPDATE usuarios SET rol = '
        '(SELECT nombre FROM catalogo_rol_usuario WHERE catalogo_rol_usuario.id = usuarios.rol_id)'
    ))
    op.drop_index('ix_usuarios_rol_id', table_name='usuarios')
    with op.batch_alter_table('usuarios') as lote:
        lote.alter_column('rol', nullable=False)
        lote.drop_constraint('fk_usuarios_rol_id', type_='foreignkey')
        lote.drop_column('rol_id')
    op.drop_table('catalogo_rol_usuario')
