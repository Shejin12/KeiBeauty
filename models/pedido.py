from models.db import db
from datetime import datetime


class Pedido(db.Model):
    __tablename__ = 'pedidos'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    monto_total = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(db.String(20), default='pendiente', nullable=False)
    direccion_envio = db.Column(db.Text, nullable=False)
    fecha_pedido = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    usuario = db.relationship('Usuario', back_populates='pedidos')
    detalles = db.relationship('DetallePedido', back_populates='pedido', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'monto_total': float(self.monto_total),
            'estado': self.estado,
            'direccion_envio': self.direccion_envio,
            'fecha_pedido': self.fecha_pedido.isoformat() if self.fecha_pedido else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'detalles': [d.to_dict() for d in self.detalles]
        }

    def __repr__(self):
        return f'<Pedido {self.id} usuario_id={self.usuario_id}>'


class DetallePedido(db.Model):
    __tablename__ = 'detalle_pedidos'

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    cantidad = db.Column(db.Integer, default=1, nullable=False)

    pedido = db.relationship('Pedido', back_populates='detalles')
    producto = db.relationship('Producto', back_populates='detalle_pedidos')

    @property
    def subtotal(self):
        return float(self.precio_unitario) * self.cantidad

    def to_dict(self):
        return {
            'id': self.id,
            'pedido_id': self.pedido_id,
            'producto_id': self.producto_id,
            'precio_unitario': float(self.precio_unitario),
            'cantidad': self.cantidad,
            'subtotal': self.subtotal,
            'producto': self.producto.to_dict() if self.producto else None
        }

    def __repr__(self):
        return f'<DetallePedido pedido_id={self.pedido_id} producto_id={self.producto_id}>'