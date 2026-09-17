import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils.decorators import admin_required
from models import db, Marca

try:
    from imagekitio import ImageKit
    IMAGEKIT_AVAILABLE = True
except ImportError:
    IMAGEKIT_AVAILABLE = False

imagekit_client = None
if IMAGEKIT_AVAILABLE:
    imagekit_client = ImageKit(
        private_key=os.environ.get('IMAGEKIT_PRIVATE_KEY')
    )

marcas_bp = Blueprint('marcas', __name__, url_prefix='/api/marcas')

@marcas_bp.route('', methods=['GET'])
def listar_marcas():
    try:
        marcas = Marca.query.all()
        return jsonify({
            'data': [m.to_dict() for m in marcas],
            'message': 'Marcas obtenidas exitosamente.'
        }), 200
    except Exception as e:
        return jsonify({'error': 'Error al listar marcas', 'message': str(e)}), 500

@marcas_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def crear_marca():
    try:
        archivo = request.files.get('archivo')
        # Leer datos: puede ser JSON o form-data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        if not data:
            return jsonify({'error': 'Datos requeridos', 'message': 'El cuerpo debe contener los campos de la marca'}), 400
        nombre = data.get('nombre', '').strip()
        if not nombre:
            return jsonify({'error': 'Nombre obligatorio', 'message': 'El nombre de la marca es obligatorio'}), 400
        if Marca.query.filter_by(nombre=nombre).first():
            return jsonify({'error': 'Marca duplicada', 'message': 'Ya existe una marca con ese nombre'}), 400
        archivo = request.files.get('archivo')
        logo_url = data.get('logo_url', '')
        if archivo and archivo.filename:
            tipos_permitidos = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/jpg']
            if archivo.content_type not in tipos_permitidos:
                return jsonify({'error': 'Tipo de archivo no soportado', 'message': f'Tipos permitidos: {", ".join(tipos_permitidos)}'}), 400
            if not IMAGEKIT_AVAILABLE or imagekit_client is None:
                return jsonify({'error': 'ImageKit no disponible', 'message': 'El SDK de ImageKit no está instalado o las credenciales no son válidas.'}), 500
            archivo_bytes = archivo.read()
            upload_response = imagekit_client.files.upload(
                file=archivo_bytes,
                file_name=f"marca_{nombre}_{archivo.filename}",
                folder="/marcas"
            )
            logo_url = upload_response.url
        marca = Marca(
            nombre=nombre,
            descripcion=data.get('descripcion', ''),
            logo_url=logo_url
        )
        db.session.add(marca)
        db.session.commit()
        return jsonify({'data': marca.to_dict(), 'message': 'Marca creada exitosamente.'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al crear marca', 'message': str(e)}), 500

@marcas_bp.route('/<int:marca_id>', methods=['PUT'])
@jwt_required()
@admin_required
def actualizar_marca(marca_id):
    try:
        marca = db.session.get(Marca, marca_id)
        if not marca:
            return jsonify({'error': 'Marca no encontrada', 'message': f'No existe marca con id {marca_id}'}), 404
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos JSON requeridos', 'message': 'El cuerpo debe ser JSON'}), 400
        if 'nombre' in data and data['nombre']:
            nombre = data['nombre'].strip()
            if nombre and Marca.query.filter(Marca.id != marca_id, Marca.nombre == nombre).first():
                return jsonify({'error': 'Marca duplicada', 'message': 'Ya existe otra marca con ese nombre'}), 400
            marca.nombre = nombre
        if 'descripcion' in data:
            marca.descripcion = data['descripcion']
        archivo = request.files.get('archivo')
        if archivo and archivo.filename:
            tipos_permitidos = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/jpg']
            if archivo.content_type not in tipos_permitidos:
                return jsonify({'error': 'Tipo de archivo no soportado', 'message': f'Tipos permitidos: {", ".join(tipos_permitidos)}'}), 400
            if not IMAGEKIT_AVAILABLE or imagekit_client is None:
                return jsonify({'error': 'ImageKit no disponible', 'message': 'El SDK de ImageKit no está instalado.'}), 500
            archivo_bytes = archivo.read()
            upload_response = imagekit_client.files.upload(
                file=archivo_bytes,
                file_name=f"marca_{marca_id}_{archivo.filename}",
                folder="/marcas"
            )
            marca.logo_url = upload_response.url
        elif 'logo_url' in data:
            marca.logo_url = data['logo_url']
        db.session.commit()
        return jsonify({'data': marca.to_dict(), 'message': 'Marca actualizada exitosamente.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al actualizar marca', 'message': str(e)}), 500

@marcas_bp.route('/<int:marca_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def eliminar_marca(marca_id):
    try:
        marca = db.session.get(Marca, marca_id)
        if not marca:
            return jsonify({'error': 'Marca no encontrada', 'message': f'No existe marca con id {marca_id}'}), 404
        db.session.delete(marca)
        db.session.commit()
        return jsonify({'data': None, 'message': 'Marca eliminada exitosamente.'}), 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar marca', 'message': str(e)}), 500
