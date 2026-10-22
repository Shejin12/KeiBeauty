from models.db import db
from models.producto_descuento import ProductoDescuento
from datetime import datetime
from decimal import Decimal
import sqlalchemy as sa


class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    ingredientes_clave = db.Column(db.Text)
    tipo_piel = db.Column(db.String(100))
    tamano = db.Column(db.String(255), nullable=True)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0, nullable=False)
    imagen_url = db.Column(db.String(255))
    estado_id = db.Column(db.Integer, db.ForeignKey('catalogo_estado_producto.id'), nullable=False)
    marca_id = db.Column(db.Integer, db.ForeignKey('marcas.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    marca = db.relationship('Marca', back_populates='productos')
    categoria = db.relationship('Categoria', back_populates='productos')
    estado = db.relationship('CatalogoEstadoProducto', backref='productos')
    detalle_carrito = db.relationship('DetalleCarrito', back_populates='producto', cascade='all, delete-orphan')
    detalle_pedidos = db.relationship('DetallePedido', back_populates='producto', cascade='all, delete-orphan')
    resenas = db.relationship('Resena', back_populates='producto', cascade='all, delete-orphan')
    imagenes = db.relationship('ProductoImagen', back_populates='producto', cascade='all, delete-orphan', order_by='ProductoImagen.orden')
    descuentos = db.relationship('ProductoDescuento', back_populates='producto', cascade='all, delete-orphan')

    def _imagen_principal_url(self):
        # Buscar imagen principal en galería, fallback a imagen_url
        if self.imagenes:
            for img in self.imagenes:
                if img.es_principal:
                    return img.imagen_url
            return self.imagenes[0].imagen_url
        return self.imagen_url

    @property
    def estado_nombre(self):
        """Nombre del estado (texto) para compatibilidad con el frontend."""
        return self.estado.nombre if self.estado else None

    def descuento_vigente(self):
        """Descuento vigente del producto (o None).

        Si la relacion `descuentos` ya esta cargada se resuelve en memoria para
        no disparar una consulta por producto en los listados.
        """
        if 'descuentos' not in sa.inspect(self).unloaded:
            ahora = datetime.utcnow()
            candidatos = [
                d for d in self.descuentos
                if d.activo and d.fecha_inicio <= ahora <= d.fecha_fin
            ]
            candidatos.sort(key=lambda d: (-float(d.porcentaje), d.fecha_fin))
            return candidatos[0] if candidatos else None
        return ProductoDescuento.vigente_para(self.id)

    def precio_con_descuento(self):
        """Precio final del producto con el descuento vigente aplicado."""
        descuento = self.descuento_vigente()
        if not descuento:
            return Decimal(str(self.precio))
        return descuento.precio_con_descuento(self.precio)

    def to_dict(self):
        # Ordenar imágenes: principal primero
        imagenes_ordenadas = []
        if self.imagenes:
            imagenes_ordenadas = sorted(self.imagenes, key=lambda x: (not x.es_principal, x.orden, x.id))
        descuento = self.descuento_vigente()
        precio_final = self.precio_con_descuento()
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'ingredientes_clave': self.ingredientes_clave,
            'tipo_piel': self.tipo_piel,
            'tamano': self.tamano or '',
            'precio': float(self.precio),
            # Precio con el descuento vigente aplicado (precio sigue siendo el
            # precio de catalogo para no romper a los consumidores existentes).
            'precio_descuento': float(precio_final),
            'tiene_descuento': descuento is not None,
            'porcentaje_descuento': float(descuento.porcentaje) if descuento else 0.0,
            'stock': self.stock,
            'imagen_url': self._imagen_principal_url(),
            'imagenes': [img.to_dict() for img in imagenes_ordenadas],
            'estado_id': self.estado_id,
            'estado': self.estado_nombre,
            'marca_id': self.marca_id,
            'categoria_id': self.categoria_id,
            'marca_nombre': self.marca.nombre if self.marca else None,
            'marca_logo_url': self.marca.logo_url if self.marca and self.marca.logo_url else None,
            'categoria_nombre': self.categoria.nombre if self.categoria else None,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }

    def __repr__(self):
        return f'<Producto {self.nombre}>'