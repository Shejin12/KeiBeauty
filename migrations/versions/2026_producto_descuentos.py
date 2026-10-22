"""descuentos por producto

Crea la tabla `producto_descuentos` (porcentaje con rango de fechas) y agrega
a `detalle_pedidos` las columnas `precio_real` y `descuento_porcentaje`, que
guardan el precio efectivamente cobrado y el descuento aplicado.

Los detalles existentes se rellenan con `precio_real = precio_unitario` y
`descuento_porcentaje = 0`, de modo que `subtotal` sigue siendo igual.

Revision ID: 2026_producto_descuentos
Revises: 2026_configuracion_tienda
Create Date: 2026-10-21
"""
from alembic import op
import sqlalchemy as sa

revision = '2026_producto_descuentos'
down_revision = '2026_configuracion_tienda'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'producto_descuentos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('producto_id', sa.Integer(), nullable=False),
        sa.Column('porcentaje', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('fecha_inicio', sa.DateTime(), nullable=False),
        sa.Column('fecha_fin', sa.DateTime(), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['producto_id'],
            ['productos.id'],
            name='fk_producto_descuentos_producto_id',
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'ix_producto_descuentos_producto_id',
        'producto_descuentos',
        ['producto_id'],
        unique=False
    )

    # Columnas del detalle del pedido: nullable -> backfill -> NOT NULL.
    with op.batch_alter_table('detalle_pedidos') as lote:
        lote.add_column(sa.Column('precio_real', sa.Numeric(precision=10, scale=2), nullable=True))
        lote.add_column(sa.Column('descuento_porcentaje', sa.Numeric(precision=5, scale=2), nullable=True))

    # Los detalles historicos no tienen descuento: el precio real es el de lista.
    op.execute(sa.text('UPDATE detalle_pedidos SET precio_real = precio_unitario, descuento_porcentaje = 0'))

    with op.batch_alter_table('detalle_pedidos') as lote:
        lote.alter_column('precio_real', nullable=False, server_default='0')
        lote.alter_column('descuento_porcentaje', nullable=False, server_default='0')


def downgrade():
    with op.batch_alter_table('detalle_pedidos') as lote:
        lote.alter_column('descuento_porcentaje', server_default=None)
        lote.alter_column('precio_real', server_default=None)
        lote.drop_column('descuento_porcentaje')
        lote.drop_column('precio_real')

    op.drop_index('ix_producto_descuentos_producto_id', table_name='producto_descuentos')
    op.drop_table('producto_descuentos')
