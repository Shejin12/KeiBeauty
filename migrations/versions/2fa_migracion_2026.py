"""add 2fa tables and fields

Revision ID: 2fa_migracion_2026
Revises: 19c2960f0082
Create Date: 2026-09-15 18:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '2fa_migracion_2026'
down_revision = '19c2960f0082'
branch_labels = None
depends_on = None


def upgrade():
    # Agregar campo two_factor_enabled a usuarios
    op.add_column('usuarios', sa.Column('two_factor_enabled', sa.Boolean(), nullable=False, server_default='false'))
    
    # Crear tabla codigo_2fa
    op.create_table('codigo_2fa',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('fecha_solicitud', sa.DateTime(), nullable=False),
        sa.Column('codigo_hash', sa.String(length=255), nullable=False),
        sa.Column('fecha_vencimiento', sa.DateTime(), nullable=False),
        sa.Column('usado', sa.Boolean(), nullable=False),
        sa.Column('intentos_fallidos', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ip_solicitud', sa.String(length=45), nullable=True),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('codigo_2fa')
    op.drop_column('usuarios', 'two_factor_enabled')
