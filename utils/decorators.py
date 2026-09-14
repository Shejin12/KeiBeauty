from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models import db, Usuario


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        usuario_id = get_jwt_identity()
        usuario = db.session.get(Usuario, usuario_id)
        if not usuario or usuario.rol != 'admin':
            return jsonify({'error': 'Acceso denegado. Se requiere rol de administrador.'}), 403
        return fn(*args, **kwargs)
    return wrapper


def cliente_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        usuario_id = get_jwt_identity()
        usuario = db.session.get(Usuario, usuario_id)
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado.'}), 404
        return fn(*args, **kwargs)
    return wrapper