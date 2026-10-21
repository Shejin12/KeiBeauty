from models.db import db
from datetime import datetime


class UsuarioDireccion(db.Model):
    """Direcciones de envío que un usuario puede tener guardadas en su cuenta."""

    __tablename__ = 'usuario_direcciones'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    alias = db.Column(db.String(50), nullable=True)
    direccion = db.Column(db.Text, nullable=False)
    es_principal = db.Column(db.Boolean, default=False, nullable=False)
    activa = db.Column(db.Boolean, default=True, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    usuario = db.relationship(
        'Usuario',
        backref=db.backref('mis_direcciones', cascade='all, delete-orphan')
    )

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'alias': self.alias,
            'direccion': self.direccion,
            'es_principal': self.es_principal,
            'activa': self.activa,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }

    def __repr__(self):
        return f'<UsuarioDireccion {self.id} usuario_id={self.usuario_id}>'


class UsuarioTelefono(db.Model):
    """Telefonos de contacto que un usuario puede tener guardados en su cuenta."""

    __tablename__ = 'usuario_telefonos'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    telefono = db.Column(db.String(20), nullable=False)
    es_principal = db.Column(db.Boolean, default=False, nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    usuario = db.relationship(
        'Usuario',
        backref=db.backref('mis_telefonos', cascade='all, delete-orphan')
    )

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'telefono': self.telefono,
            'es_principal': self.es_principal,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }

    def __repr__(self):
        return f'<UsuarioTelefono {self.id} usuario_id={self.usuario_id}>'
