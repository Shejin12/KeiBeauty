"""interruptor de envio gratis

Agrega la clave de configuracion `envio_gratis_activo`, que permite encender
y apagar la promocion de envio gratis desde el panel de administracion.

Solo es una insercion de datos: la tabla `configuracion_tienda` ya existe.
El valor inicial es 'true' (envio gratis activo), que es el comportamiento que
venia funcionando.

Revision ID: 2026_envio_gratis_activo
Revises: 2026_producto_descuentos
Create Date: 2026-10-22
"""
from alembic import op
import sqlalchemy as sa

revision = '2026_envio_gratis_activo'
down_revision = '2026_producto_descuentos'
branch_labels = None
depends_on = None

CLAVE = 'envio_gratis_activo'
VALOR_INICIAL = 'true'
DESCRIPCION = 'Indica si la promocion de envio gratis esta activa'


def upgrade():
    tabla = sa.table(
        'configuracion_tienda',
        sa.column('clave', sa.String),
        sa.column('valor', sa.String),
        sa.column('descripcion', sa.String),
    )
    # Solo se inserta si no existe: no pisa lo que haya configurado el admin.
    existe = op.get_bind().execute(
        sa.text('SELECT 1 FROM configuracion_tienda WHERE clave = :clave'), {'clave': CLAVE}
    ).first()
    if not existe:
        op.bulk_insert(tabla, [{
            'clave': CLAVE,
            'valor': VALOR_INICIAL,
            'descripcion': DESCRIPCION
        }])


def downgrade():
    op.execute(
        sa.text('DELETE FROM configuracion_tienda WHERE clave = :clave').bindparams(clave=CLAVE)
    )
