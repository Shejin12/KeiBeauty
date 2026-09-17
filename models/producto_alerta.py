from models.db import db
from datetime import datetime

class ProductoAlerta(db.Model):
    __tablename__ = 'producto_alertas'

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id', ondelete='CASCADE'), nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False, index=True)
    activa = db.Column(db.Boolean, default=True, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    producto = db.relationship('Producto', backref='alertas')
    usuario = db.relationship('Usuario', backref='producto_alertas')

    __table_args__ = (db.UniqueConstraint('producto_id', 'usuario_id', name='uq_producto_usuario_alerta'),)

    def to_dict(self):
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'usuario_id': self.usuario_id,
            'activa': self.activa,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
