from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from models import db, Usuario, RecuperacionContrasena, Codigo2FA
from utils.email import email_service
from utils.decorators import solo_en_autenticacion, rechazar_en_autenticacion
from datetime import timedelta

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

    if not nombre or not email or not password or not direccion_envio:
        return jsonify({'error': 'Campos obligatorios: nombre, email, password, direccion_envio.'}), 400

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

    # Verificar si tiene 2FA activado
    if usuario.two_factor_enabled:
        # Generar código 2FA
        try:
            ip = request.remote_addr
            codigo, codigo_2fa = Codigo2FA.crear_codigo(usuario.id, ip=ip)
            
            frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
            email_service.enviar_codigo_2fa(
                to_email=usuario.email,
                codigo=codigo,
                minutos_validez=5
            )
        except Exception as e:
            current_app.logger.error(f'Error enviando código 2FA: {e}')
            # No fallamos el login por error de email

        # Generar JWT temporal con estado "en_autenticacion" (expira en 10 min)
        token_temporal = create_access_token(
            identity=str(usuario.id),
            additional_claims={'estado': 'en_autenticacion', 'email': usuario.email},
            expires_delta=timedelta(minutes=10)
        )

        return jsonify({
            'data': {
                'requiere_2fa': True,
                'email': usuario.email,
                'token_temporal': token_temporal
            },
            'message': 'Código enviado a tu correo'
        }), 200

    # Sin 2FA, login normal
    access_token = create_access_token(identity=str(usuario.id))
    refresh_token = create_refresh_token(identity=str(usuario.id))

    return jsonify({
        'mensaje': 'Login exitoso.',
        'usuario': usuario.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200


@auth_bp.route('/verificar-2fa', methods=['POST'])
@solo_en_autenticacion
def verificar_2fa():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos JSON requeridos.'}), 400

    codigo = data.get('codigo')

    if not codigo:
        return jsonify({'error': 'Código es obligatorio.'}), 400

    # Obtener usuario_id desde el JWT temporal
    claims = get_jwt()
    usuario_id = claims.get('sub')
    email = claims.get('email')

    if not usuario_id:
        return jsonify({'error': 'Token inválido.'}), 400

    usuario = db.session.get(Usuario, int(usuario_id))

    if not usuario:
        return jsonify({'error': 'Usuario no encontrado.'}), 404

    if not usuario.two_factor_enabled:
        return jsonify({'error': '2FA no está activado para este usuario.'}), 400

    codigo_2fa, error = Codigo2FA.validar_codigo(int(usuario_id), codigo)
    if error:
        return jsonify({'error': error}), 400

    # Código válido, marcar como usado
    codigo_2fa.marcar_como_usado()

    # Generar tokens reales
    access_token = create_access_token(identity=str(usuario.id))
    refresh_token = create_refresh_token(identity=str(usuario.id))

    return jsonify({
        'mensaje': 'Login exitoso.',
        'usuario': usuario.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200


@auth_bp.route('/reenviar-codigo-2fa', methods=['POST'])
@solo_en_autenticacion
def reenviar_codigo_2fa():
    # Obtener usuario_id desde el JWT temporal
    claims = get_jwt()
    usuario_id = claims.get('sub')

    if not usuario_id:
        return jsonify({'error': 'Token inválido.'}), 400

    usuario = db.session.get(Usuario, int(usuario_id))

    if not usuario or not usuario.two_factor_enabled:
        # Siempre respondemos éxito por seguridad
        return jsonify({
            'data': None,
            'message': 'Código reenviado'
        }), 200

    # Verificar rate limit: último código enviado hace menos de 60s
    from models import Codigo2FA
    from datetime import datetime, timedelta
    from sqlalchemy import desc
    
    ultimo_codigo = Codigo2FA.query.filter_by(usuario_id=usuario.id).order_by(desc(Codigo2FA.fecha_solicitud)).first()
    
    if ultimo_codigo and (datetime.utcnow() - ultimo_codigo.fecha_solicitud) < timedelta(seconds=60):
        return jsonify({'error': 'Debes esperar 60 segundos antes de reenviar el código.'}), 429
    
    try:
        ip = request.remote_addr
        codigo, codigo_2fa = Codigo2FA.crear_codigo(usuario.id, ip=request.remote_addr)
        
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
        email_service.enviar_codigo_2fa(
            to_email=usuario.email,
            codigo=codigo,
            minutos_validez=5
        )
    except Exception as e:
        current_app.logger.error(f'Error reenviando código 2FA: {e}')

    return jsonify({
        'data': None,
        'message': 'Código reenviado'
    }), 200


@auth_bp.route('/activar-2fa', methods=['POST'])
@jwt_required()
@rechazar_en_autenticacion
def activar_2fa():
    usuario_id = int(get_jwt_identity())
    usuario = db.session.get(Usuario, usuario_id)
    
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado.'}), 404
    
    usuario.two_factor_enabled = True
    db.session.commit()
    
    return jsonify({
        'data': {'two_factor_enabled': True},
        'message': '2FA activado exitosamente'
    }), 200


@auth_bp.route('/cancelar-login', methods=['POST'])
@solo_en_autenticacion
def cancelar_login():
    claims = get_jwt()
    usuario_id = claims.get('sub')
    if usuario_id:
        from models import Codigo2FA
        Codigo2FA.query.filter_by(usuario_id=int(usuario_id), usado=False).update({'usado': True})
        db.session.commit()
    return jsonify({'message': 'Login cancelado. El código pendiente ha sido invalidado.'}), 200


@auth_bp.route('/desactivar-2fa', methods=['POST'])
@jwt_required()
@rechazar_en_autenticacion
def desactivar_2fa():
    usuario_id = int(get_jwt_identity())
    usuario = db.session.get(Usuario, usuario_id)
    
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado.'}), 404
    
    usuario.two_factor_enabled = False
    
    # Marcar todos los códigos activos como usados
    from models import Codigo2FA
    Codigo2FA.query.filter_by(usuario_id=usuario.id, usado=False).update({'usado': True})
    
    db.session.commit()
    
    return jsonify({
        'data': {'two_factor_enabled': False},
        'message': '2FA desactivado exitosamente'
    }), 200


@auth_bp.route('/perfil', methods=['GET'])
@jwt_required()
@rechazar_en_autenticacion
def perfil():
    usuario_id = get_jwt_identity()
    usuario = db.session.get(Usuario, usuario_id)

    if not usuario:
        return jsonify({'error': 'Usuario no encontrado.'}), 404

    return jsonify({'usuario': usuario.to_dict()}), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@rechazar_en_autenticacion
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