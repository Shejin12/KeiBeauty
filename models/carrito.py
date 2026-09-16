from models.db import db
from datetime import datetime
import secrets


class Carrito(db.Model):
    __tablename__ = 'carritos'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=True)
    guest_token = db.Column(db.String(64), unique=True, nullable=True, index=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    usuario = db.relationship('Usuario', back_populates='carrito')
    detalles = db.relationship('DetalleCarrito', back_populates='carrito', cascade='all, delete-orphan')

    @classmethod
    def generar_guest_token(cls):
        return secrets.token_urlsafe(32)

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'guest_token': self.guest_token,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'detalles': [d.to_dict() for d in self.detalles]
        }

    def calcular_total(self):
        return sum(d.subtotal for d in self.detalles)

    def __repr__(self):
        return f'<Carrito usuario_id={self.usuario_id} guest_token={self.guest_token}>'


class DetalleCarrito(db.Model):
    __tablename__ = 'detalle_carrito'

    id = db.Column(db.Integer, primary_key=True)
    carrito_id = db.Column(db.Integer, db.ForeignKey('carritos.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, default=1, nullable=False)
    fecha_agregado = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    carrito = db.relationship('Carrito', back_populates='detalles')
    producto = db.relationship('Producto', back_populates='detalle_carrito')

    @property
    def subtotal(self):
        return float(self.producto.precio) * self.cantidad if self.producto else 0

    def to_dict(self):
        return {
            'id': self.id,
            'carrito_id': self.carrito_id,
            'producto_id': self.producto_id,
            'cantidad': self.cantidad,
            'fecha_agregado': self.fecha_agregado.isoformat() if self.fecha_agregado else None,
            'subtotal': self.subtotal,
            'producto': self.producto.to_dict() if self.producto else None
        }

    def __repr__(self):
        return f'<DetalleCarrito carrito_id={self.carrito_id} producto_id={self.producto_id}>'