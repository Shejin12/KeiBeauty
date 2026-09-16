from models.db import db


class Marca(db.Model):
    __tablename__ = 'marcas'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    logo_url = db.Column(db.String(255))

    productos = db.relationship('Producto', back_populates='marca', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'logo_url': self.logo_url
        }

    def __repr__(self):
        return f'<Marca {self.nombre}>'