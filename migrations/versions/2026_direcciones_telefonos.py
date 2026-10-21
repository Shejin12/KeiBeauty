"""direcciones y telefonos multiples por usuario

Crea las tablas `usuario_direcciones` y `usuario_telefonos` para que una cuenta
pueda tener varias direcciones de envio y varios telefonos, y agrega el campo
`telefono_2` a `pedidos` como segundo telefono de referencia (opcional).

Las FKs hacia `usuarios` usan ON DELETE CASCADE en PostgreSQL y los modelos
declaran ademas cascade 'all, delete-orphan' a nivel ORM, que es lo que
garantiza el borrado en cascada en cualquier motor.

Cada tipo (direccion / telefono) admite una sola fila principal por usuario:
se garantiza en el ORM y, en PostgreSQL, con un indice unico parcial sobre
WHERE es_principal.

Revision ID: 2026_direcciones_telefonos
Revises: 2026_cascade_usuarios_fk
Create Date: 2026-10-21
"""
from alembic import op
import sqlalchemy as sa

revision = '2026_direcciones_telefonos'
down_revision = '2026_cascade_usuarios_fk'
branch_labels = None
depends_on = None


INDEX_DIRECCIONES = 'ux_usuario_direcciones_principal'
INDEX_TELEFONOS = 'ux_usuario_telefonos_principal'


def _es_postgres():
    return op.get_bind().dialect.name == 'postgresql'


def upgrade():
    op.create_table(
        'usuario_direcciones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('alias', sa.String(length=50), nullable=True),
        sa.Column('direccion', sa.Text(), nullable=False),
        sa.Column('es_principal', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('activa', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['usuario_id'],
            ['usuarios.id'],
            name='fk_usuario_direcciones_usuario_id',
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'ix_usuario_direcciones_usuario_id',
        'usuario_direcciones',
        ['usuario_id'],
        unique=False
    )

    op.create_table(
        'usuario_telefonos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('telefono', sa.String(length=20), nullable=False),
        sa.Column('es_principal', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['usuario_id'],
            ['usuarios.id'],
            name='fk_usuario_telefonos_usuario_id',
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'ix_usuario_telefonos_usuario_id',
        'usuario_telefonos',
        ['usuario_id'],
        unique=False
    )

    # Indice unico parcial: una sola direccion y un solo telefono principal por usuario.
    if _es_postgres():
        op.create_index(
            INDEX_DIRECCIONES,
            'usuario_direcciones',
            ['usuario_id'],
            unique=True,
            postgresql_where=sa.text('es_principal')
        )
        op.create_index(
            INDEX_TELEFONOS,
            'usuario_telefonos',
            ['usuario_id'],
            unique=True,
            postgresql_where=sa.text('es_principal')
        )

    # Segundo telefono de referencia del pedido (opcional).
    op.add_column(
        'pedidos',
        sa.Column('telefono_2', sa.String(length=20), nullable=True)
    )


def downgrade():
    op.drop_column('pedidos', 'telefono_2')

    if _es_postgres():
        op.drop_index(INDEX_DIRECCIONES, table_name='usuario_direcciones')
        op.drop_index(INDEX_TELEFONOS, table_name='usuario_telefonos')

    op.drop_index('ix_usuario_telefonos_usuario_id', table_name='usuario_telefonos')
    op.drop_table('usuario_telefonos')

    op.drop_index('ix_usuario_direcciones_usuario_id', table_name='usuario_direcciones')
    op.drop_table('usuario_direcciones')
