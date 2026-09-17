from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from utils.decorators import admin_required
from models import db, Resena, Producto, Pedido, DetallePedido, Usuario

resenas_bp = Blueprint('resenas', __name__, url_prefix='/api/resenas')

@resenas_bp.route('', methods=['GET'])
def listar_resenas():
    try:
        producto_id = request.args.get('producto', type=int)
        # Si se pide por producto, es público (para detalle de producto)
        if producto_id:
            resenas = Resena.query.filter_by(producto_id=producto_id).order_by(Resena.fecha.desc()).all()
            # Calcular promedio
            promedio = None
            total = len(resenas)
            if total > 0:
                promedio = round(sum(r.calificacion for r in resenas) / total, 1)
            return jsonify({
                'data': [r.to_dict() for r in resenas],
                'promedio': promedio,
                'total': total,
                'message': 'Reseñas obtenidas exitosamente.'
            }), 200
        # Sin producto, requiere admin (lista completa)
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request()
        from utils.decorators import admin_required
        # Verificar rol manualmente
        usuario_id = get_jwt_identity()
        usuario = db.session.get(Usuario, int(usuario_id))
        if not usuario or usuario.rol != 'admin':
            return jsonify({'error': 'Acceso denegado', 'message': 'Se requiere rol de administrador'}), 403
        resenas = Resena.query.order_by(Resena.fecha.desc()).all()
        return jsonify({
            'data': [r.to_dict() for r in resenas],
            'message': 'Reseñas obtenidas exitosamente.'
        }), 200
    except Exception as e:
        # Si es error de JWT y había producto_id, ya se manejó arriba; si no, intentar mensaje claro
        if 'producto' in request.args:
            return jsonify({'error': 'Error al listar reseñas', 'message': str(e)}), 500
        return jsonify({'error': 'Error al listar reseñas', 'message': str(e)}), 500

@resenas_bp.route('', methods=['POST'])
@jwt_required()
def crear_resena():
    try:
        usuario_id = int(get_jwt_identity())
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos JSON requeridos', 'message': 'El cuerpo debe ser JSON'}), 400
        producto_id = data.get('producto_id')
        calificacion = data.get('calificacion')
        comentario = data.get('comentario', '')
        if not producto_id:
            return jsonify({'error': 'Producto requerido', 'message': 'El campo producto_id es obligatorio'}), 400
        try:
            calificacion = int(calificacion)
        except (ValueError, TypeError):
            return jsonify({'error': 'Calificación inválida', 'message': 'La calificación debe ser un número entero'}), 400
        if calificacion < 1 or calificacion > 5:
            return jsonify({'error': 'Calificación fuera de rango', 'message': 'La calificación debe ser entre 1 y 5 estrellas'}), 400
        producto = db.session.get(Producto, producto_id)
        if not producto:
            return jsonify({'error': 'Producto no encontrado', 'message': f'No existe producto con id {producto_id}'}), 404
        # Verificar que el usuario haya comprado este producto
        pedido_con_producto = Pedido.query.join(DetallePedido).filter(
            Pedido.usuario_id == usuario_id,
            DetallePedido.producto_id == producto_id
        ).first()
        if not pedido_con_producto:
            return jsonify({'error': 'No autorizado', 'message': 'Solo puedes reseñar productos que hayas comprado'}), 403
        # Verificar si ya existe reseña del usuario para este producto
        existente = Resena.query.filter_by(usuario_id=usuario_id, producto_id=producto_id).first()
        if existente:
            return jsonify({'error': 'Reseña duplicada', 'message': 'Ya has reseñado este producto'}), 400
        resena = Resena(
            usuario_id=usuario_id,
            producto_id=producto_id,
            calificacion=calificacion,
            comentario=comentario if comentario else None
        )
        db.session.add(resena)
        db.session.commit()
        return jsonify({'data': resena.to_dict(), 'message': 'Reseña creada exitosamente.'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al crear reseña', 'message': str(e)}), 500

@resenas_bp.route('/<int:resena_id>', methods=['PUT'])
@jwt_required()
@admin_required
def actualizar_resena(resena_id):
    try:
        resena = db.session.get(Resena, resena_id)
        if not resena:
            return jsonify({'error': 'Reseña no encontrada', 'message': f'No existe reseña con id {resena_id}'}), 404
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos JSON requeridos', 'message': 'El cuerpo debe ser JSON'}), 400
        if 'calificacion' in data:
            try:
                calificacion = int(data['calificacion'])
                if calificacion < 1 or calificacion > 5:
                    return jsonify({'error': 'Calificación fuera de rango', 'message': 'Debe ser entre 1 y 5'}), 400
                resena.calificacion = calificacion
            except (ValueError, TypeError):
                return jsonify({'error': 'Calificación inválida', 'message': 'Debe ser un entero'}), 400
        if 'comentario' in data:
            resena.comentario = data['comentario'] if data['comentario'] else None
        db.session.commit()
        return jsonify({'data': resena.to_dict(), 'message': 'Reseña actualizada exitosamente.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al actualizar reseña', 'message': str(e)}), 500

@resenas_bp.route('/<int:resena_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def eliminar_resena(resena_id):
    try:
        resena = db.session.get(Resena, resena_id)
        if not resena:
            return jsonify({'error': 'Reseña no encontrada', 'message': f'No existe reseña con id {resena_id}'}), 404
        db.session.delete(resena)
        db.session.commit()
        return jsonify({'data': None, 'message': 'Reseña eliminada exitosamente.'}), 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar reseña', 'message': str(e)}), 500
