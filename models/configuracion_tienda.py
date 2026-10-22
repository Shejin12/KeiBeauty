from models.db import db
from datetime import datetime


class ConfiguracionTienda(db.Model):
    """Configuración general de la tienda en formato clave/valor.

    Cada fila es una opción editable desde el panel de administración
    (por ejemplo el costo de envío o el mínimo para envío gratis).
    """

    __tablename__ = 'configuracion_tienda'

    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(200), nullable=True)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @classmethod
    def obtener(cls, clave, default=None):
        """Devuelve el valor de una clave o `default` si no existe."""
        registro = cls.query.filter_by(clave=clave).first()
        return registro.valor if registro else default

    @classmethod
    def obtener_numero(cls, clave, default=0.0):
        """Devuelve el valor de una clave como float o `default` si no existe o no es numérico."""
        valor = cls.obtener(clave)
        if valor is None:
            return float(default)
        try:
            return float(str(valor).strip())
        except (TypeError, ValueError):
            return float(default)

    @classmethod
    def obtener_booleano(cls, clave, default=False):
        """Devuelve el valor de una clave como booleano.

        Acepta 'true'/'false', '1'/'0', 'si'/'no'. Si la clave no existe o el
        valor no se reconoce devuelve `default`.
        """
        valor = cls.obtener(clave)
        if valor is None:
            return bool(default)
        texto = str(valor).strip().lower()
        if texto in ('true', '1', 'si', 'sí', 'yes', 'activo', 'on'):
            return True
        if texto in ('false', '0', 'no', 'off', 'inactivo'):
            return False
        return bool(default)

    @classmethod
    def establecer(cls, clave, valor, descripcion=None):
        """Crea o actualiza una clave de configuración y devuelve el registro."""
        registro = cls.query.filter_by(clave=clave).first()
        if registro:
            registro.valor = str(valor)
            if descripcion is not None:
                registro.descripcion = descripcion
            registro.fecha_actualizacion = datetime.utcnow()
        else:
            registro = cls(clave=clave, valor=str(valor), descripcion=descripcion)
            db.session.add(registro)
        db.session.flush()
        return registro

    def to_dict(self):
        return {
            'id': self.id,
            'clave': self.clave,
            'valor': self.valor,
            'descripcion': self.descripcion,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }

    def __repr__(self):
        return f'<ConfiguracionTienda {self.clave}={self.valor}>'
