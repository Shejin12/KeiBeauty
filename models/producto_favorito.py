from models.db import db
from datetime import datetime


class ProductoFavorito(db.Model):
    __tablename__ = 'producto_favorito'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False, index=True)
    fecha_agregado = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'producto_id', name='uq_usuario_producto_favorito'),
    )

    usuario = db.relationship('Usuario', backref='favoritos')
    producto = db.relationship('Producto', backref='favoritos')

    @classmethod
    def agregar(cls, usuario_id, producto_id):
        """Agrega un producto a favoritos si no existe."""
        existente = cls.query.filter_by(usuario_id=usuario_id, producto_id=producto_id).first()
        if existente:
            return existente, False
        
        favorito = cls(usuario_id=usuario_id, producto_id=producto_id)
        db.session.add(favorito)
        db.session.commit()
        return favorito, True

    @classmethod
    def quitar(cls, usuario_id, producto_id):
        """Quita un producto de favoritos."""
        favorito = cls.query.filter_by(usuario_id=usuario_id, producto_id=producto_id).first()
        if not favorito:
            return False
        db.session.delete(favorito)
        db.session.commit()
        return True

    @classmethod
    def es_favorito(cls, usuario_id, producto_id):
        """Verifica si un producto está en favoritos del usuario."""
        return cls.query.filter_by(usuario_id=usuario_id, producto_id=producto_id).first() is not None

    @classmethod
    def obtener_favoritos(cls, usuario_id):
        """Obtiene todos los favoritos del usuario con info del producto."""
        return cls.query.filter_by(usuario_id=usuario_id).order_by(cls.fecha_agregado.desc()).all()

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'producto_id': self.producto_id,
            'fecha_agregado': self.fecha_agregado.isoformat() if self.fecha_agregado else None,
            'producto': self.producto.to_dict() if self.producto else None
        }

    def __repr__(self):
        return f'<ProductoFavorito usuario_id={self.usuario_id} producto_id={self.producto_id}>'