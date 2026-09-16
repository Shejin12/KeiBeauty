import os
from io import BytesIO
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, get_jwt
from utils.decorators import admin_required, rechazar_en_autenticacion
from utils.email import email_service
from models import db, Pedido, DetallePedido, Producto, Carrito, DetalleCarrito

try:
    from imagekitio import ImageKit
    IMAGEKIT_AVAILABLE = True
except ImportError:
    IMAGEKIT_AVAILABLE = False

pedidos_bp = Blueprint('pedidos', __name__, url_prefix='/api/pedidos')


def get_usuario_id_opcional():
    """Obtiene el usuario_id del JWT si existe, None si no hay token. Rechaza tokens temporales 2FA."""
    try:
        verify_jwt_in_request(optional=True)
        claims = get_jwt()
        if claims and claims.get('estado') == 'en_autenticacion':
            return None
        return get_jwt_identity()
    except:
        return None


def get_guest_token():
    """Obtiene el guest token del header"""
    return request.headers.get('X-Guest-Token') or request.args.get('guest_token')


@pedidos_bp.route('', methods=['POST'])
def crear_pedido():
    try:
        # Verificar si hay token JWT (opcional)
        usuario_id = get_usuario_id_opcional()
        es_invitado = usuario_id is None
        usuario_id = int(usuario_id) if usuario_id else None
        guest_token = get_guest_token()
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos JSON requeridos', 'message': 'El cuerpo de la petición debe ser JSON válido'}), 400
        
        # Validaciones de dirección
        direccion_envio = data.get('direccion_envio')
        if not direccion_envio or not direccion_envio.strip():
            return jsonify({'error': 'Dirección requerida', 'message': 'La dirección de envío es obligatoria'}), 400
        
        # Para invitados, validar campos adicionales
        email_contacto = None
        telefono_contacto = None
        
        if es_invitado:
            email_contacto = data.get('email_contacto')
            telefono_contacto = data.get('telefono_contacto')
            
            if not email_contacto:
                return jsonify({'error': 'Email requerido', 'message': 'El email de contacto es obligatorio para pedidos como invitado'}), 400
            if not telefono_contacto:
                return jsonify({'error': 'Teléfono requerido', 'message': 'El teléfono de contacto es obligatorio'}), 400
            if len(telefono_contacto.strip()) < 8:
                return jsonify({'error': 'Teléfono inválido', 'message': 'El teléfono debe tener al menos 8 dígitos'}), 400
            # Validar formato de email básico
            if '@' not in email_contacto or '.' not in email_contacto:
                return jsonify({'error': 'Email inválido', 'message': 'El formato del email no es válido'}), 400
        else:
            # Usuario autenticado: usar datos del perfil
            usuario = db.session.get(__import__('models', fromlist=['Usuario']).Usuario, usuario_id)
            if usuario:
                email_contacto = usuario.email
                telefono_contacto = usuario.telefono
        
        # Obtener items del pedido
        items_pedido = []
        monto_total = 0
        carrito = None
        
        if es_invitado:
            # Para invitados, obtener items del carrito de invitado
            if guest_token:
                carrito = Carrito.query.filter_by(guest_token=guest_token).first()
            
            if not carrito or not carrito.detalles:
                # Fallback: items en el body (compatibilidad)
                items_data = data.get('items', [])
                if not items_data or len(items_data) == 0:
                    return jsonify({'error': 'Carrito vacío', 'message': 'No hay productos en el carrito'}), 400
                
                for item_data in items_data:
                    producto_id = item_data.get('producto_id')
                    cantidad = item_data.get('cantidad', 1)
                    
                    if not producto_id:
                        return jsonify({'error': 'Producto requerido', 'message': 'Cada item debe tener producto_id'}), 400
                    
                    producto = db.session.get(Producto, producto_id)
                    if not producto or producto.estado != 'activo':
                        return jsonify({'error': 'Producto no disponible', 'message': f'El producto {producto_id} no está disponible'}), 400
                    
                    if cantidad > producto.stock:
                        return jsonify({'error': 'Stock insuficiente', 'message': f'Solo hay {producto.stock} unidades de {producto.nombre}'}), 400
                    
                    precio_unitario = float(producto.precio)
                    subtotal = precio_unitario * cantidad
                    monto_total += subtotal
                    
                    items_pedido.append({
                        'producto_id': producto.id,
                        'precio_unitario': precio_unitario,
                        'cantidad': cantidad,
                        'subtotal': subtotal,
                        'nombre_producto': producto.nombre
                    })
            else:
                # Usar items del carrito de invitado
                for detalle_carrito in carrito.detalles:
                    producto = detalle_carrito.producto
                    if not producto or producto.estado != 'activo':
                        return jsonify({'error': 'Producto no disponible', 'message': f'El producto {detalle_carrito.producto_id} ya no está disponible'}), 400
                    
                    if detalle_carrito.cantidad > producto.stock:
                        return jsonify({'error': 'Stock insuficiente', 'message': f'Solo hay {producto.stock} unidades de {producto.nombre}'}), 400
                    
                    subtotal = float(producto.precio) * detalle_carrito.cantidad
                    monto_total += subtotal
                    
                    items_pedido.append({
                        'producto_id': producto.id,
                        'precio_unitario': float(producto.precio),
                        'cantidad': detalle_carrito.cantidad,
                        'subtotal': subtotal,
                        'nombre_producto': producto.nombre
                    })
        else:
            # Usuario autenticado: usar carrito
            carrito = Carrito.query.filter_by(usuario_id=usuario_id).first()
            if not carrito or not carrito.detalles:
                return jsonify({'error': 'Carrito vacío', 'message': 'No hay productos en el carrito'}), 400
            
            for detalle_carrito in carrito.detalles:
                producto = detalle_carrito.producto
                if not producto or producto.estado != 'activo':
                    return jsonify({'error': 'Producto no disponible', 'message': f'El producto {detalle_carrito.producto_id} ya no está disponible'}), 400
                
                if detalle_carrito.cantidad > producto.stock:
                    return jsonify({'error': 'Stock insuficiente', 'message': f'Solo hay {producto.stock} unidades de {producto.nombre}'}), 400
                
                subtotal = float(producto.precio) * detalle_carrito.cantidad
                monto_total += subtotal
                
                items_pedido.append({
                    'producto_id': producto.id,
                    'precio_unitario': float(producto.precio),
                    'cantidad': detalle_carrito.cantidad,
                    'subtotal': subtotal,
                    'nombre_producto': producto.nombre
                })
        
        # Crear pedido y detalles en transacción
        try:
            pedido = Pedido(
                usuario_id=usuario_id,
                monto_total=monto_total,
                estado='pendiente',
                direccion_envio=direccion_envio.strip(),
                email_contacto=email_contacto,
                telefono_contacto=telefono_contacto
            )
            db.session.add(pedido)
            db.session.flush()  # Para obtener el ID del pedido
            
            for item in items_pedido:
                detalle = DetallePedido(
                    pedido_id=pedido.id,
                    producto_id=item['producto_id'],
                    precio_unitario=item['precio_unitario'],
                    cantidad=item['cantidad'],
                    subtotal=item['subtotal'],
                    nombre_producto=item.get('nombre_producto', '')
                )
                db.session.add(detalle)
                
                # Reducir stock
                producto = db.session.get(Producto, item['producto_id'])
                producto.stock -= item['cantidad']
            
            # Si es usuario autenticado, vaciar carrito
            if not es_invitado and carrito:
                DetalleCarrito.query.filter_by(carrito_id=carrito.id).delete()
                carrito.fecha_actualizacion = db.func.now()
            # Si es invitado, vaciar carrito de invitado
            elif es_invitado and carrito:
                DetalleCarrito.query.filter_by(carrito_id=carrito.id).delete()
                carrito.fecha_actualizacion = db.func.now()
            
            db.session.commit()
            
            # Enviar email de confirmación (async, no bloquear)
            try:
                if email_contacto:
                    nombre_contacto = usuario.nombre if not es_invitado and usuario else 'Cliente'
                    email_service.enviar_confirmacion_pedido(email_contacto, nombre_contacto, pedido.to_dict())
            except Exception as e:
                # Log pero no fallar el pedido
                print(f'Error enviando email confirmación: {e}')
            
            return jsonify({
                'data': pedido.to_dict(),
                'message': 'Pedido creado exitosamente.'
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Error al crear pedido', 'message': str(e)}), 500
            
    except Exception as e:
        return jsonify({'error': 'Error interno', 'message': str(e)}), 500


@pedidos_bp.route('', methods=['GET'])
@jwt_required()
@rechazar_en_autenticacion
def listar_pedidos():
    try:
        usuario_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = Pedido.query.filter_by(usuario_id=usuario_id).order_by(Pedido.fecha_pedido.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'data': [p.to_dict() for p in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            },
            'message': 'Pedidos obtenidos exitosamente.'
        }), 200
    except Exception as e:
        return jsonify({'error': 'Error al obtener pedidos', 'message': str(e)}), 500


@pedidos_bp.route('/<int:pedido_id>', methods=['GET'])
@jwt_required(optional=True)
@rechazar_en_autenticacion
def obtener_pedido(pedido_id):
    try:
        # Verificar si hay usuario autenticado
        verify_jwt_in_request(optional=True)
        claims = get_jwt()
        usuario_id = get_jwt_identity() if claims and claims.get('estado') != 'en_autenticacion' else None
        usuario_id = int(usuario_id) if usuario_id else None
        
        pedido = db.session.get(Pedido, pedido_id)
        if not pedido:
            return jsonify({'error': 'Pedido no encontrado', 'message': f'No existe pedido con id {pedido_id}'}), 404
        
        # Si es pedido de usuario autenticado
        if pedido.usuario_id is not None:
            if usuario_id is None:
                return jsonify({'error': 'Acceso denegado', 'message': 'Se requiere autenticación para ver este pedido'}), 401
            
            usuario = db.session.get(__import__('models', fromlist=['Usuario']).Usuario, usuario_id)
            # Solo el dueño o admin puede ver el pedido
            if pedido.usuario_id != usuario_id and not (usuario and usuario.rol == 'admin'):
                return jsonify({'error': 'Acceso denegado', 'message': 'No tienes permiso para ver este pedido'}), 403
        else:
            # Es pedido de invitado - permitir acceso con guest_token o email_contacto
            guest_token = request.headers.get('X-Guest-Token') or request.args.get('guest_token')
            email_contacto = request.args.get('email_contacto')
            
            # Si no hay guest_token ni email, exigir autenticación
            if not guest_token and not email_contacto:
                return jsonify({'error': 'Acceso denegado', 'message': 'Se requiere token de invitado o email de contacto para ver este pedido'}), 401
            
            # Validar guest_token si se proporciona
            if guest_token:
                carrito = Carrito.query.filter_by(guest_token=guest_token).first()
                if not carrito:
                    return jsonify({'error': 'Acceso denegado', 'message': 'Token de invitado inválido'}), 403
            
            # Validar email si se proporciona
            if email_contacto:
                if pedido.email_contacto != email_contacto:
                    return jsonify({'error': 'Acceso denegado', 'message': 'Email de contacto no coincide con el pedido'}), 403
        
        return jsonify({
            'data': pedido.to_dict(),
            'message': 'Pedido obtenido exitosamente.'
        }), 200
    except Exception as e:
        return jsonify({'error': 'Error al obtener pedido', 'message': str(e)}), 500


@pedidos_bp.route('/<int:pedido_id>/estado', methods=['PATCH'])
@jwt_required()
@admin_required
def cambiar_estado_pedido(pedido_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos JSON requeridos', 'message': 'El cuerpo de la petición debe ser JSON válido'}), 400
        
        nuevo_estado = data.get('estado')
        if not nuevo_estado:
            return jsonify({'error': 'Estado requerido', 'message': 'El campo estado es obligatorio'}), 400
        
        estados_validos = ['pendiente', 'confirmado', 'enviado', 'entregado', 'cancelado']
        if nuevo_estado not in estados_validos:
            return jsonify({'error': 'Estado inválido', 'message': f'Estados válidos: {", ".join(estados_validos)}'}), 400
        
        pedido = db.session.get(Pedido, pedido_id)
        if not pedido:
            return jsonify({'error': 'Pedido no encontrado', 'message': f'No existe pedido con id {pedido_id}'}), 404
        
        pedido.estado = nuevo_estado
        pedido.fecha_actualizacion = db.func.now()
        db.session.commit()
        
        return jsonify({
            'data': pedido.to_dict(),
            'message': 'Estado del pedido actualizado exitosamente.'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al actualizar estado', 'message': str(e)}), 500


# Configurar cliente ImageKit (opcional)
imagekit_client = None
if IMAGEKIT_AVAILABLE:
    imagekit_client = ImageKit(
        private_key=os.environ.get('IMAGEKIT_PRIVATE_KEY')
    )


@pedidos_bp.route('/<int:pedido_id>/guia', methods=['PUT', 'POST'])
@jwt_required()
@admin_required
def subir_guia(pedido_id):
    try:
        pedido = db.session.get(Pedido, pedido_id)
        if not pedido:
            return jsonify({'error': 'Pedido no encontrado', 'message': f'No existe pedido con id {pedido_id}'}), 404

        archivo = request.files.get('archivo')
        if not archivo:
            return jsonify({'error': 'Archivo requerido', 'message': 'Se debe enviar un archivo con el campo "archivo"'}), 400

        # Validar tipo de archivo (solo imágenes)
        tipos_permitidos = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/jpg']
        if archivo.content_type not in tipos_permitidos:
            return jsonify({'error': 'Tipo de archivo no soportado', 'message': f'Tipos permitidos: {", ".join(tipos_permitidos)}'}), 400

        # Subir archivo a ImageKit
        if not IMAGEKIT_AVAILABLE or imagekit_client is None:
            return jsonify({'error': 'ImageKit no disponible', 'message': 'El SDK de ImageKit no está instalado o las credenciales no son válidas.'}), 500

        archivo_bytes = archivo.read()
        upload_response = imagekit_client.files.upload(
            file=archivo_bytes,
            file_name=f"guia_pedido_{pedido_id}_{archivo.filename}",
            folder="/pedidos/guia"
        )

        pedido.url_guia = upload_response.url
        pedido.fecha_actualizacion = db.func.now()
        db.session.commit()

        return jsonify({
            'data': pedido.to_dict(),
            'message': 'Imagen de guía subida exitosamente.'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al subir imagen de guía', 'message': str(e)}), 500