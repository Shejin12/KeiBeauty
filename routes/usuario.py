from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import rechazar_en_autenticacion
from models import db, Usuario, UsuarioDireccion, UsuarioTelefono

usuario_bp = Blueprint('usuario', __name__, url_prefix='/api/usuario')

# Longitud minima de una direccion de envio (caracteres).
MIN_CARACTERES_DIRECCION = 10
# Cantidad minima de digitos de un telefono.
MIN_DIGITOS_TELEFONO = 8
# Longitud maxima del alias de una direccion.
MAX_CARACTERES_ALIAS = 50


def _usuario_actual():
    """Devuelve el usuario autenticado o None."""
    usuario_id = get_jwt_identity()
    if not usuario_id:
        return None
    return db.session.get(Usuario, int(usuario_id))


def _digitos(valor):
    """Cantidad de digitos de un texto (ignora espacios, guiones y signos)."""
    return len(''.join(c for c in str(valor) if c.isdigit()))


def _garantizar_principal_direccion(usuario):
    """Devuelve la direccion principal activa del usuario.

    Si no hay ninguna activa (por ejemplo porque la principal se desactivo o
    se elimino), promueve la direccion activa mas antigua.
    """
    principal = UsuarioDireccion.query.filter_by(
        usuario_id=usuario.id, es_principal=True, activa=True
    ).first()
    if principal:
        return principal

    siguiente = UsuarioDireccion.query.filter_by(
        usuario_id=usuario.id, activa=True
    ).order_by(UsuarioDireccion.fecha_creacion.asc(), UsuarioDireccion.id.asc()).first()
    if siguiente:
        siguiente.es_principal = True
    return siguiente


def _garantizar_principal_telefono(usuario):
    """Devuelve el telefono principal activo del usuario.

    Si no hay ninguno activo, promueve el telefono activo mas antiguo.
    """
    principal = UsuarioTelefono.query.filter_by(
        usuario_id=usuario.id, es_principal=True, activo=True
    ).first()
    if principal:
        return principal

    siguiente = UsuarioTelefono.query.filter_by(
        usuario_id=usuario.id, activo=True
    ).order_by(UsuarioTelefono.fecha_creacion.asc(), UsuarioTelefono.id.asc()).first()
    if siguiente:
        siguiente.es_principal = True
    return siguiente


def _sincronizar_direccion_principal(usuario):
    """Mantiene usuarios.direccion_envio sincronizada con la direccion principal."""
    principal = _garantizar_principal_direccion(usuario)
    usuario.direccion_envio = principal.direccion if principal else None


def _sincronizar_telefono_principal(usuario):
    """Mantiene usuarios.telefono sincronizada con el telefono principal.

    La columna usuarios.telefono es NOT NULL: si el usuario se queda sin
    telefonos se conserva el valor anterior en vez de dejarla vacia.
    """
    principal = _garantizar_principal_telefono(usuario)
    if principal:
        usuario.telefono = principal.telefono


def _promover_siguiente_direccion(usuario):
    """Promueve como principal la direccion activa mas antigua del usuario."""
    siguiente = UsuarioDireccion.query.filter_by(
        usuario_id=usuario.id, es_principal=False, activa=True
    ).order_by(UsuarioDireccion.fecha_creacion.asc(), UsuarioDireccion.id.asc()).first()
    if siguiente:
        siguiente.es_principal = True
    return siguiente


def _promover_siguiente_telefono(usuario):
    """Promueve como principal el telefono activo mas antiguo del usuario."""
    siguiente = UsuarioTelefono.query.filter_by(
        usuario_id=usuario.id, es_principal=False, activo=True
    ).order_by(UsuarioTelefono.fecha_creacion.asc(), UsuarioTelefono.id.asc()).first()
    if siguiente:
        siguiente.es_principal = True
    return siguiente


# ---------------------------------------------------------------------------
# Direcciones de envio
# ---------------------------------------------------------------------------

@usuario_bp.route('/direcciones', methods=['GET'])
@jwt_required()
@rechazar_en_autenticacion
def listar_direcciones():
    try:
        usuario = _usuario_actual()
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado.', 'message': 'No se pudo localizar la cuenta.'}), 404

        direcciones = UsuarioDireccion.query.filter_by(usuario_id=usuario.id).order_by(
            UsuarioDireccion.es_principal.desc(),
            UsuarioDireccion.fecha_creacion.asc(),
            UsuarioDireccion.id.asc()
        ).all()

        return jsonify({
            'data': [d.to_dict() for d in direcciones],
            'message': 'Direcciones obtenidas exitosamente.'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al obtener las direcciones', 'message': str(e)}), 500


@usuario_bp.route('/direcciones', methods=['POST'])
@jwt_required()
@rechazar_en_autenticacion
def crear_direccion():
    try:
        usuario = _usuario_actual()
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado.', 'message': 'No se pudo localizar la cuenta.'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos JSON requeridos', 'message': 'El cuerpo de la petición debe ser JSON válido'}), 400

        direccion = (data.get('direccion') or '').strip()
        if not direccion:
            return jsonify({'error': 'Dirección requerida', 'message': 'La dirección de envío es obligatoria'}), 400
        if len(direccion) < MIN_CARACTERES_DIRECCION:
            return jsonify({
                'error': 'Dirección inválida',
                'message': f'La dirección debe tener al menos {MIN_CARACTERES_DIRECCION} caracteres'
            }), 400

        alias = (data.get('alias') or '').strip() or None
        if alias and len(alias) > MAX_CARACTERES_ALIAS:
            return jsonify({
                'error': 'Alias inválido',
                'message': f'El alias no debe exceder {MAX_CARACTERES_ALIAS} caracteres'
            }), 400

        # Solo puede haber una direccion principal por usuario.
        es_principal = bool(data.get('es_principal'))
        ya_tiene_principal = UsuarioDireccion.query.filter_by(
            usuario_id=usuario.id, es_principal=True
        ).first() is not None
        if es_principal:
            UsuarioDireccion.query.filter_by(usuario_id=usuario.id, es_principal=True).update(
                {UsuarioDireccion.es_principal: False}
            )

        nueva = UsuarioDireccion(
            usuario_id=usuario.id,
            alias=alias,
            direccion=direccion,
            es_principal=es_principal,
            activa=True
        )
        db.session.add(nueva)
        db.session.flush()

        # Si el usuario no tenia direccion principal, esta pasa a serlo.
        if not ya_tiene_principal and not es_principal:
            nueva.es_principal = True

        _sincronizar_direccion_principal(usuario)
        db.session.commit()

        return jsonify({
            'data': nueva.to_dict(),
            'message': 'Dirección guardada exitosamente.'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al guardar la dirección', 'message': str(e)}), 500


@usuario_bp.route('/direcciones/<int:direccion_id>', methods=['PUT'])
@jwt_required()
@rechazar_en_autenticacion
def actualizar_direccion(direccion_id):
    try:
        usuario = _usuario_actual()
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado.', 'message': 'No se pudo localizar la cuenta.'}), 404

        direccion = UsuarioDireccion.query.filter_by(id=direccion_id, usuario_id=usuario.id).first()
        if not direccion:
            return jsonify({'error': 'Dirección no encontrada', 'message': f'No existe la dirección {direccion_id} en tu cuenta'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos JSON requeridos', 'message': 'El cuerpo de la petición debe ser JSON válido'}), 400

        if 'alias' in data:
            alias = (data.get('alias') or '').strip() or None
            if alias and len(alias) > MAX_CARACTERES_ALIAS:
                return jsonify({
                    'error': 'Alias inválido',
                    'message': f'El alias no debe exceder {MAX_CARACTERES_ALIAS} caracteres'
                }), 400
            direccion.alias = alias

        if 'direccion' in data:
            valor = (data.get('direccion') or '').strip()
            if not valor:
                return jsonify({'error': 'Dirección requerida', 'message': 'La dirección de envío no puede quedar vacía'}), 400
            if len(valor) < MIN_CARACTERES_DIRECCION:
                return jsonify({
                    'error': 'Dirección inválida',
                    'message': f'La dirección debe tener al menos {MIN_CARACTERES_DIRECCION} caracteres'
                }), 400
            direccion.direccion = valor

        if 'activa' in data:
            direccion.activa = bool(data.get('activa'))
            # Una direccion desactivada no puede seguir siendo la principal.
            if not direccion.activa:
                direccion.es_principal = False

        if 'es_principal' in data and data.get('es_principal'):
            UsuarioDireccion.query.filter_by(usuario_id=usuario.id, es_principal=True).update(
                {UsuarioDireccion.es_principal: False}
            )
            direccion.es_principal = True

        _sincronizar_direccion_principal(usuario)
        db.session.commit()

        return jsonify({
            'data': direccion.to_dict(),
            'message': 'Dirección actualizada exitosamente.'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al actualizar la dirección', 'message': str(e)}), 500


@usuario_bp.route('/direcciones/<int:direccion_id>', methods=['DELETE'])
@jwt_required()
@rechazar_en_autenticacion
def eliminar_direccion(direccion_id):
    try:
        usuario = _usuario_actual()
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado.', 'message': 'No se pudo localizar la cuenta.'}), 404

        direccion = UsuarioDireccion.query.filter_by(id=direccion_id, usuario_id=usuario.id).first()
        if not direccion:
            return jsonify({'error': 'Dirección no encontrada', 'message': f'No existe la dirección {direccion_id} en tu cuenta'}), 404

        era_principal = direccion.es_principal
        db.session.delete(direccion)
        db.session.flush()

        # Si era la principal se promueve la siguiente para no dejar la cuenta sin direccion por defecto.
        if era_principal:
            _promover_siguiente_direccion(usuario)

        _sincronizar_direccion_principal(usuario)
        db.session.commit()

        return jsonify({
            'data': None,
            'message': 'Dirección eliminada exitosamente.'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar la dirección', 'message': str(e)}), 500


# ---------------------------------------------------------------------------
# Telefonos de contacto
# ---------------------------------------------------------------------------

@usuario_bp.route('/telefonos', methods=['GET'])
@jwt_required()
@rechazar_en_autenticacion
def listar_telefonos():
    try:
        usuario = _usuario_actual()
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado.', 'message': 'No se pudo localizar la cuenta.'}), 404

        telefonos = UsuarioTelefono.query.filter_by(usuario_id=usuario.id).order_by(
            UsuarioTelefono.es_principal.desc(),
            UsuarioTelefono.fecha_creacion.asc(),
            UsuarioTelefono.id.asc()
        ).all()

        return jsonify({
            'data': [t.to_dict() for t in telefonos],
            'message': 'Teléfonos obtenidos exitosamente.'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al obtener los teléfonos', 'message': str(e)}), 500


@usuario_bp.route('/telefonos', methods=['POST'])
@jwt_required()
@rechazar_en_autenticacion
def crear_telefono():
    try:
        usuario = _usuario_actual()
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado.', 'message': 'No se pudo localizar la cuenta.'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos JSON requeridos', 'message': 'El cuerpo de la petición debe ser JSON válido'}), 400

        telefono = (data.get('telefono') or '').strip()
        if not telefono:
            return jsonify({'error': 'Teléfono requerido', 'message': 'El teléfono es obligatorio'}), 400
        if _digitos(telefono) < MIN_DIGITOS_TELEFONO:
            return jsonify({
                'error': 'Teléfono inválido',
                'message': f'El teléfono debe tener al menos {MIN_DIGITOS_TELEFONO} dígitos'
            }), 400
        if len(telefono) > 20:
            return jsonify({'error': 'Teléfono inválido', 'message': 'El teléfono no debe exceder 20 caracteres'}), 400

        es_principal = bool(data.get('es_principal'))
        ya_tiene_principal = UsuarioTelefono.query.filter_by(
            usuario_id=usuario.id, es_principal=True
        ).first() is not None
        if es_principal:
            UsuarioTelefono.query.filter_by(usuario_id=usuario.id, es_principal=True).update(
                {UsuarioTelefono.es_principal: False}
            )

        nuevo = UsuarioTelefono(
            usuario_id=usuario.id,
            telefono=telefono,
            es_principal=es_principal,
            activo=True
        )
        db.session.add(nuevo)
        db.session.flush()

        # Si el usuario no tenia telefono principal, este pasa a serlo.
        if not ya_tiene_principal and not es_principal:
            nuevo.es_principal = True

        _sincronizar_telefono_principal(usuario)
        db.session.commit()

        return jsonify({
            'data': nuevo.to_dict(),
            'message': 'Teléfono guardado exitosamente.'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al guardar el teléfono', 'message': str(e)}), 500


@usuario_bp.route('/telefonos/<int:telefono_id>', methods=['PUT'])
@jwt_required()
@rechazar_en_autenticacion
def actualizar_telefono(telefono_id):
    try:
        usuario = _usuario_actual()
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado.', 'message': 'No se pudo localizar la cuenta.'}), 404

        telefono = UsuarioTelefono.query.filter_by(id=telefono_id, usuario_id=usuario.id).first()
        if not telefono:
            return jsonify({'error': 'Teléfono no encontrado', 'message': f'No existe el teléfono {telefono_id} en tu cuenta'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos JSON requeridos', 'message': 'El cuerpo de la petición debe ser JSON válido'}), 400

        if 'telefono' in data:
            valor = (data.get('telefono') or '').strip()
            if not valor:
                return jsonify({'error': 'Teléfono requerido', 'message': 'El teléfono no puede quedar vacío'}), 400
            if _digitos(valor) < MIN_DIGITOS_TELEFONO:
                return jsonify({
                    'error': 'Teléfono inválido',
                    'message': f'El teléfono debe tener al menos {MIN_DIGITOS_TELEFONO} dígitos'
                }), 400
            if len(valor) > 20:
                return jsonify({'error': 'Teléfono inválido', 'message': 'El teléfono no debe exceder 20 caracteres'}), 400
            telefono.telefono = valor

        if 'activo' in data:
            telefono.activo = bool(data.get('activo'))
            # Un telefono desactivado no puede seguir siendo el principal.
            if not telefono.activo:
                telefono.es_principal = False

        if 'es_principal' in data and data.get('es_principal'):
            UsuarioTelefono.query.filter_by(usuario_id=usuario.id, es_principal=True).update(
                {UsuarioTelefono.es_principal: False}
            )
            telefono.es_principal = True

        _sincronizar_telefono_principal(usuario)
        db.session.commit()

        return jsonify({
            'data': telefono.to_dict(),
            'message': 'Teléfono actualizado exitosamente.'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al actualizar el teléfono', 'message': str(e)}), 500


@usuario_bp.route('/telefonos/<int:telefono_id>', methods=['DELETE'])
@jwt_required()
@rechazar_en_autenticacion
def eliminar_telefono(telefono_id):
    try:
        usuario = _usuario_actual()
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado.', 'message': 'No se pudo localizar la cuenta.'}), 404

        telefono = UsuarioTelefono.query.filter_by(id=telefono_id, usuario_id=usuario.id).first()
        if not telefono:
            return jsonify({'error': 'Teléfono no encontrado', 'message': f'No existe el teléfono {telefono_id} en tu cuenta'}), 404

        era_principal = telefono.es_principal
        db.session.delete(telefono)
        db.session.flush()

        # Si era el principal se promueve el siguiente.
        if era_principal:
            _promover_siguiente_telefono(usuario)

        _sincronizar_telefono_principal(usuario)
        db.session.commit()

        return jsonify({
            'data': None,
            'message': 'Teléfono eliminado exitosamente.'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar el teléfono', 'message': str(e)}), 500
