from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from models import db, Usuario

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/registro', methods=['POST'])
def registro():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos JSON requeridos.'}), 400

    nombre = data.get('nombre')
    email = data.get('email')
    password = data.get('password')
    telefono = data.get('telefono')
    direccion_envio = data.get('direccion_envio')

    if not nombre or not email or not password:
        return jsonify({'error': 'Campos obligatorios: nombre, email, password.'}), 400

    if Usuario.query.filter_by(email=email).first():
        return jsonify({'error': 'El email ya está registrado.'}), 400

    usuario = Usuario(
        nombre=nombre,
        email=email,
        telefono=telefono,
        direccion_envio=direccion_envio,
        rol='cliente'
    )
    usuario.set_password(password)

    db.session.add(usuario)
    db.session.commit()

    access_token = create_access_token(identity=str(usuario.id))
    refresh_token = create_refresh_token(identity=str(usuario.id))

    return jsonify({
        'mensaje': 'Usuario registrado exitosamente.',
        'usuario': usuario.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos JSON requeridos.'}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email y password son obligatorios.'}), 400

    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario or not usuario.check_password(password):
        return jsonify({'error': 'Credenciales inválidas.'}), 401

    access_token = create_access_token(identity=str(usuario.id))
    refresh_token = create_refresh_token(identity=str(usuario.id))

    return jsonify({
        'mensaje': 'Login exitoso.',
        'usuario': usuario.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200


@auth_bp.route('/perfil', methods=['GET'])
@jwt_required()
def perfil():
    usuario_id = get_jwt_identity()
    usuario = db.session.get(Usuario, usuario_id)

    if not usuario:
        return jsonify({'error': 'Usuario no encontrado.'}), 404

    return jsonify({'usuario': usuario.to_dict()}), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    usuario_id = get_jwt_identity()
    access_token = create_access_token(identity=usuario_id)
    return jsonify({'access_token': access_token}), 200