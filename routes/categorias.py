from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils.decorators import admin_required
from models import db, Categoria, Producto, CatalogoEstadoProducto

categorias_bp = Blueprint('categorias', __name__, url_prefix='/api/categorias')


@categorias_bp.route('', methods=['GET'])
def listar_categorias():
    try:
        categorias = Categoria.query.order_by(Categoria.nombre.asc()).all()
        data = [c.to_dict() for c in categorias]
        return jsonify({
            'data': data,
            'message': 'Categorías obtenidas exitosamente.'
        }), 200
    except Exception as e:
        return jsonify({'error': 'Error al listar categorías', 'message': str(e)}), 500


@categorias_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def crear_categoria():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos JSON requeridos', 'message': 'El cuerpo debe ser JSON válido'}), 400

        nombre = data.get('nombre', '').strip()
        if not nombre:
            return jsonify({'error': 'Nombre obligatorio', 'message': 'El campo nombre es obligatorio'}), 400

        if len(nombre) > 100:
            return jsonify({'error': 'Nombre muy largo', 'message': 'El nombre no debe exceder 100 caracteres'}), 400

        if Categoria.query.filter_by(nombre=nombre).first():
            return jsonify({'error': 'Categoría duplicada', 'message': f'Ya existe una categoría con el nombre "{nombre}"'}), 400

        categoria = Categoria(
            nombre=nombre,
            descripcion=data.get('descripcion', '')
        )
        db.session.add(categoria)
        db.session.commit()

        return jsonify({
            'data': categoria.to_dict(),
            'message': 'Categoría creada exitosamente.'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al crear categoría', 'message': str(e)}), 500


@categorias_bp.route('/<int:categoria_id>', methods=['PUT'])
@jwt_required()
@admin_required
def editar_categoria(categoria_id):
    try:
        categoria = db.session.get(Categoria, categoria_id)
        if not categoria:
            return jsonify({'error': 'Categoría no encontrada', 'message': f'No existe categoría con id {categoria_id}'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos JSON requeridos', 'message': 'El cuerpo debe ser JSON válido'}), 400

        if 'nombre' in data:
            nombre = str(data['nombre']).strip()
            if not nombre:
                return jsonify({'error': 'Nombre obligatorio', 'message': 'El campo nombre es obligatorio'}), 400
            if len(nombre) > 100:
                return jsonify({'error': 'Nombre muy largo', 'message': 'El nombre no debe exceder 100 caracteres'}), 400
            existente = Categoria.query.filter(Categoria.nombre == nombre, Categoria.id != categoria.id).first()
            if existente:
                return jsonify({'error': 'Categoría duplicada', 'message': f'Ya existe otra categoría con el nombre "{nombre}"'}), 400
            categoria.nombre = nombre

        if 'descripcion' in data:
            categoria.descripcion = data['descripcion']

        db.session.commit()

        return jsonify({
            'data': categoria.to_dict(),
            'message': 'Categoría actualizada exitosamente.'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al actualizar categoría', 'message': str(e)}), 500


@categorias_bp.route('/<int:categoria_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def eliminar_categoria(categoria_id):
    try:
        categoria = db.session.get(Categoria, categoria_id)
        if not categoria:
            return jsonify({'error': 'Categoría no encontrada', 'message': f'No existe categoría con id {categoria_id}'}), 404

        estado_activo = CatalogoEstadoProducto.por_nombre('activo')
        estado_activo_id = estado_activo.id if estado_activo else None
        productos_asociados = Producto.query.filter_by(categoria_id=categoria_id, estado_id=estado_activo_id).count()
        if productos_asociados > 0:
            return jsonify({
                'error': 'Categoría con productos asociados',
                'message': f'No se puede eliminar la categoría porque tiene {productos_asociados} producto(s) activo(s) asociado(s).'
            }), 400

        db.session.delete(categoria)
        db.session.commit()

        return jsonify({
            'data': None,
            'message': 'Categoría eliminada exitosamente.'
        }), 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar categoría', 'message': str(e)}), 500
