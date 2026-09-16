from models.db import db
from datetime import datetime


class Resena(db.Model):
    __tablename__ = 'resenas'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    calificacion = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    usuario = db.relationship('Usuario', back_populates='resenas')
    producto = db.relationship('Producto', back_populates='resenas')

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'producto_id': self.producto_id,
            'calificacion': self.calificacion,
            'comentario': self.comentario,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'usuario_nombre': self.usuario.nombre if self.usuario else None
        }

    def __repr__(self):
        return f'<Resena {self.id} usuario={self.usuario_id} producto={self.producto_id}>'