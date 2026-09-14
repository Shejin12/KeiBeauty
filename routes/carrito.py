from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Carrito, DetalleCarrito, Producto

carrito_bp = Blueprint('carrito', __name__, url_prefix='/api/carrito')


def _get_or_create_carrito(usuario_id):
    carrito = Carrito.query.filter_by(usuario_id=usuario_id).first()
    if not carrito:
        carrito = Carrito(usuario_id=usuario_id)
        db.session.add(carrito)
        db.session.commit()
    return carrito


@carrito_bp.route('', methods=['GET'])
@jwt_required()
def get_carrito():
    try:
        usuario_id = int(get_jwt_identity())
        carrito = _get_or_create_carrito(usuario_id)
        return jsonify({
            'data': carrito.to_dict(),
            'message': 'Carrito obtenido exitosamente.'
        }), 200
    except Exception as e:
        return jsonify({'error': 'Error al obtener carrito', 'message': str(e)}), 500


@carrito_bp.route('/items', methods=['POST'])
@jwt_required()
def add_item():
    try:
        usuario_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos JSON requeridos', 'message': 'El cuerpo de la petición debe ser JSON válido'}), 400
        
        producto_id = data.get('producto_id')
        cantidad = data.get('cantidad', 1)
        
        if not producto_id:
            return jsonify({'error': 'Campo obligatorio', 'message': 'producto_id es requerido'}), 400
        
        try:
            cantidad = int(cantidad)
        except (ValueError, TypeError):
            return jsonify({'error': 'Cantidad inválida', 'message': 'La cantidad debe ser un número entero'}), 400
        
        if cantidad < 1:
            return jsonify({'error': 'Cantidad inválida', 'message': 'La cantidad debe ser al menos 1'}), 400
        
        producto = db.session.get(Producto, producto_id)
        if not producto:
            return jsonify({'error': 'Producto no encontrado', 'message': f'No existe producto con id {producto_id}'}), 404
        
        if producto.estado != 'activo':
            return jsonify({'error': 'Producto no disponible', 'message': 'El producto no está disponible para compra'}), 400
        
        if cantidad > producto.stock:
            return jsonify({'error': 'Stock insuficiente', 'message': f'Solo hay {producto.stock} unidades disponibles'}), 400
        
        carrito = _get_or_create_carrito(usuario_id)
        
        # Verificar si el item ya existe en el carrito
        detalle_existente = DetalleCarrito.query.filter_by(
            carrito_id=carrito.id, 
            producto_id=producto_id
        ).first()
        
        if detalle_existente:
            nueva_cantidad = detalle_existente.cantidad + cantidad
            if nueva_cantidad > producto.stock:
                return jsonify({'error': 'Stock insuficiente', 'message': f'Solo hay {producto.stock} unidades disponibles'}), 400
            detalle_existente.cantidad = nueva_cantidad
        else:
            detalle = DetalleCarrito(
                carrito_id=carrito.id,
                producto_id=producto_id,
                cantidad=cantidad
            )
            db.session.add(detalle)
        
        carrito.fecha_actualizacion = db.func.now()
        db.session.commit()
        
        # Recargar carrito actualizado
        carrito = _get_or_create_carrito(usuario_id)
        
        return jsonify({
            'data': carrito.to_dict(),
            'message': 'Producto añadido al carrito.'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al añadir al carrito', 'message': str(e)}), 500


@carrito_bp.route('/items/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_item(item_id):
    try:
        usuario_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos JSON requeridos', 'message': 'El cuerpo de la petición debe ser JSON válido'}), 400
        
        cantidad = data.get('cantidad')
        if cantidad is None:
            return jsonify({'error': 'Campo obligatorio', 'message': 'cantidad es requerido'}), 400
        
        try:
            cantidad = int(cantidad)
        except (ValueError, TypeError):
            return jsonify({'error': 'Cantidad inválida', 'message': 'La cantidad debe ser un número entero'}), 400
        
        if cantidad < 1:
            return jsonify({'error': 'Cantidad inválida', 'message': 'La cantidad debe ser al menos 1'}), 400
        
        carrito = Carrito.query.filter_by(usuario_id=usuario_id).first()
        if not carrito:
            return jsonify({'error': 'Carrito no encontrado', 'message': 'No existe carrito para este usuario'}), 404
        
        detalle = DetalleCarrito.query.filter_by(id=item_id, carrito_id=carrito.id).first()
        if not detalle:
            return jsonify({'error': 'Item no encontrado', 'message': 'El item no pertenece a tu carrito'}), 404
        
        if cantidad > detalle.producto.stock:
            return jsonify({'error': 'Stock insuficiente', 'message': f'Solo hay {detalle.producto.stock} unidades disponibles'}), 400
        
        detalle.cantidad = cantidad
        carrito.fecha_actualizacion = db.func.now()
        db.session.commit()
        
        carrito = Carrito.query.filter_by(usuario_id=usuario_id).first()
        
        return jsonify({
            'data': carrito.to_dict(),
            'message': 'Carrito actualizado exitosamente.'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al actualizar carrito', 'message': str(e)}), 500


@carrito_bp.route('/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_item(item_id):
    try:
        usuario_id = int(get_jwt_identity())
        
        carrito = Carrito.query.filter_by(usuario_id=usuario_id).first()
        if not carrito:
            return jsonify({'error': 'Carrito no encontrado', 'message': 'No existe carrito para este usuario'}), 404
        
        detalle = DetalleCarrito.query.filter_by(id=item_id, carrito_id=carrito.id).first()
        if not detalle:
            return jsonify({'error': 'Item no encontrado', 'message': 'El item no pertenece a tu carrito'}), 404
        
        db.session.delete(detalle)
        carrito.fecha_actualizacion = db.func.now()
        db.session.commit()
        
        carrito = Carrito.query.filter_by(usuario_id=usuario_id).first()
        
        return jsonify({
            'data': carrito.to_dict(),
            'message': 'Item eliminado del carrito.'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar item', 'message': str(e)}), 500


@carrito_bp.route('', methods=['DELETE'])
@jwt_required()
def clear_carrito():
    try:
        usuario_id = int(get_jwt_identity())
        
        carrito = Carrito.query.filter_by(usuario_id=usuario_id).first()
        if not carrito:
            return jsonify({'data': None, 'message': 'Carrito ya está vacío.'}), 200
        
        DetalleCarrito.query.filter_by(carrito_id=carrito.id).delete()
        carrito.fecha_actualizacion = db.func.now()
        db.session.commit()
        
        return jsonify({
            'data': carrito.to_dict(),
            'message': 'Carrito vaciado exitosamente.'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al vaciar carrito', 'message': str(e)}), 500