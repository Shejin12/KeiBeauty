from models.db import db
from datetime import datetime

class Notificacion(db.Model):
    __tablename__ = 'notificaciones'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False, index=True)
    tipo_id = db.Column(db.Integer, db.ForeignKey('catalogo_tipo_notificacion.id'), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    leido = db.Column(db.Boolean, default=False, nullable=False)
    datos = db.Column(db.JSON, nullable=True)  # {pedido_id, producto_id, etc}
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    usuario = db.relationship('Usuario', backref='notificaciones')
    tipo = db.relationship('CatalogoTipoNotificacion', backref='notificaciones')

    @property
    def tipo_nombre(self):
        """Nombre del tipo (texto) para compatibilidad con el frontend."""
        return self.tipo.nombre if self.tipo else None

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'tipo_id': self.tipo_id,
            'tipo': self.tipo_nombre,
            'titulo': self.titulo,
            'mensaje': self.mensaje,
            'leido': self.leido,
            'datos': self.datos,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
