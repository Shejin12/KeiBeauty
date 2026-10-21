"""codigo recuperacion de contrasena

Tabla para los códigos de 6 dígitos que sustituyen al enlace de
restablecimiento de contraseña. Misma estructura que codigo_2fa.

Revision ID: 2026_codigo_recuperacion
Revises: 2026_catalogo_tipo_notificacion
Create Date: 2026-10-21
"""
from alembic import op
import sqlalchemy as sa

revision = '2026_codigo_recuperacion'
down_revision = '2026_catalogo_tipo_notificacion'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'codigo_recuperacion',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('fecha_solicitud', sa.DateTime(), nullable=False),
        sa.Column('codigo_hash', sa.String(length=255), nullable=False),
        sa.Column('fecha_vencimiento', sa.DateTime(), nullable=False),
        sa.Column('usado', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('intentos_fallidos', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ip_solicitud', sa.String(length=45), nullable=True),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], name='fk_codigo_recuperacion_usuario_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_codigo_recuperacion_usuario_id', 'codigo_recuperacion', ['usuario_id'])


def downgrade():
    op.drop_index('ix_codigo_recuperacion_usuario_id', table_name='codigo_recuperacion')
    op.drop_table('codigo_recuperacion')
