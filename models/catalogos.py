from models.db import db


class CatalogoRolUsuario(db.Model):
    """Catálogo de roles de usuario (admin, cliente)."""
    __tablename__ = 'catalogo_rol_usuario'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=True)

    @classmethod
    def por_nombre(cls, nombre):
        """Busca un rol por su nombre. Retorna None si no existe."""
        return cls.query.filter_by(nombre=nombre).first()

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'activo': self.activo,
        }

    def __repr__(self):
        return f'<CatalogoRolUsuario {self.nombre}>'


class CatalogoEstadoProducto(db.Model):
    """Catálogo de estados de producto (activo, inactivo, agotado)."""
    __tablename__ = 'catalogo_estado_producto'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=True)

    @classmethod
    def por_nombre(cls, nombre):
        """Busca un estado por su nombre. Retorna None si no existe."""
        return cls.query.filter_by(nombre=nombre).first()

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'activo': self.activo,
        }

    def __repr__(self):
        return f'<CatalogoEstadoProducto {self.nombre}>'


class CatalogoEstadoPedido(db.Model):
    """Catálogo de estados de pedido (pendiente, confirmado, enviado, entregado, cancelado)."""
    __tablename__ = 'catalogo_estado_pedido'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=True)

    @classmethod
    def por_nombre(cls, nombre):
        """Busca un estado por su nombre. Retorna None si no existe."""
        return cls.query.filter_by(nombre=nombre).first()

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'activo': self.activo,
        }

    def __repr__(self):
        return f'<CatalogoEstadoPedido {self.nombre}>'


class CatalogoTipoNotificacion(db.Model):
    """Catálogo de tipos de notificación (pedido_estado, pedido_guia, producto_stock)."""
    __tablename__ = 'catalogo_tipo_notificacion'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=True)

    @classmethod
    def por_nombre(cls, nombre):
        """Busca un tipo por su nombre. Retorna None si no existe."""
        return cls.query.filter_by(nombre=nombre).first()

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'activo': self.activo,
        }

    def __repr__(self):
        return f'<CatalogoTipoNotificacion {self.nombre}>'
