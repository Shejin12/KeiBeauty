import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, get_jwt
from utils.decorators import admin_required
from models import db, Producto, Marca, Categoria, ProductoFavorito, InventarioMovimiento, ProductoImagen, Notificacion, ProductoAlerta, Usuario
from datetime import datetime

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

products_bp = Blueprint('products', __name__, url_prefix='/api/products')

def notificar_stock_disponible(producto):
    """Notifica por app y correo a usuarios con alerta activa cuando el producto vuelve a tener stock"""
    try:
        if producto.stock <= 0:
            return
        alertas = ProductoAlerta.query.filter_by(producto_id=producto.id, activa=True).all()
        for alerta in alertas:
            titulo = f"{producto.nombre} ¡ya está disponible!"
            mensaje = f"El producto {producto.nombre} que esperabas ya tiene stock ({producto.stock} unidades). ¡No te quedes sin el tuyo!"
            notif = Notificacion(usuario_id=alerta.usuario_id, tipo='producto_stock', titulo=titulo, mensaje=mensaje, datos={'producto_id': producto.id, 'stock': producto.stock})
            db.session.add(notif)
            alerta.activa = False  # Desactivar tras notificar (una sola vez)
            # Enviar correo también
            try:
                from models import Usuario
                usuario = db.session.get(Usuario, alerta.usuario_id)
                if usuario and usuario.email:
                    from utils.email import email_service
                    email_service.enviar_notificacion_stock(usuario.email, usuario.nombre, producto.to_dict())
            except Exception as e:
                print(f"Error enviando correo stock a {alerta.usuario_id}: {e}")
        if alertas:
            db.session.commit()
    except Exception as e:
        print(f"Error notificando stock: {e}")
        db.session.rollback()


def _es_admin_actual():
    """Helper para detectar si el usuario actual es admin (con token válido y no temporal)"""
    try:
        verify_jwt_in_request(optional=True)
        # Si no hay token, get_jwt_identity() será None
        uid = get_jwt_identity()
        if not uid:
            return False
        # Verificar que no sea token temporal de 2FA
        try:
            from flask_jwt_extended import get_jwt
            claims = get_jwt()
            if claims and claims.get('estado') == 'en_autenticacion':
                return False
        except:
            pass
        usuario = db.session.get(Usuario, int(uid))
        return usuario is not None and usuario.rol == 'admin'
    except:
        return False

@products_bp.route('', methods=['GET'])
def get_products():
    try:
        categoria = request.args.get('categoria', type=int)
        marca = request.args.get('marca', type=int)
        buscar = request.args.get('buscar', type=str)
        con_favorito = request.args.get('con_favorito', type=int)
        estado = request.args.get('estado', type=str)

        es_admin = _es_admin_actual()

        if es_admin:
            query = Producto.query
            if estado and estado in ['activo', 'inactivo', 'agotado']:
                query = query.filter_by(estado=estado)
            # si no hay estado, mostrar todos (sin filtro)
        else:
            query = Producto.query.filter_by(estado='activo')

        if categoria:
            query = query.filter_by(categoria_id=categoria)
        if marca:
            query = query.filter_by(marca_id=marca)
        if buscar:
            # Escapar comodines LIKE para búsqueda literal: % y _ del usuario
            # se tratan como texto, no como comodines (bound parameter, sin SQL crudo)
            patron = buscar.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
            query = query.filter(Producto.nombre.ilike(f'%{patron}%', escape='\\'))

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

        if not producto:
            return jsonify({'error': 'Producto no encontrado', 'message': f'No existe producto con id {product_id}'}), 404

        # Permitir a admin ver cualquier estado, clientes solo activo
        if producto.estado != 'activo':
            if not _es_admin_actual():
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
        archivo = request.files.get('archivo')
        # Leer datos: puede ser JSON o form-data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            # Convertir valores numéricos en form-data
            for k in ['precio', 'stock', 'marca_id', 'categoria_id']:
                if k in data and data[k] is not None:
                    try:
                        data[k] = float(data[k]) if k == 'precio' else int(data[k])
                    except (ValueError, TypeError):
                        pass
        if not data:
            return jsonify({'error': 'Datos requeridos', 'message': 'El cuerpo debe contener los campos del producto'}), 400

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

        tamano = data.get('tamano', '')
        if tamano and len(str(tamano)) > 255:
            return jsonify({'error': 'Tamaño inválido', 'message': 'El tamaño no debe exceder 255 caracteres'}), 400

        # Subir imagen si se envía archivo
        archivo = request.files.get('archivo')
        imagen_url = data.get('imagen_url', '')
        if archivo and archivo.filename:
            tipos_permitidos = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/jpg']
            if archivo.content_type not in tipos_permitidos:
                return jsonify({'error': 'Tipo de archivo no soportado', 'message': f'Tipos permitidos: {", ".join(tipos_permitidos)}'}), 400
            if not IMAGEKIT_AVAILABLE or imagekit_client is None:
                return jsonify({'error': 'ImageKit no disponible', 'message': 'El SDK de ImageKit no está instalado o las credenciales no son válidas.'}), 500
            archivo_bytes = archivo.read()
            upload_response = imagekit_client.files.upload(
                file=archivo_bytes,
                file_name=f"producto_{data['nombre']}_{archivo.filename}",
                folder="/productos"
            )
            imagen_url = upload_response.url

        estado_inicial = 'agotado' if stock == 0 else data.get('estado', 'activo')
        producto = Producto(
            nombre=data['nombre'],
            descripcion=data.get('descripcion', ''),
            ingredientes_clave=data.get('ingredientes_clave', ''),
            tipo_piel=data.get('tipo_piel', ''),
            precio=precio,
            stock=stock,
            imagen_url=imagen_url,
            tamano=tamano,
            estado=estado_inicial,
            marca_id=data['marca_id'],
            categoria_id=data['categoria_id']
        )

        db.session.add(producto)
        db.session.flush()  # para obtener id antes de commit
        # Crear entrada en galería si hay imagen
        if imagen_url:
            try:
                # Limpiar principal anterior si existiera (no debería haber)
                imagen_principal = ProductoImagen(producto_id=producto.id, imagen_url=imagen_url, es_principal=True, orden=0)
                db.session.add(imagen_principal)
            except:
                pass
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

        stock_previo = producto.stock
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            for k in ['precio', 'stock', 'marca_id', 'categoria_id']:
                if k in data and data[k] is not None:
                    try:
                        data[k] = float(data[k]) if k == 'precio' else int(float(data[k]))
                    except (ValueError, TypeError):
                        pass
        if not data and not request.files:
            return jsonify({'error': 'Datos requeridos', 'message': 'El cuerpo debe contener los campos'}), 400
        if not data:
            data = {}

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
                # Actualizar estado según stock
                if stock == 0:
                    producto.estado = 'agotado'
                elif producto.estado == 'agotado' and stock > 0:
                    producto.estado = 'activo'
            except (ValueError, TypeError):
                return jsonify({'error': 'Stock inválido', 'message': 'El stock debe ser un entero válido'}), 400
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
                file_name=f"producto_{product_id}_{archivo.filename}",
                folder="/productos"
            )
            producto.imagen_url = upload_response.url
            # También crear entrada en galería como principal
            try:
                ProductoImagen.query.filter_by(producto_id=product_id, es_principal=True).update({ProductoImagen.es_principal: False})
                nueva = ProductoImagen(producto_id=product_id, imagen_url=upload_response.url, es_principal=True, orden=ProductoImagen.query.filter_by(producto_id=product_id).count())
                db.session.add(nueva)
            except:
                pass
        elif 'imagen_url' in data:
            producto.imagen_url = data['imagen_url']
        if 'estado' in data:
            if data['estado'] not in ['activo', 'inactivo', 'agotado']:
                return jsonify({'error': 'Estado inválido', 'message': 'Estado debe ser: activo, inactivo o agotado'}), 400
            producto.estado = data['estado']
        if 'tamano' in data:
            producto.tamano = data['tamano']
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
        # Notificar si volvió a tener stock
        if stock_previo == 0 and producto.stock > 0:
            notificar_stock_disponible(producto)

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


@products_bp.route('/<int:product_id>/imagen', methods=['POST'])
@jwt_required()
@admin_required
def subir_imagen_producto(product_id):
    try:
        producto = db.session.get(Producto, product_id)
        if not producto:
            return jsonify({'error': 'Producto no encontrado', 'message': f'No existe producto con id {product_id}'}), 404
        archivo = request.files.get('archivo')
        if not archivo:
            return jsonify({'error': 'Archivo requerido', 'message': 'Se debe enviar un archivo con el campo "archivo"'}), 400
        tipos_permitidos = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/jpg']
        if archivo.content_type not in tipos_permitidos:
            return jsonify({'error': 'Tipo de archivo no soportado', 'message': f'Tipos permitidos: {", ".join(tipos_permitidos)}'}), 400
        if not IMAGEKIT_AVAILABLE or imagekit_client is None:
            return jsonify({'error': 'ImageKit no disponible', 'message': 'El SDK de ImageKit no está instalado o las credenciales no son válidas.'}), 500
        archivo_bytes = archivo.read()
        upload_response = imagekit_client.files.upload(
            file=archivo_bytes,
            file_name=f"producto_{product_id}_{archivo.filename}",
            folder="/productos"
        )
        producto.imagen_url = upload_response.url
        db.session.commit()
        return jsonify({'data': producto.to_dict(), 'message': 'Imagen del producto subida exitosamente.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al subir imagen del producto', 'message': str(e)}), 500


# --- Galería múltiple ---
@products_bp.route('/<int:product_id>/imagenes', methods=['GET'])
def listar_imagenes_producto(product_id):
    try:
        producto = db.session.get(Producto, product_id)
        if not producto:
            return jsonify({'error': 'Producto no encontrado', 'message': f'No existe producto con id {product_id}'}), 404
        imagenes = ProductoImagen.query.filter_by(producto_id=product_id).order_by(ProductoImagen.es_principal.desc(), ProductoImagen.orden.asc(), ProductoImagen.id.asc()).all()
        return jsonify({'data': [img.to_dict() for img in imagenes], 'message': 'Imágenes obtenidas exitosamente.'}), 200
    except Exception as e:
        return jsonify({'error': 'Error al listar imágenes', 'message': str(e)}), 500


@products_bp.route('/<int:product_id>/imagenes', methods=['POST'])
@jwt_required()
@admin_required
def subir_imagenes_galeria(product_id):
    try:
        producto = db.session.get(Producto, product_id)
        if not producto:
            return jsonify({'error': 'Producto no encontrado', 'message': f'No existe producto con id {product_id}'}), 404
        archivos = request.files.getlist('archivos')
        # Compatibilidad con campo archivo singular
        if not archivos or (len(archivos) == 1 and archivos[0].filename == ''):
            archivo = request.files.get('archivo')
            if archivo and archivo.filename:
                archivos = [archivo]
            else:
                # También permitir URLs via JSON
                if request.is_json:
                    data = request.get_json()
                    urls = data.get('imagenes') or data.get('urls') or []
                    if isinstance(urls, str):
                        urls = [urls]
                    creadas = []
                    for url in urls:
                        if not url:
                            continue
                        existe_principal = ProductoImagen.query.filter_by(producto_id=product_id, es_principal=True).first()
                        img = ProductoImagen(producto_id=product_id, imagen_url=url.strip(), es_principal=False if existe_principal else True, orden=ProductoImagen.query.filter_by(producto_id=product_id).count())
                        db.session.add(img)
                        creadas.append(img)
                    db.session.commit()
                    return jsonify({'data': [c.to_dict() for c in creadas], 'message': f'{len(creadas)} imágenes agregadas.'}), 201
                return jsonify({'error': 'Archivo requerido', 'message': 'Envía archivos con campo "archivos" o "archivo"'}), 400
        if not IMAGEKIT_AVAILABLE or imagekit_client is None:
            return jsonify({'error': 'ImageKit no disponible', 'message': 'SDK no instalado'}), 500
        tipos_permitidos = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/jpg']
        creadas = []
        for archivo in archivos:
            if not archivo.filename:
                continue
            if archivo.content_type not in tipos_permitidos:
                continue
            archivo_bytes = archivo.read()
            upload_response = imagekit_client.files.upload(
                file=archivo_bytes,
                file_name=f"producto_{product_id}_{archivo.filename}",
                folder="/productos"
            )
            existe_principal = ProductoImagen.query.filter_by(producto_id=product_id, es_principal=True).first()
            es_principal = False if existe_principal else (len(creadas) == 0 and ProductoImagen.query.filter_by(producto_id=product_id).count() == 0)
            img = ProductoImagen(
                producto_id=product_id,
                imagen_url=upload_response.url,
                es_principal=es_principal,
                orden=ProductoImagen.query.filter_by(producto_id=product_id).count()
            )
            db.session.add(img)
            creadas.append(img)
        db.session.commit()
        # Sincronizar imagen_url principal legacy por compatibilidad
        principal = ProductoImagen.query.filter_by(producto_id=product_id, es_principal=True).first()
        if principal:
            producto.imagen_url = principal.imagen_url
            db.session.commit()
        return jsonify({'data': [c.to_dict() for c in creadas], 'message': f'{len(creadas)} imágenes subidas exitosamente.'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al subir imágenes', 'message': str(e)}), 500


@products_bp.route('/<int:product_id>/imagenes/<int:imagen_id>/principal', methods=['PUT'])
@jwt_required()
@admin_required
def marcar_imagen_principal(product_id, imagen_id):
    try:
        imagen = ProductoImagen.query.filter_by(id=imagen_id, producto_id=product_id).first()
        if not imagen:
            return jsonify({'error': 'Imagen no encontrada', 'message': f'No existe imagen {imagen_id} para producto {product_id}'}), 404
        # Quitar principal anterior
        ProductoImagen.query.filter_by(producto_id=product_id, es_principal=True).update({ProductoImagen.es_principal: False})
        imagen.es_principal = True
        db.session.commit()
        # Actualizar legacy
        producto = db.session.get(Producto, product_id)
        if producto:
            producto.imagen_url = imagen.imagen_url
            db.session.commit()
        return jsonify({'data': imagen.to_dict(), 'message': 'Imagen marcada como principal.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al marcar principal', 'message': str(e)}), 500


@products_bp.route('/<int:product_id>/imagenes/<int:imagen_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def eliminar_imagen_galeria(product_id, imagen_id):
    try:
        imagen = ProductoImagen.query.filter_by(id=imagen_id, producto_id=product_id).first()
        if not imagen:
            return jsonify({'error': 'Imagen no encontrada', 'message': f'No existe imagen {imagen_id}'}), 404
        era_principal = imagen.es_principal
        db.session.delete(imagen)
        db.session.flush()
        # Si era principal, asignar nueva principal si quedan imágenes
        if era_principal:
            siguiente = ProductoImagen.query.filter_by(producto_id=product_id).order_by(ProductoImagen.orden.asc()).first()
            if siguiente:
                siguiente.es_principal = True
                producto = db.session.get(Producto, product_id)
                if producto:
                    producto.imagen_url = siguiente.imagen_url
        else:
            # Si no era principal y no quedan imágenes con principal, asegurar una
            if not ProductoImagen.query.filter_by(producto_id=product_id, es_principal=True).first():
                primera = ProductoImagen.query.filter_by(producto_id=product_id).order_by(ProductoImagen.orden.asc()).first()
                if primera:
                    primera.es_principal = True
        db.session.commit()
        return jsonify({'data': None, 'message': 'Imagen eliminada exitosamente.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar imagen', 'message': str(e)}), 500


@products_bp.route('/<int:product_id>/inventario', methods=['POST'])
@jwt_required()
@admin_required
def ajustar_inventario(product_id):
    try:
        producto = db.session.get(Producto, product_id)
        if not producto:
            return jsonify({'error': 'Producto no encontrado', 'message': f'No existe producto con id {product_id}'}), 404
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos JSON requeridos', 'message': 'El cuerpo de la petición debe ser JSON válido'}), 400
        tipo = data.get('tipo')
        cantidad = data.get('cantidad')
        if tipo not in ['entrada', 'salida']:
            return jsonify({'error': 'Tipo inválido', 'message': 'El tipo debe ser: entrada o salida'}), 400
        try:
            cantidad = int(cantidad)
        except (ValueError, TypeError):
            return jsonify({'error': 'Cantidad inválida', 'message': 'La cantidad debe ser un número entero'}), 400
        if cantidad <= 0:
            return jsonify({'error': 'Cantidad inválida', 'message': 'La cantidad debe ser mayor a 0'}), 400
        costo_unitario = data.get('costo_unitario')
        if tipo == 'entrada' and costo_unitario is not None:
            try:
                costo_unitario = float(costo_unitario)
                if costo_unitario < 0:
                    return jsonify({'error': 'Costo inválido', 'message': 'El costo no puede ser negativo'}), 400
            except (ValueError, TypeError):
                return jsonify({'error': 'Costo inválido', 'message': 'Costo debe ser número'}), 400
        else:
            costo_unitario = None
        stock_previo = producto.stock
        if tipo == 'entrada':
            producto.stock += cantidad
        elif tipo == 'salida':
            if producto.stock < cantidad:
                return jsonify({'error': 'Stock insuficiente', 'message': f'Solo hay {producto.stock} unidades disponibles'}), 400
            producto.stock -= cantidad
        # Actualizar estado según stock
        if producto.stock == 0:
            producto.estado = 'agotado'
        elif producto.estado == 'agotado' and producto.stock > 0:
            producto.estado = 'activo'
        movimiento = InventarioMovimiento(
            producto_id=producto.id,
            tipo=tipo,
            cantidad=cantidad,
            costo_unitario=costo_unitario if tipo == 'entrada' else None
        )
        db.session.add(movimiento)
        db.session.commit()
        # Si pasó de 0 a >0, notificar
        if stock_previo == 0 and producto.stock > 0 and tipo == 'entrada':
            notificar_stock_disponible(producto)
        return jsonify({'data': producto.to_dict(), 'message': f'Inventario actualizado: {tipo} de {cantidad} unidades'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al ajustar inventario', 'message': str(e)}), 500


@products_bp.route('/marcas', methods=['GET', 'OPTIONS'])
def get_marcas():
    try:
        marcas = Marca.query.all()
        data = [{'id': m.id, 'nombre': m.nombre, 'logo_url': m.logo_url} for m in marcas]
        return jsonify({
            'data': data,
            'message': 'Marcas obtenidas exitosamente.'
        }), 200
    except Exception as e:
        return jsonify({'error': 'Error al obtener marcas', 'message': str(e)}), 500


@products_bp.route('/admin-test', methods=['GET'])
@jwt_required()
@admin_required
def admin_test():
    return jsonify({'data': None, 'message': 'Acceso de administrador concedido.'}), 200