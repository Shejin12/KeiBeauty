from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from models import db, Usuario


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('estado') == 'en_autenticacion':
            return jsonify({'error': 'Token temporal de 2FA no válido para esta operación.', 'message': 'Complete la verificación 2FA primero.'}), 403
        usuario_id = get_jwt_identity()
        usuario = db.session.get(Usuario, usuario_id)
        if not usuario or usuario.rol_nombre != 'admin':
            return jsonify({'error': 'Acceso denegado. Se requiere rol de administrador.'}), 403
        return fn(*args, **kwargs)
    return wrapper


def cliente_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('estado') == 'en_autenticacion':
            return jsonify({'error': 'Token temporal de 2FA no válido para esta operación.', 'message': 'Complete la verificación 2FA primero.'}), 403
        usuario_id = get_jwt_identity()
        usuario = db.session.get(Usuario, usuario_id)
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado.'}), 404
        return fn(*args, **kwargs)
    return wrapper


def solo_en_autenticacion(fn):
    """Solo permite acceso si el JWT tiene estado 'en_autenticacion'."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('estado') != 'en_autenticacion':
            return jsonify({'error': 'Se requiere token de verificación 2FA.', 'message': 'Inicie sesión nuevamente para obtener un token temporal.'}), 403
        return fn(*args, **kwargs)
    return wrapper


def rechazar_en_autenticacion(fn):
    """Rechaza JWT con estado 'en_autenticacion', solo permite JWT completos."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('estado') == 'en_autenticacion':
            return jsonify({'error': 'Token temporal de 2FA no válido para esta operación.', 'message': 'Complete la verificación 2FA primero.'}), 403
        return fn(*args, **kwargs)
    return wrapper