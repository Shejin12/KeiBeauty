from models.db import db
from datetime import datetime
from decimal import Decimal


class ProductoDescuento(db.Model):
    """Descuento por porcentaje aplicado a un producto en un rango de fechas."""

    __tablename__ = 'producto_descuentos'

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(
        db.Integer,
        db.ForeignKey('productos.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    porcentaje = db.Column(db.Numeric(5, 2), nullable=False)
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    fecha_fin = db.Column(db.DateTime, nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    producto = db.relationship('Producto', back_populates='descuentos')

    @classmethod
    def vigente_para(cls, producto_id, momento=None):
        """Devuelve el descuento vigente de un producto (o None).

        Vigente = activo, dentro del rango de fechas y con la fecha de fin mas
        cercana. Si hay varios solapados se aplica el de mayor porcentaje; en
        caso de empate, el que termina antes.
        """
        momento = momento or datetime.utcnow()
        candidatos = cls.query.filter(
            cls.producto_id == producto_id,
            cls.activo.is_(True),
            cls.fecha_inicio <= momento,
            cls.fecha_fin >= momento
        ).order_by(cls.porcentaje.desc(), cls.fecha_fin.asc()).all()
        return candidatos[0] if candidatos else None

    @property
    def vigente(self):
        """Indica si el descuento está activo y dentro de su rango de fechas."""
        ahora = datetime.utcnow()
        return bool(self.activo and self.fecha_inicio <= ahora <= self.fecha_fin)

    def precio_con_descuento(self, precio_base):
        """Calcula el precio final aplicando el porcentaje de descuento."""
        base = Decimal(str(precio_base))
        factor = Decimal('1') - (Decimal(str(self.porcentaje)) / Decimal('100'))
        return (base * factor).quantize(Decimal('0.01'))

    def to_dict(self):
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'porcentaje': float(self.porcentaje),
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
            'activo': self.activo,
            'vigente': self.vigente,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }

    def __repr__(self):
        return f'<ProductoDescuento {self.id} producto_id={self.producto_id} {self.porcentaje}%>'


def precio_con_descuento_vigente(producto, momento=None):
    """Precio final de un producto con el descuento vigente aplicado.

    Es la única fuente de verdad del cálculo: la usan tanto el detalle del
    producto como la creación del pedido, para que nunca diverjan.
    """
    precio_base = Decimal(str(producto.precio))
    descuento = ProductoDescuento.vigente_para(producto.id, momento)
    if not descuento:
        return precio_base, None
    return descuento.precio_con_descuento(precio_base), descuento
