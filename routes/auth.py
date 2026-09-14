from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from models import db, Usuario, RecuperacionContrasena
from utils.email import email_service

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


@auth_bp.route('/olvide-contrasena', methods=['POST'])
def olvide_contrasena():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos JSON requeridos.'}), 400

    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email es requerido.'}), 400

    usuario = Usuario.query.filter_by(email=email).first()

    # Siempre respondemos éxito por seguridad (no revelar si email existe)
    if usuario:
        try:
            token, recuperacion = RecuperacionContrasena.crear_solicitud(usuario.id)
            
            frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
            email_service.enviar_recuperacion_contrasena(
                to_email=usuario.email,
                nombre=usuario.nombre,
                token=token,
                frontend_url=frontend_url
            )
        except Exception as e:
            current_app.logger.error(f'Error enviando email recuperacion: {e}')
            # No fallamos la request por seguridad

    return jsonify({
        'data': None,
        'message': 'Si el email existe, recibirás instrucciones para restablecer tu contraseña.'
    }), 200


@auth_bp.route('/reestablecer-contrasena', methods=['POST'])
def reestablecer_contrasena():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos JSON requeridos.'}), 400

    token = data.get('token')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if not token or not password:
        return jsonify({'error': 'Token y nueva contraseña son requeridos.'}), 400

    if password != confirm_password:
        return jsonify({'error': 'Las contraseñas no coinciden.'}), 400

    if len(password) < 6:
        return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres.'}), 400

    recuperacion, error = RecuperacionContrasena.validar_token(token)
    if error:
        return jsonify({'error': error}), 400

    usuario = db.session.get(Usuario, recuperacion.usuario_id)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado.'}), 404

    usuario.set_password(password)
    recuperacion.marcar_como_usado()
    db.session.commit()

    return jsonify({
        'data': None,
        'message': 'Contraseña restablecida exitosamente. Ya puedes iniciar sesión.'
    }), 200