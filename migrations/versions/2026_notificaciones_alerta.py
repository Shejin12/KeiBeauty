"""notificaciones y alerta stock

Revision ID: 2026_notificaciones_alerta
Revises: 2026_producto_imagenes_galeria
Create Date: 2026-09-17
"""
from alembic import op
import sqlalchemy as sa

revision = '2026_notificaciones_alerta'
down_revision = '2026_producto_imagenes_galeria'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'notificaciones',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('titulo', sa.String(length=200), nullable=False),
        sa.Column('mensaje', sa.Text(), nullable=False),
        sa.Column('leido', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('datos', sa.JSON(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_notificaciones_usuario_id', 'notificaciones', ['usuario_id'])
    op.create_index('ix_notificaciones_leido', 'notificaciones', ['leido'])

    op.create_table(
        'producto_alertas',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('producto_id', sa.Integer(), sa.ForeignKey('productos.id', ondelete='CASCADE'), nullable=False),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False),
        sa.Column('activa', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('producto_id', 'usuario_id', name='uq_producto_usuario_alerta')
    )
    op.create_index('ix_producto_alertas_producto_id', 'producto_alertas', ['producto_id'])
    op.create_index('ix_producto_alertas_usuario_id', 'producto_alertas', ['usuario_id'])

def downgrade():
    op.drop_index('ix_producto_alertas_usuario_id', table_name='producto_alertas')
    op.drop_index('ix_producto_alertas_producto_id', table_name='producto_alertas')
    op.drop_table('producto_alertas')
    op.drop_index('ix_notificaciones_leido', table_name='notificaciones')
    op.drop_index('ix_notificaciones_usuario_id', table_name='notificaciones')
    op.drop_table('notificaciones')
