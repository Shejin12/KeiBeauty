from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils.decorators import admin_required
from models import db, ConfiguracionTienda

configuracion_bp = Blueprint('configuracion', __name__, url_prefix='/api/configuracion')

# Claves numéricas que se validan como números >= 0.
CLAVES_NUMERICAS = ['costo_envio', 'minimo_envio_gratis']
# Claves booleanas (interruptores) que se validan como true/false.
CLAVES_BOOLEANAS = ['envio_gratis_activo']

# Valores aceptados para una clave booleana.
VALORES_VERDADEROS = ('true', '1', 'si', 'sí', 'yes', 'activo', 'on')
VALORES_FALSOS = ('false', '0', 'no', 'off', 'inactivo')


@configuracion_bp.route('', methods=['GET'])
@jwt_required()
@admin_required
def listar_configuracion():
    try:
        registros = ConfiguracionTienda.query.order_by(ConfiguracionTienda.clave.asc()).all()
        return jsonify({
            'data': [r.to_dict() for r in registros],
            'message': 'Configuración obtenida exitosamente.'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al obtener la configuración', 'message': str(e)}), 500


@configuracion_bp.route('', methods=['PUT'])
@jwt_required()
@admin_required
def actualizar_configuracion():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos JSON requeridos', 'message': 'El cuerpo de la petición debe ser JSON válido'}), 400

        clave = (data.get('clave') or '').strip()
        if not clave:
            return jsonify({'error': 'Clave requerida', 'message': 'El campo clave es obligatorio'}), 400
        if 'valor' not in data or data.get('valor') is None or str(data.get('valor')).strip() == '':
            return jsonify({'error': 'Valor requerido', 'message': 'El campo valor es obligatorio'}), 400

        registro = ConfiguracionTienda.query.filter_by(clave=clave).first()
        if not registro:
            return jsonify({
                'error': 'Clave no encontrada',
                'message': f'No existe la clave de configuración "{clave}"'
            }), 404

        valor = str(data.get('valor')).strip()

        # Las claves booleanas solo admiten valores de verdad/falso.
        if clave in CLAVES_BOOLEANAS:
            normalizado = valor.lower()
            if normalizado in VALORES_VERDADEROS:
                valor = 'true'
            elif normalizado in VALORES_FALSOS:
                valor = 'false'
            else:
                return jsonify({
                    'error': 'Valor inválido',
                    'message': f'El valor de "{clave}" debe ser true o false'
                }), 400

        # Las claves numéricas no admiten valores negativos ni texto no numérico.
        if clave in CLAVES_NUMERICAS:
            try:
                numero = float(valor)
            except (TypeError, ValueError):
                return jsonify({
                    'error': 'Valor inválido',
                    'message': f'El valor de "{clave}" debe ser un número'
                }), 400
            if numero < 0:
                return jsonify({
                    'error': 'Valor inválido',
                    'message': f'El valor de "{clave}" no puede ser negativo'
                }), 400
            valor = f'{numero:.2f}'

        ConfiguracionTienda.establecer(clave, valor)
        db.session.commit()

        return jsonify({
            'data': ConfiguracionTienda.query.filter_by(clave=clave).first().to_dict(),
            'message': 'Configuración actualizada exitosamente.'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al actualizar la configuración', 'message': str(e)}), 500


@configuracion_bp.route('/envio', methods=['GET'])
def configuracion_envio():
    """Política de envío (pública) para poder mostrar el desglose en el checkout."""
    try:
        return jsonify({
            'data': {
                'costo_envio': ConfiguracionTienda.obtener_numero('costo_envio', 0.0),
                'minimo_envio_gratis': ConfiguracionTienda.obtener_numero('minimo_envio_gratis', 0.0),
                'envio_gratis_activo': ConfiguracionTienda.obtener_booleano('envio_gratis_activo', True)
            },
            'message': 'Configuración de envío obtenida exitosamente.'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al obtener la configuración de envío', 'message': str(e)}), 500
