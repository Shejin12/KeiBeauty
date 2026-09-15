from models.db import db
from datetime import datetime, timedelta
import secrets
from werkzeug.security import generate_password_hash, check_password_hash


class Codigo2FA(db.Model):
    __tablename__ = 'codigo_2fa'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    codigo_hash = db.Column(db.String(255), nullable=False)
    fecha_vencimiento = db.Column(db.DateTime, nullable=False)
    usado = db.Column(db.Boolean, default=False, nullable=False)
    intentos_fallidos = db.Column(db.Integer, default=0, nullable=False)
    ip_solicitud = db.Column(db.String(45))

    usuario = db.relationship('Usuario', backref='codigos_2fa')

    @classmethod
    def crear_codigo(cls, usuario_id, ip=None):
        """Genera un código de 6 dígitos, lo hashea y lo guarda en BD."""
        # Invalidar códigos previos no usados del mismo usuario
        cls.query.filter_by(usuario_id=usuario_id, usado=False).update({'usado': True})

        # Generar código de 6 dígitos
        codigo = secrets.randbelow(900000) + 100000
        codigo_hash = generate_password_hash(str(codigo))
        fecha_vencimiento = datetime.utcnow() + timedelta(minutes=5)

        codigo_2fa = cls(
            usuario_id=usuario_id,
            codigo_hash=codigo_hash,
            fecha_vencimiento=fecha_vencimiento,
            ip_solicitud=ip
        )
        db.session.add(codigo_2fa)
        db.session.commit()

        return str(codigo), codigo_2fa

    @classmethod
    def validar_codigo(cls, usuario_id, codigo_plano):
        """Valida un código de 2FA."""
        codigo_2fa = cls.query.filter_by(
            usuario_id=usuario_id,
            usado=False
        ).filter(
            Codigo2FA.fecha_vencimiento > datetime.utcnow()
        ).order_by(Codigo2FA.fecha_solicitud.desc()).first()

        if not codigo_2fa:
            return None, 'No hay código activo o ha expirado'

        if codigo_2fa.intentos_fallidos >= 5:
            return None, 'Demasiados intentos fallidos, solicitá un nuevo código'

        if not check_password_hash(codigo_2fa.codigo_hash, str(codigo_plano)):
            codigo_2fa.intentos_fallidos += 1
            db.session.commit()
            return None, 'Código incorrecto'

        return codigo_2fa, None

    def marcar_como_usado(self):
        self.usado = True
        db.session.commit()


# Agregar two_factor_enabled al modelo Usuario
def init_usuario_2fa():
    """Agregar campo two_factor_enabled al modelo Usuario."""
    # Esto se hará en la migración
    pass