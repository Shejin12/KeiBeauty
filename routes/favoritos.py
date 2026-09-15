from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Producto, ProductoFavorito
from utils.decorators import rechazar_en_autenticacion

favoritos_bp = Blueprint('favoritos', __name__, url_prefix='/api/favoritos')


@favoritos_bp.route('', methods=['GET'])
@jwt_required()
@rechazar_en_autenticacion
def get_favoritos():
    """Lista de favoritos del usuario autenticado."""
    try:
        usuario_id = int(get_jwt_identity())
        
        favoritos = ProductoFavorito.obtener_favoritos(usuario_id)
        
        data = [f.to_dict() for f in favoritos]
        
        return jsonify({
            'data': data,
            'message': 'Favoritos obtenidos exitosamente.'
        }), 200
    except Exception as e:
        return jsonify({'error': 'Error al obtener favoritos', 'message': str(e)}), 500


@favoritos_bp.route('/<int:producto_id>', methods=['POST'])
@jwt_required()
@rechazar_en_autenticacion
def agregar_favorito(producto_id):
    """Agrega un producto a favoritos (idempotente)."""
    try:
        usuario_id = int(get_jwt_identity())
        
        # Verificar que el producto existe
        producto = db.session.get(Producto, producto_id)
        if not producto:
            return jsonify({'error': 'Producto no encontrado', 'message': f'No existe producto con id {producto_id}'}), 404
        
        favorito, creado = ProductoFavorito.agregar(usuario_id, producto_id)
        
        return jsonify({
            'data': favorito.to_dict(),
            'message': 'Producto añadido a favoritos'
        }), 200
    except Exception as e:
        return jsonify({'error': 'Error al agregar a favoritos', 'message': str(e)}), 500


@favoritos_bp.route('/<int:producto_id>', methods=['DELETE'])
@jwt_required()
@rechazar_en_autenticacion
def quitar_favorito(producto_id):
    """Quita un producto de favoritos."""
    try:
        usuario_id = int(get_jwt_identity())
        
        resultado = ProductoFavorito.quitar(usuario_id, producto_id)
        
        if not resultado:
            return jsonify({'error': 'No encontrado', 'message': 'El producto no está en favoritos'}), 404
        
        return jsonify({
            'data': None,
            'message': 'Producto quitado de favoritos'
        }), 204
    except Exception as e:
        return jsonify({'error': 'Error al quitar de favoritos', 'message': str(e)}), 500