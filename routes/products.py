from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from utils.decorators import admin_required
from models import db, Producto, Marca, Categoria, ProductoFavorito

products_bp = Blueprint('products', __name__, url_prefix='/api/products')


@products_bp.route('', methods=['GET'])
def get_products():
    try:
        categoria = request.args.get('categoria', type=int)
        marca = request.args.get('marca', type=int)
        buscar = request.args.get('buscar', type=str)
        con_favorito = request.args.get('con_favorito', type=int)

        query = Producto.query.filter_by(estado='activo')

        if categoria:
            query = query.filter_by(categoria_id=categoria)
        if marca:
            query = query.filter_by(marca_id=marca)
        if buscar:
            query = query.filter(Producto.nombre.ilike(f'%{buscar}%'))

        productos = query.order_by(Producto.fecha_creacion.desc()).all()
        
        # Si se solicita con_favorito y hay usuario autenticado
        favoritos_set = set()
        if con_favorito == 1:
            try:
                verify_jwt_in_request(optional=True)
                from flask_jwt_extended import get_jwt
                claims = get_jwt()
                if claims and claims.get('estado') != 'en_autenticacion':
                    usuario_id = get_jwt_identity()
                    if usuario_id:
                        favoritos = ProductoFavorito.query.filter_by(usuario_id=int(usuario_id)).all()
                        favoritos_set = {f.producto_id for f in favoritos}
            except:
                pass
        
        data = []
        for p in productos:
            producto_dict = p.to_dict()
            if con_favorito == 1:
                producto_dict['es_favorito'] = p.id in favoritos_set
            data.append(producto_dict)

        return jsonify({
            'data': data,
            'message': 'Productos obtenidos exitosamente.'
        }), 200
    except Exception as e:
        return jsonify({'error': 'Error al obtener productos', 'message': str(e)}), 500


@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        producto = db.session.get(Producto, product_id)

        if not producto or producto.estado != 'activo':
            return jsonify({'error': 'Producto no encontrado', 'message': f'No existe producto con id {product_id}'}), 404

        return jsonify({
            'data': producto.to_dict(),
            'message': 'Producto obtenido exitosamente.'
        }), 200
    except Exception as e:
        return jsonify({'error': 'Error al obtener producto', 'message': str(e)}), 500


@products_bp.route('/categorias', methods=['GET', 'OPTIONS'])
def get_categorias():
    try:
        categorias = Categoria.query.all()
        data = [{'id': c.id, 'nombre': c.nombre} for c in categorias]
        return jsonify({
            'data': data,
            'message': 'Categorías obtenidas exitosamente.'
        }), 200
    except Exception as e:
        return jsonify({'error': 'Error al obtener categorías', 'message': str(e)}), 500


@products_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_product():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos JSON requeridos', 'message': 'El cuerpo de la petición debe ser JSON válido'}), 400

        required_fields = ['nombre', 'precio', 'stock', 'marca_id', 'categoria_id']
        missing = [f for f in required_fields if f not in data or data[f] is None]
        if missing:
            return jsonify({'error': 'Campos obligatorios faltantes', 'message': f'Faltan: {", ".join(missing)}'}), 400

        try:
            precio = float(data['precio'])
            stock = int(data['stock'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Tipos inválidos', 'message': 'precio debe ser número, stock debe ser entero'}), 400

        if precio <= 0:
            return jsonify({'error': 'Precio inválido', 'message': 'El precio debe ser mayor a 0'}), 400
        if stock < 0:
            return jsonify({'error': 'Stock inválido', 'message': 'El stock no puede ser negativo'}), 400

        marca = db.session.get(Marca, data['marca_id'])
        if not marca:
            return jsonify({'error': 'Marca no encontrada', 'message': f'No existe marca con id {data["marca_id"]}'}), 404

        categoria = db.session.get(Categoria, data['categoria_id'])
        if not categoria:
            return jsonify({'error': 'Categoría no encontrada', 'message': f'No existe categoría con id {data["categoria_id"]}'}), 404

        producto = Producto(
            nombre=data['nombre'],
            descripcion=data.get('descripcion', ''),
            ingredientes_clave=data.get('ingredientes_clave', ''),
            tipo_piel=data.get('tipo_piel', ''),
            precio=precio,
            stock=stock,
            imagen_url=data.get('imagen_url', ''),
            estado=data.get('estado', 'activo'),
            marca_id=data['marca_id'],
            categoria_id=data['categoria_id']
        )

        db.session.add(producto)
        db.session.commit()

        return jsonify({
            'data': producto.to_dict(),
            'message': 'Producto creado exitosamente.'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al crear producto', 'message': str(e)}), 500


@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_product(product_id):
    try:
        producto = db.session.get(Producto, product_id)

        if not producto:
            return jsonify({'error': 'Producto no encontrado', 'message': f'No existe producto con id {product_id}'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos JSON requeridos', 'message': 'El cuerpo de la petición debe ser JSON válido'}), 400

        if 'nombre' in data and data['nombre']:
            producto.nombre = data['nombre']
        if 'descripcion' in data:
            producto.descripcion = data['descripcion']
        if 'ingredientes_clave' in data:
            producto.ingredientes_clave = data['ingredientes_clave']
        if 'tipo_piel' in data:
            producto.tipo_piel = data['tipo_piel']
        if 'precio' in data:
            try:
                precio = float(data['precio'])
                if precio <= 0:
                    return jsonify({'error': 'Precio inválido', 'message': 'El precio debe ser mayor a 0'}), 400
                producto.precio = precio
            except (ValueError, TypeError):
                return jsonify({'error': 'Precio inválido', 'message': 'El precio debe ser un número válido'}), 400
        if 'stock' in data:
            try:
                stock = int(data['stock'])
                if stock < 0:
                    return jsonify({'error': 'Stock inválido', 'message': 'El stock no puede ser negativo'}), 400
                producto.stock = stock
            except (ValueError, TypeError):
                return jsonify({'error': 'Stock inválido', 'message': 'El stock debe ser un entero válido'}), 400
        if 'imagen_url' in data:
            producto.imagen_url = data['imagen_url']
        if 'estado' in data:
            if data['estado'] not in ['activo', 'inactivo', 'agotado']:
                return jsonify({'error': 'Estado inválido', 'message': 'Estado debe ser: activo, inactivo o agotado'}), 400
            producto.estado = data['estado']
        if 'marca_id' in data:
            marca = db.session.get(Marca, data['marca_id'])
            if not marca:
                return jsonify({'error': 'Marca no encontrada', 'message': f'No existe marca con id {data["marca_id"]}'}), 404
            producto.marca_id = data['marca_id']
        if 'categoria_id' in data:
            categoria = db.session.get(Categoria, data['categoria_id'])
            if not categoria:
                return jsonify({'error': 'Categoría no encontrada', 'message': f'No existe categoría con id {data["categoria_id"]}'}), 404
            producto.categoria_id = data['categoria_id']

        db.session.commit()

        return jsonify({
            'data': producto.to_dict(),
            'message': 'Producto actualizado exitosamente.'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al actualizar producto', 'message': str(e)}), 500


@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_product(product_id):
    try:
        producto = db.session.get(Producto, product_id)

        if not producto:
            return jsonify({'error': 'Producto no encontrado', 'message': f'No existe producto con id {product_id}'}), 404

        db.session.delete(producto)
        db.session.commit()

        return jsonify({
            'data': None,
            'message': 'Producto eliminado exitosamente.'
        }), 204

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar producto', 'message': str(e)}), 500


@products_bp.route('/admin-test', methods=['GET'])
@jwt_required()
@admin_required
def admin_test():
    return jsonify({'data': None, 'message': 'Acceso de administrador concedido.'}), 200