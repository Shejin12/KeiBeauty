from models.db import db
from datetime import datetime, timedelta
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import backref


class CodigoRecuperacion(db.Model):
    """Códigos de 6 dígitos para restablecer la contraseña (en vez de un enlace)."""
    __tablename__ = 'codigo_recuperacion'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    codigo_hash = db.Column(db.String(255), nullable=False)
    fecha_vencimiento = db.Column(db.DateTime, nullable=False)
    usado = db.Column(db.Boolean, default=False, nullable=False)
    intentos_fallidos = db.Column(db.Integer, default=0, nullable=False)
    ip_solicitud = db.Column(db.String(45))

    # cascade 'all, delete-orphan': al eliminar el usuario se eliminan sus codigos
    # (sin esto el ORM intenta poner usuario_id = NULL y revienta el NOT NULL).
    usuario = db.relationship(
        'Usuario',
        backref=backref('codigos_recuperacion', cascade='all, delete-orphan')
    )

    @classmethod
    def crear_codigo(cls, usuario_id, ip=None, minutos_validez=15):
        """Genera un código de 6 dígitos, lo hashea y lo guarda en BD."""
        # Invalidar códigos previos no usados del mismo usuario
        cls.query.filter_by(usuario_id=usuario_id, usado=False).update({'usado': True})

        codigo = secrets.randbelow(900000) + 100000
        codigo_hash = generate_password_hash(str(codigo))
        fecha_vencimiento = datetime.utcnow() + timedelta(minutes=minutos_validez)

        codigo_recuperacion = cls(
            usuario_id=usuario_id,
            codigo_hash=codigo_hash,
            fecha_vencimiento=fecha_vencimiento,
            ip_solicitud=ip
        )
        db.session.add(codigo_recuperacion)
        db.session.commit()

        return str(codigo), codigo_recuperacion

    @classmethod
    def validar_codigo(cls, usuario_id, codigo_plano):
        """Valida un código de recuperación. Retorna (codigo, error)."""
        codigo = cls.query.filter_by(
            usuario_id=usuario_id,
            usado=False
        ).filter(
            CodigoRecuperacion.fecha_vencimiento > datetime.utcnow()
        ).order_by(CodigoRecuperacion.fecha_solicitud.desc()).first()

        if not codigo:
            return None, 'No hay código activo o ha expirado'

        if codigo.intentos_fallidos >= 5:
            return None, 'Demasiados intentos fallidos, solicitá un nuevo código'

        if not check_password_hash(codigo.codigo_hash, str(codigo_plano)):
            codigo.intentos_fallidos += 1
            db.session.commit()
            return None, 'Código incorrecto'

        return codigo, None

    def marcar_como_usado(self):
        self.usado = True
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'fecha_solicitud': self.fecha_solicitud.isoformat() if self.fecha_solicitud else None,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None,
            'usado': self.usado
        }

    def __repr__(self):
        return f'<CodigoRecuperacion usuario_id={self.usuario_id} usado={self.usado}>'
