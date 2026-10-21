"""cascade de FKs hacia usuarios

Agrega ON DELETE CASCADE a las FKs de codigo_2fa y recuperacion_contrasena
hacia usuarios. Sin esto, al eliminar un usuario el ORM intenta poner
usuario_id = NULL en las filas hijas y la restriccion NOT NULL revienta.

Los modelos ademas declaran cascade 'all, delete-orphan' a nivel ORM, que es
lo que garantiza el borrado en cascada en cualquier motor (incluido SQLite,
que no aplica ON DELETE). Esta migracion deja el ON DELETE CASCADE en
PostgreSQL como red de seguridad a nivel de base de datos.

Revision ID: 2026_cascade_usuarios_fk
Revises: 2026_codigo_recuperacion
Create Date: 2026-10-21
"""
from alembic import op
import sqlalchemy as sa

revision = '2026_cascade_usuarios_fk'
down_revision = '2026_codigo_recuperacion'
branch_labels = None
depends_on = None

TABLAS = ['codigo_2fa', 'recuperacion_contrasena']

# Nombre con el que queda cada constraint tras la migracion
NOMBRES = {
    'codigo_2fa': 'fk_codigo_2fa_usuario_id',
    'recuperacion_contrasena': 'fk_recuperacion_contrasena_usuario_id',
}


def _es_postgres():
    return op.get_bind().dialect.name == 'postgresql'


def _constraints_actual(tabla):
    """Devuelve los nombres de las FK de la tabla que apuntan a usuarios(usuario_id)."""
    return [r[0] for r in op.get_bind().execute(sa.text("""
        SELECT c.conname
        FROM pg_constraint c
        JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey)
        WHERE c.conrelid = to_regclass(:tabla)
          AND c.contype = 'f'
          AND a.attname = 'usuario_id'
    """), {'tabla': tabla}).fetchall()]


def _recrear_fk(tabla, nombre_destino, ondelete):
    for nombre in _constraints_actual(tabla):
        op.execute(f'ALTER TABLE {tabla} DROP CONSTRAINT IF EXISTS {nombre}')
    ondelete_sql = ' ON DELETE CASCADE' if ondelete else ''
    op.execute(
        f'ALTER TABLE {tabla} ADD CONSTRAINT {nombre_destino} '
        f'FOREIGN KEY (usuario_id) REFERENCES usuarios(id){ondelete_sql}'
    )


def upgrade():
    if not _es_postgres():
        # En SQLite el borrado en cascada lo resuelve el cascade del ORM
        # (cascade='all, delete-orphan'); SQLite no aplica ON DELETE.
        return
    for tabla in TABLAS:
        _recrear_fk(tabla, NOMBRES[tabla], ondelete=True)


def downgrade():
    if not _es_postgres():
        return
    for tabla in TABLAS:
        _recrear_fk(tabla, NOMBRES[tabla], ondelete=False)
