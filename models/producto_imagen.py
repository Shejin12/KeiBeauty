from models.db import db
from datetime import datetime


class ProductoImagen(db.Model):
    __tablename__ = 'producto_imagenes'

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id', ondelete='CASCADE'), nullable=False, index=True)
    imagen_url = db.Column(db.String(500), nullable=False)
    es_principal = db.Column(db.Boolean, default=False, nullable=False)
    orden = db.Column(db.Integer, default=0, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    producto = db.relationship('Producto', back_populates='imagenes')

    def to_dict(self):
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'imagen_url': self.imagen_url,
            'es_principal': self.es_principal,
            'orden': self.orden,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }

    def __repr__(self):
        return f'<ProductoImagen {self.id} producto={self.producto_id} principal={self.es_principal}>'
