from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, get_jwt
from utils.decorators import rechazar_en_autenticacion
from models import db, Notificacion, ProductoAlerta, Producto
from datetime import datetime

notificaciones_bp = Blueprint('notificaciones', __name__, url_prefix='/api/notificaciones')

def crear_notificacion(usuario_id, tipo, titulo, mensaje, datos=None):
    """Helper para crear notificación"""
    try:
        notif = Notificacion(
            usuario_id=usuario_id,
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            datos=datos or {}
        )
        db.session.add(notif)
        db.session.commit()
        return notif
    except Exception as e:
        db.session.rollback()
        print(f"Error creando notificación: {e}")
        return None

@notificaciones_bp.route('', methods=['GET'])
@jwt_required()
@rechazar_en_autenticacion
def listar_notificaciones():
    try:
        usuario_id = int(get_jwt_identity())
        notifs = Notificacion.query.filter_by(usuario_id=usuario_id).order_by(Notificacion.fecha_creacion.desc()).limit(50).all()
        no_leidas = sum(1 for n in notifs if not n.leido)
        return jsonify({
            'data': [n.to_dict() for n in notifs],
            'no_leidas': no_leidas,
            'message': 'Notificaciones obtenidas.'
        }), 200
    except Exception as e:
        return jsonify({'error': 'Error al listar', 'message': str(e)}), 500

@notificaciones_bp.route('/<int:notif_id>/leida', methods=['PUT'])
@jwt_required()
@rechazar_en_autenticacion
def marcar_leida(notif_id):
    try:
        usuario_id = int(get_jwt_identity())
        notif = Notificacion.query.filter_by(id=notif_id, usuario_id=usuario_id).first()
        if not notif:
            return jsonify({'error': 'No encontrada', 'message': f'Notificación {notif_id} no existe'}), 404
        notif.leido = True
        db.session.commit()
        return jsonify({'data': notif.to_dict(), 'message': 'Marcada como leída'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error', 'message': str(e)}), 500

@notificaciones_bp.route('/leer-todas', methods=['PUT'])
@jwt_required()
@rechazar_en_autenticacion
def marcar_todas_leidas():
    try:
        usuario_id = int(get_jwt_identity())
        Notificacion.query.filter_by(usuario_id=usuario_id, leido=False).update({'leido': True})
        db.session.commit()
        return jsonify({'data': None, 'message': 'Todas marcadas como leídas'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error', 'message': str(e)}), 500

# --- Alertas de stock ---
@notificaciones_bp.route('/producto/<int:producto_id>/alerta', methods=['GET'])
@jwt_required()
@rechazar_en_autenticacion
def obtener_alerta(producto_id):
    try:
        usuario_id = int(get_jwt_identity())
        alerta = ProductoAlerta.query.filter_by(producto_id=producto_id, usuario_id=usuario_id).first()
        if not alerta:
            return jsonify({'data': {'activa': False}, 'message': 'Sin alerta'}), 200
        return jsonify({'data': alerta.to_dict(), 'message': 'Alerta obtenida'}), 200
    except Exception as e:
        return jsonify({'error': 'Error', 'message': str(e)}), 500

@notificaciones_bp.route('/producto/<int:producto_id>/alerta', methods=['POST'])
@jwt_required()
@rechazar_en_autenticacion
def crear_alerta(producto_id):
    try:
        usuario_id = int(get_jwt_identity())
        producto = db.session.get(Producto, producto_id)
        if not producto:
            return jsonify({'error': 'Producto no encontrado', 'message': f'No existe producto {producto_id}'}), 404
        # Solo para productos sin stock
        if producto.stock > 0:
            return jsonify({'error': 'Producto disponible', 'message': 'El producto ya tiene stock, no necesitas alerta'}), 400
        existente = ProductoAlerta.query.filter_by(producto_id=producto_id, usuario_id=usuario_id).first()
        if existente:
            existente.activa = True
            db.session.commit()
            return jsonify({'data': existente.to_dict(), 'message': 'Alerta reactivada'}), 200
        alerta = ProductoAlerta(producto_id=producto_id, usuario_id=usuario_id, activa=True)
        db.session.add(alerta)
        db.session.commit()
        return jsonify({'data': alerta.to_dict(), 'message': 'Alerta creada. Te avisaremos cuando haya stock.'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error', 'message': str(e)}), 500

@notificaciones_bp.route('/producto/<int:producto_id>/alerta', methods=['DELETE'])
@jwt_required()
@rechazar_en_autenticacion
def eliminar_alerta(producto_id):
    try:
        usuario_id = int(get_jwt_identity())
        alerta = ProductoAlerta.query.filter_by(producto_id=producto_id, usuario_id=usuario_id).first()
        if not alerta:
            return jsonify({'error': 'No encontrada', 'message': 'No tienes alerta para este producto'}), 404
        alerta.activa = False
        db.session.commit()
        return jsonify({'data': None, 'message': 'Alerta desactivada'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error', 'message': str(e)}), 500
