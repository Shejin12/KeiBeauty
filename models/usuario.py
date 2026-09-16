from werkzeug.security import generate_password_hash, check_password_hash
from models.db import db
from datetime import datetime


class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    direccion_envio = db.Column(db.Text)
    rol = db.Column(db.String(20), default='cliente', nullable=False)
    two_factor_enabled = db.Column(db.Boolean, default=True, nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    carrito = db.relationship('Carrito', back_populates='usuario', uselist=False, cascade='all, delete-orphan')
    pedidos = db.relationship('Pedido', back_populates='usuario', cascade='all, delete-orphan')
    resenas = db.relationship('Resena', back_populates='usuario', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'telefono': self.telefono,
            'direccion_envio': self.direccion_envio,
            'rol': self.rol,
            'two_factor_enabled': self.two_factor_enabled,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }

    def __repr__(self):
        return f'<Usuario {self.email}>'