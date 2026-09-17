from models.db import db
from datetime import datetime

class Notificacion(db.Model):
    __tablename__ = 'notificaciones'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False, index=True)
    tipo = db.Column(db.String(50), nullable=False)  # pedido_estado, pedido_guia, producto_stock
    titulo = db.Column(db.String(200), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    leido = db.Column(db.Boolean, default=False, nullable=False)
    datos = db.Column(db.JSON, nullable=True)  # {pedido_id, producto_id, etc}
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    usuario = db.relationship('Usuario', backref='notificaciones')

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'tipo': self.tipo,
            'titulo': self.titulo,
            'mensaje': self.mensaje,
            'leido': self.leido,
            'datos': self.datos,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
