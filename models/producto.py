from models.db import db
from datetime import datetime


class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    ingredientes_clave = db.Column(db.Text)
    tipo_piel = db.Column(db.String(100))
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0, nullable=False)
    imagen_url = db.Column(db.String(255))
    estado = db.Column(db.String(20), default='activo', nullable=False)
    marca_id = db.Column(db.Integer, db.ForeignKey('marcas.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    marca = db.relationship('Marca', back_populates='productos')
    categoria = db.relationship('Categoria', back_populates='productos')
    detalle_carrito = db.relationship('DetalleCarrito', back_populates='producto', cascade='all, delete-orphan')
    detalle_pedidos = db.relationship('DetallePedido', back_populates='producto', cascade='all, delete-orphan')
    resenas = db.relationship('Resena', back_populates='producto', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'ingredientes_clave': self.ingredientes_clave,
            'tipo_piel': self.tipo_piel,
            'precio': float(self.precio),
            'stock': self.stock,
            'imagen_url': self.imagen_url,
            'estado': self.estado,
            'marca_id': self.marca_id,
            'categoria_id': self.categoria_id,
            'marca_nombre': self.marca.nombre if self.marca else None,
            'categoria_nombre': self.categoria.nombre if self.categoria else None,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }

    def __repr__(self):
        return f'<Producto {self.nombre}>'