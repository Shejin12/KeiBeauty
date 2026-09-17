from models.db import db
from datetime import datetime

class InventarioMovimiento(db.Model):
    __tablename__ = 'inventario_movimientos'
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    costo_unitario = db.Column(db.Numeric(10, 2), nullable=True)  # Costo por unidad solo para entradas (lote)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'tipo': self.tipo,
            'cantidad': self.cantidad,
            'costo_unitario': float(self.costo_unitario) if self.costo_unitario is not None else None,
            'costo_total': float(self.costo_unitario * self.cantidad) if self.costo_unitario is not None else None,
            'fecha': self.fecha.isoformat() if self.fecha else None
        }
