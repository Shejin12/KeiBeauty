from models.db import db
from datetime import datetime


class Pedido(db.Model):
    __tablename__ = 'pedidos'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    monto_total = db.Column(db.Numeric(10, 2), nullable=False)
    estado_id = db.Column(db.Integer, db.ForeignKey('catalogo_estado_pedido.id'), nullable=False)
    direccion_envio = db.Column(db.Text, nullable=False)
    email_contacto = db.Column(db.String(150), nullable=True)
    telefono_contacto = db.Column(db.String(20), nullable=True)
    fecha_pedido = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    url_guia = db.Column(db.String(500), nullable=True)

    usuario = db.relationship('Usuario', back_populates='pedidos')
    estado = db.relationship('CatalogoEstadoPedido', backref='pedidos')
    detalles = db.relationship('DetallePedido', back_populates='pedido', cascade='all, delete-orphan')

    @property
    def estado_nombre(self):
        """Nombre del estado (texto) para compatibilidad con el frontend."""
        return self.estado.nombre if self.estado else None

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'monto_total': float(self.monto_total),
            'estado_id': self.estado_id,
            'estado': self.estado_nombre,
            'direccion_envio': self.direccion_envio,
            'email_contacto': self.email_contacto,
            'telefono_contacto': self.telefono_contacto,
            'fecha_pedido': self.fecha_pedido.isoformat() if self.fecha_pedido else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'url_guia': self.url_guia,
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
    nombre_producto = db.Column(db.String(200), nullable=True)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

    pedido = db.relationship('Pedido', back_populates='detalles')
    producto = db.relationship('Producto', back_populates='detalle_pedidos')

    def to_dict(self):
        return {
            'id': self.id,
            'pedido_id': self.pedido_id,
            'producto_id': self.producto_id,
            'precio_unitario': float(self.precio_unitario),
            'cantidad': self.cantidad,
            'nombre_producto': self.nombre_producto,
            'subtotal': float(self.subtotal),
            'producto': self.producto.to_dict() if self.producto else None
        }

    def __repr__(self):
        return f'<DetallePedido pedido_id={self.pedido_id} producto_id={self.producto_id}>'