"""agregar guest_token y usuario_id nullable en carritos

Revision ID: 2026_guest_token_carritos
Revises: 188f4f333d85
Create Date: 2026-09-16
"""
from alembic import op
import sqlalchemy as sa

revision = '2026_guest_token_carritos'
down_revision = '188f4f333d85'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('carritos', sa.Column('guest_token', sa.String(length=64), nullable=True))
    op.create_index('ix_carritos_guest_token', 'carritos', ['guest_token'], unique=True)
    op.alter_column('carritos', 'usuario_id', existing_type=sa.Integer(), nullable=True)

def downgrade():
    op.drop_index('ix_carritos_guest_token', table_name='carritos')
    op.drop_column('carritos', 'guest_token')
    op.alter_column('carritos', 'usuario_id', existing_type=sa.Integer(), nullable=False)
