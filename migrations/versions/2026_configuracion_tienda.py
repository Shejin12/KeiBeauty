"""configuracion de la tienda y costo de envio

Crea la tabla `configuracion_tienda` (clave/valor) para los ajustes
editables desde el panel de administracion, y agrega a `pedidos` las columnas
`subtotal_productos` y `costo_envio`.

El total del pedido pasa a ser `subtotal_productos + costo_envio`. Los
pedidos existentes se rellenan con `subtotal_productos = monto_total` y
`costo_envio = 0`, de forma que `monto_total` sigue cuadrando exactamente
igual que antes de la migracion.

Revision ID: 2026_configuracion_tienda
Revises: 2026_direcciones_telefonos
Create Date: 2026-10-21
"""
from alembic import op
import sqlalchemy as sa

revision = '2026_configuracion_tienda'
down_revision = '2026_direcciones_telefonos'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'configuracion_tienda',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('clave', sa.String(length=50), nullable=False),
        sa.Column('valor', sa.String(length=255), nullable=False),
        sa.Column('descripcion', sa.String(length=200), nullable=True),
        sa.Column('fecha_actualizacion', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('clave')
    )

    # Valores iniciales de la politica de envio.
    tabla = sa.table(
        'configuracion_tienda',
        sa.column('clave', sa.String),
        sa.column('valor', sa.String),
        sa.column('descripcion', sa.String),
    )
    op.bulk_insert(tabla, [
        {
            'clave': 'costo_envio',
            'valor': '30.00',
            'descripcion': 'Costo fijo de envio en quetzales'
        },
        {
            'clave': 'minimo_envio_gratis',
            'valor': '200.00',
            'descripcion': 'Subtotal minimo (en quetzales) para obtener envio gratis'
        },
    ])

    # Columnas del desglose del pedido: nullable -> backfill -> NOT NULL.
    with op.batch_alter_table('pedidos') as lote:
        lote.add_column(sa.Column('subtotal_productos', sa.Numeric(precision=10, scale=2), nullable=True))
        lote.add_column(sa.Column('costo_envio', sa.Numeric(precision=10, scale=2), nullable=True))

    # Los pedidos historicos no tienen envio desglosado: el total actual
    # pasa a ser el subtotal de productos y el envio queda en cero.
    op.execute(sa.text('UPDATE pedidos SET subtotal_productos = monto_total, costo_envio = 0'))

    with op.batch_alter_table('pedidos') as lote:
        lote.alter_column('subtotal_productos', nullable=False, server_default='0')
        lote.alter_column('costo_envio', nullable=False, server_default='0')


def downgrade():
    with op.batch_alter_table('pedidos') as lote:
        lote.alter_column('costo_envio', server_default=None)
        lote.alter_column('subtotal_productos', server_default=None)
        lote.drop_column('costo_envio')
        lote.drop_column('subtotal_productos')

    op.drop_table('configuracion_tienda')
