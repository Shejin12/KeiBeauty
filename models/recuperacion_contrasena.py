from models.db import db
from datetime import datetime, timedelta
import hashlib
import secrets


class RecuperacionContrasena(db.Model):
    __tablename__ = 'recuperacion_contrasena'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    token_hash = db.Column(db.String(64), nullable=False, unique=True)
    fecha_vencimiento = db.Column(db.DateTime, nullable=False)
    usado = db.Column(db.Boolean, default=False, nullable=False)

    usuario = db.relationship('Usuario', backref='recuperaciones_contrasena')

    @staticmethod
    def generar_token():
        """Genera un token aleatorio seguro"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_token(token):
        """Genera hash SHA-256 del token"""
        return hashlib.sha256(token.encode()).hexdigest()

    @classmethod
    def crear_solicitud(cls, usuario_id, expiracion_horas=24):
        """Crea una nueva solicitud de recuperación de contraseña"""
        # Invalidar solicitudes previas no usadas del mismo usuario
        cls.query.filter_by(usuario_id=usuario_id, usado=False).update({'usado': True})
        
        token = cls.generar_token()
        token_hash = cls.hash_token(token)
        fecha_vencimiento = datetime.utcnow() + timedelta(hours=expiracion_horas)
        
        recuperacion = cls(
            usuario_id=usuario_id,
            token_hash=token_hash,
            fecha_vencimiento=fecha_vencimiento
        )
        db.session.add(recuperacion)
        db.session.commit()
        
        return token, recuperacion

    @classmethod
    def validar_token(cls, token):
        """Valida un token de recuperación y retorna la solicitud si es válida"""
        token_hash = cls.hash_token(token)
        recuperacion = cls.query.filter_by(token_hash=token_hash, usado=False).first()
        
        if not recuperacion:
            return None, 'Token inválido o ya utilizado'
        
        if recuperacion.fecha_vencimiento < datetime.utcnow():
            return None, 'Token expirado'
        
        return recuperacion, None

    def marcar_como_usado(self):
        """Marca el token como usado"""
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
        return f'<RecuperacionContrasena usuario_id={self.usuario_id} usado={self.usado}>'