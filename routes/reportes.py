from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from utils.decorators import admin_required
from models import db, Pedido, DetallePedido, Producto, Usuario, InventarioMovimiento, CatalogoEstadoPedido, CatalogoRolUsuario
from sqlalchemy import func, extract, case
from datetime import datetime, timedelta
import io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

reportes_bp = Blueprint('reportes', __name__, url_prefix='/api/reportes')


def _excel_response(wb, filename):
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name=filename, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


def _generar_excel(titulo, headers, rows, filename, subtitulo=None):
    """Arma un Excel con titulo, subtitulo de periodo, encabezados y datos.

    Usa get_column_letter para las columnas: `chr(64 + n)` se rompe a partir de
    la columna 26 y con celdas combinadas.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = titulo[:30]
    fill = PatternFill(start_color="8CB07A", end_color="8CB07A", fill_type="solid")
    font = Font(color="FFFFFF", bold=True)

    ws.append([titulo])
    if headers:
        end_col = get_column_letter(len(headers))
        ws.merge_cells(f'A1:{end_col}1')
        ws['A1'].font = Font(size=14, bold=True, color="3A3E40")
        ws['A1'].alignment = Alignment(horizontal='center')

        # Subtitulo con el periodo si se proporciona
        header_row = 2
        if subtitulo:
            ws.append([subtitulo])
            ws.merge_cells(f'A2:{end_col}2')
            ws['A2'].font = Font(size=10, italic=True, color="565659")
            ws['A2'].alignment = Alignment(horizontal='center')
            header_row = 3
            ws.append(headers)
        else:
            ws.append(headers)

        # Estilo encabezado
        for col in range(1, len(headers) + 1):
            cell = ws.cell(row=header_row, column=col)
            cell.fill = fill
            cell.font = font
            cell.alignment = Alignment(horizontal='center')

        for row in rows:
            # Asegurar que la fila tenga la misma longitud que los headers
            if len(row) < len(headers):
                row = list(row) + [''] * (len(headers) - len(row))
            # Normalizar valores vacios (None) para no romper el merge
            ws.append(['' if valor is None else valor for valor in row])

        # Ajustar ancho sin usar ws.columns (evita MergedCell)
        for idx, h in enumerate(headers, start=1):
            max_len = len(str(h))
            for r in rows:
                if idx - 1 < len(r) and r[idx - 1] not in (None, ''):
                    max_len = max(max_len, len(str(r[idx - 1])))
            ws.column_dimensions[get_column_letter(idx)].width = min(max_len + 4, 40)
    else:
        for row in rows:
            ws.append(['' if valor is None else valor for valor in row])

    return _excel_response(wb, filename)


def _subtitulo_periodo(desde, hasta):
    """Subtitulo con el periodo cubierto por el reporte."""
    if desde and hasta:
        return f'Periodo: {desde.strftime("%Y-%m-%d")} al {hasta.strftime("%Y-%m-%d")}'
    if desde:
        return f'Periodo: desde {desde.strftime("%Y-%m-%d")}'
    if hasta:
        return f'Periodo: hasta {hasta.strftime("%Y-%m-%d")}'
    return 'Periodo: todo el historial'


def _nombre_archivo(base, desde, hasta):
    """Nombre del archivo con el rango de fechas cuando aplica."""
    if desde and hasta:
        return f"{base}_{desde.strftime('%Y-%m-%d')}_{hasta.strftime('%Y-%m-%d')}.xlsx"
    if desde:
        return f"{base}_desde_{desde.strftime('%Y-%m-%d')}.xlsx"
    if hasta:
        return f"{base}_hasta_{hasta.strftime('%Y-%m-%d')}.xlsx"
    return f'{base}.xlsx'


def _parse_fecha(fecha_str):
    if not fecha_str:
        return None
    try:
        return datetime.strptime(fecha_str, '%Y-%m-%d')
    except:
        return None


def _rango(desde, hasta):
    """Devuelve (desde, hasta_fin) aplicando el filtro de fechas a un query."""
    query = Pedido.query
    if desde:
        query = query.filter(Pedido.fecha_pedido >= desde)
    if hasta:
        hasta_fin = hasta.replace(hour=23, minute=59, second=59)
        query = query.filter(Pedido.fecha_pedido <= hasta_fin)
    return query


@reportes_bp.route('/ventas-totales', methods=['GET'])
@jwt_required()
@admin_required
def ventas_totales():
    try:
        desde = _parse_fecha(request.args.get('desde'))
        hasta = _parse_fecha(request.args.get('hasta'))
        excel = request.args.get('excel') == '1' or request.args.get('formato') == 'excel'

        estado_cancelado = CatalogoEstadoPedido.por_nombre('cancelado')
        query = _rango(desde, hasta)
        if estado_cancelado:
            query = query.filter(Pedido.estado_id != estado_cancelado.id)

        total_pedidos = query.count()
        total_ventas = query.with_entities(func.coalesce(func.sum(Pedido.monto_total), 0)).scalar() or 0

        if excel:
            headers = ['Métrica', 'Valor']
            rows = [
                ['Total Pedidos', total_pedidos],
                ['Total Ventas (Q)', float(total_ventas)],
            ]
            if desde or hasta:
                rows.append(['Desde', desde.strftime('%Y-%m-%d') if desde else ''])
                rows.append(['Hasta', hasta.strftime('%Y-%m-%d') if hasta else ''])
            return _generar_excel(
                'Ventas Totales', headers, rows,
                _nombre_archivo('ventas_totales', desde, hasta),
                subtitulo=_subtitulo_periodo(desde, hasta)
            )

        return jsonify({
            'data': {
                'total_pedidos': total_pedidos,
                'total_ventas': float(total_ventas),
                'desde': desde.isoformat() if desde else None,
                'hasta': hasta.isoformat() if hasta else None
            },
            'message': 'Ventas totales obtenidas'
        }), 200
    except Exception as e:
        return jsonify({'error': 'Error', 'message': str(e)}), 500


@reportes_bp.route('/ventas-por-mes', methods=['GET'])
@jwt_required()
@admin_required
def ventas_por_mes():
    try:
        desde = _parse_fecha(request.args.get('desde'))
        hasta = _parse_fecha(request.args.get('hasta'))
        excel = request.args.get('excel') == '1' or request.args.get('formato') == 'excel'

        # Agrupar por año-mes, respetando el rango de fechas solicitado
        estado_cancelado = CatalogoEstadoPedido.por_nombre('cancelado')
        query = db.session.query(
            extract('year', Pedido.fecha_pedido).label('anio'),
            extract('month', Pedido.fecha_pedido).label('mes'),
            func.count(Pedido.id).label('pedidos'),
            func.sum(Pedido.monto_total).label('total')
        ).filter(Pedido.estado_id != estado_cancelado.id)

        if desde:
            query = query.filter(Pedido.fecha_pedido >= desde)
        if hasta:
            hasta_fin = hasta.replace(hour=23, minute=59, second=59)
            query = query.filter(Pedido.fecha_pedido <= hasta_fin)

        resultados = query.group_by('anio', 'mes').order_by('anio', 'mes').all()

        data = [{
            'anio': int(r.anio),
            'mes': int(r.mes),
            'pedidos': r.pedidos,
            'total': float(r.total or 0)
        } for r in resultados]

        if excel:
            headers = ['Año', 'Mes', 'Pedidos', 'Total Ventas (Q)']
            rows = [[d['anio'], d['mes'], d['pedidos'], d['total']] for d in data]
            return _generar_excel(
                'Ventas por Mes', headers, rows,
                _nombre_archivo('ventas_por_mes', desde, hasta),
                subtitulo=_subtitulo_periodo(desde, hasta)
            )

        return jsonify({
            'data': data,
            'desde': desde.isoformat() if desde else None,
            'hasta': hasta.isoformat() if hasta else None,
            'message': 'Ventas por mes obtenidas'
        }), 200
    except Exception as e:
        return jsonify({'error': 'Error', 'message': str(e)}), 500


@reportes_bp.route('/ventas-por-periodo', methods=['GET'])
@jwt_required()
@admin_required
def ventas_por_periodo():
    try:
        desde_str = request.args.get('desde')
        hasta_str = request.args.get('hasta')
        excel = request.args.get('excel') == '1' or request.args.get('formato') == 'excel'
        if not desde_str or not hasta_str:
            return jsonify({'error': 'Fechas requeridas', 'message': 'Se requieren desde y hasta (YYYY-MM-DD)'}), 400
        desde = _parse_fecha(desde_str)
        hasta = _parse_fecha(hasta_str)
        if not desde or not hasta:
            return jsonify({'error': 'Formato inválido', 'message': 'Use YYYY-MM-DD'}), 400
        hasta_fin = hasta.replace(hour=23, minute=59, second=59)
        estado_cancelado = CatalogoEstadoPedido.por_nombre('cancelado')
        pedidos = Pedido.query.filter(
            Pedido.fecha_pedido >= desde,
            Pedido.fecha_pedido <= hasta_fin,
            Pedido.estado_id != estado_cancelado.id
        ).order_by(Pedido.fecha_pedido.desc()).all()
        total = sum(float(p.monto_total) for p in pedidos)

        if excel:
            headers = ['ID', 'Fecha', 'Cliente', 'Estado', 'Total (Q)']
            rows = []
            for p in pedidos:
                nombre = p.usuario.nombre if p.usuario else (p.email_contacto or 'Invitado')
                rows.append([p.id, p.fecha_pedido.strftime('%Y-%m-%d'), nombre, p.estado_nombre, float(p.monto_total)])
            rows.append([])
            rows.append(['Total', '', '', '', total])
            return _generar_excel(
                'Ventas por Periodo', headers, rows,
                _nombre_archivo('ventas', desde, hasta),
                subtitulo=_subtitulo_periodo(desde, hasta)
            )

        return jsonify({
            'data': {
                'pedidos': [p.to_dict() for p in pedidos],
                'total_ventas': total,
                'cantidad': len(pedidos),
                'desde': desde_str,
                'hasta': hasta_str
            },
            'message': 'Ventas por periodo obtenidas'
        }), 200
    except Exception as e:
        return jsonify({'error': 'Error', 'message': str(e)}), 500


@reportes_bp.route('/ganancias', methods=['GET'])
@jwt_required()
@admin_required
def ganancias():
    try:
        desde = _parse_fecha(request.args.get('desde'))
        hasta = _parse_fecha(request.args.get('hasta'))
        excel = request.args.get('excel') == '1' or request.args.get('formato') == 'excel'

        # Ventas (ingresos)
        estado_cancelado = CatalogoEstadoPedido.por_nombre('cancelado')
        q_ventas = Pedido.query.filter(Pedido.estado_id != estado_cancelado.id)
        if desde:
            q_ventas = q_ventas.filter(Pedido.fecha_pedido >= desde)
        if hasta:
            hasta_fin = hasta.replace(hour=23, minute=59, second=59)
            q_ventas = q_ventas.filter(Pedido.fecha_pedido <= hasta_fin)
        ingresos = q_ventas.with_entities(func.coalesce(func.sum(Pedido.monto_total), 0)).scalar() or 0
        ingresos = float(ingresos)

        # Costos (entradas con costo_unitario)
        q_costos = InventarioMovimiento.query.filter_by(tipo='entrada').filter(
            InventarioMovimiento.costo_unitario.isnot(None)
        )
        if desde:
            q_costos = q_costos.filter(InventarioMovimiento.fecha >= desde)
        if hasta:
            hasta_fin = hasta.replace(hour=23, minute=59, second=59)
            q_costos = q_costos.filter(InventarioMovimiento.fecha <= hasta_fin)
        costos_data = q_costos.all()
        costos = sum(float(m.costo_unitario * m.cantidad) for m in costos_data) if costos_data else 0

        ganancia = ingresos - costos
        margen = (ganancia / ingresos * 100) if ingresos > 0 else 0

        # Serie mensual para el grafico de reportes
        por_mes = _ganancias_por_mes(desde, hasta)

        if excel:
            headers = ['Concepto', 'Monto (Q)']
            rows = [
                ['Ingresos (Ventas)', ingresos],
                ['Costos (Entradas)', costos],
                ['Ganancia', ganancia],
                ['Margen %', round(margen, 2)],
            ]
            if por_mes:
                rows.append([])
                rows.append(['Detalle por mes', '', ''])
                rows.append(['Año', 'Mes', 'Ingresos (Q)'])
                for m in por_mes:
                    rows.append([m['anio'], m['mes'], m['ingresos']])
            return _generar_excel(
                'Ganancias', headers, rows,
                _nombre_archivo('ganancias', desde, hasta),
                subtitulo=_subtitulo_periodo(desde, hasta)
            )

        return jsonify({
            'data': {
                'ingresos': ingresos,
                'costos': costos,
                'ganancia': ganancia,
                'margen_porcentaje': round(margen, 2),
                'por_mes': por_mes,
                'desde': desde.isoformat() if desde else None,
                'hasta': hasta.isoformat() if hasta else None
            },
            'message': 'Ganancias obtenidas'
        }), 200
    except Exception as e:
        return jsonify({'error': 'Error', 'message': str(e)}), 500


def _ganancias_por_mes(desde, hasta):
    """Serie mensual de ingresos y costos dentro del rango indicado."""
    estado_cancelado = CatalogoEstadoPedido.por_nombre('cancelado')

    q_ventas = db.session.query(
        extract('year', Pedido.fecha_pedido).label('anio'),
        extract('month', Pedido.fecha_pedido).label('mes'),
        func.coalesce(func.sum(Pedido.monto_total), 0).label('total')
    ).filter(Pedido.estado_id != estado_cancelado.id)
    if desde:
        q_ventas = q_ventas.filter(Pedido.fecha_pedido >= desde)
    if hasta:
        q_ventas = q_ventas.filter(Pedido.fecha_pedido <= hasta.replace(hour=23, minute=59, second=59))
    ventas = {(int(r.anio), int(r.mes)): float(r.total or 0) for r in q_ventas.group_by('anio', 'mes').all()}

    q_costos = db.session.query(
        extract('year', InventarioMovimiento.fecha).label('anio'),
        extract('month', InventarioMovimiento.fecha).label('mes'),
        func.coalesce(func.sum(InventarioMovimiento.costo_unitario * InventarioMovimiento.cantidad), 0).label('total')
    ).filter(InventarioMovimiento.tipo == 'entrada').filter(InventarioMovimiento.costo_unitario.isnot(None))
    if desde:
        q_costos = q_costos.filter(InventarioMovimiento.fecha >= desde)
    if hasta:
        q_costos = q_costos.filter(InventarioMovimiento.fecha <= hasta.replace(hour=23, minute=59, second=59))
    costos = {(int(r.anio), int(r.mes)): float(r.total or 0) for r in q_costos.group_by('anio', 'mes').all()}

    resultado = []
    for clave in sorted(set(ventas) | set(costos)):
        ingreso = ventas.get(clave, 0.0)
        costo = costos.get(clave, 0.0)
        resultado.append({
            'anio': clave[0],
            'mes': clave[1],
            'ingresos': round(ingreso, 2),
            'costos': round(costo, 2),
            'ganancia': round(ingreso - costo, 2)
        })
    return resultado


@reportes_bp.route('/productos-mas-vendidos', methods=['GET'])
@jwt_required()
@admin_required
def productos_mas_vendidos():
    try:
        limit = request.args.get('limit', 10, type=int)
        desde = _parse_fecha(request.args.get('desde'))
        hasta = _parse_fecha(request.args.get('hasta'))
        excel = request.args.get('excel') == '1' or request.args.get('formato') == 'excel'

        estado_cancelado = CatalogoEstadoPedido.por_nombre('cancelado')
        q = db.session.query(
            Producto.id,
            Producto.nombre,
            Producto.marca_id,
            func.sum(DetallePedido.cantidad).label('total_vendidos'),
            func.sum(DetallePedido.subtotal).label('total_ingresos')
        ).join(DetallePedido, DetallePedido.producto_id == Producto.id)\
         .join(Pedido, Pedido.id == DetallePedido.pedido_id)\
         .filter(Pedido.estado_id != estado_cancelado.id)

        if desde:
            q = q.filter(Pedido.fecha_pedido >= desde)
        if hasta:
            hasta_fin = hasta.replace(hour=23, minute=59, second=59)
            q = q.filter(Pedido.fecha_pedido <= hasta_fin)

        q = q.group_by(Producto.id, Producto.nombre, Producto.marca_id).order_by(
            func.sum(DetallePedido.cantidad).desc()
        ).limit(limit)
        resultados = q.all()

        data = []
        for r in resultados:
            marca = db.session.get(Producto, r.id).marca
            data.append({
                'producto_id': r.id,
                'nombre': r.nombre,
                'marca': marca.nombre if marca else '',
                'total_vendidos': int(r.total_vendidos),
                'total_ingresos': float(r.total_ingresos or 0)
            })

        if excel:
            headers = ['Producto', 'Marca', 'Unidades Vendidas', 'Ingresos (Q)']
            rows = [[d['nombre'], d['marca'], d['total_vendidos'], d['total_ingresos']] for d in data]
            return _generar_excel(
                'Productos Mas Vendidos', headers, rows,
                _nombre_archivo('productos_mas_vendidos', desde, hasta),
                subtitulo=_subtitulo_periodo(desde, hasta)
            )

        return jsonify({'data': data, 'message': 'Productos más vendidos obtenidos'}), 200
    except Exception as e:
        return jsonify({'error': 'Error', 'message': str(e)}), 500


@reportes_bp.route('/clientes-top', methods=['GET'])
@jwt_required()
@admin_required
def clientes_top():
    try:
        limit = request.args.get('limit', 10, type=int)
        desde = _parse_fecha(request.args.get('desde'))
        hasta = _parse_fecha(request.args.get('hasta'))
        excel = request.args.get('excel') == '1' or request.args.get('formato') == 'excel'

        rol_cliente = CatalogoRolUsuario.por_nombre('cliente')
        estado_cancelado = CatalogoEstadoPedido.por_nombre('cancelado')
        q = db.session.query(
            Usuario.id,
            Usuario.nombre,
            Usuario.email,
            func.count(Pedido.id).label('total_pedidos'),
            func.sum(Pedido.monto_total).label('total_gastado')
        ).join(Pedido, Pedido.usuario_id == Usuario.id)\
         .filter(Usuario.rol_id == rol_cliente.id).filter(Pedido.estado_id != estado_cancelado.id)

        if desde:
            q = q.filter(Pedido.fecha_pedido >= desde)
        if hasta:
            hasta_fin = hasta.replace(hour=23, minute=59, second=59)
            q = q.filter(Pedido.fecha_pedido <= hasta_fin)

        q = q.group_by(Usuario.id, Usuario.nombre, Usuario.email).order_by(
            func.sum(Pedido.monto_total).desc()
        ).limit(limit)
        resultados = q.all()

        data = []
        for r in resultados:
            data.append({
                'usuario_id': r.id,
                'nombre': r.nombre,
                'email': r.email,
                'total_pedidos': int(r.total_pedidos),
                'total_gastado': float(r.total_gastado or 0)
            })

        if excel:
            headers = ['Cliente', 'Email', 'Pedidos', 'Total Gastado (Q)']
            rows = [[d['nombre'], d['email'], d['total_pedidos'], d['total_gastado']] for d in data]
            return _generar_excel(
                'Clientes Top', headers, rows,
                _nombre_archivo('clientes_top', desde, hasta),
                subtitulo=_subtitulo_periodo(desde, hasta)
            )

        return jsonify({'data': data, 'message': 'Clientes top obtenidos'}), 200
    except Exception as e:
        return jsonify({'error': 'Error', 'message': str(e)}), 500


@reportes_bp.route('/ventas-con-descuento', methods=['GET'])
@jwt_required()
@admin_required
def ventas_con_descuento():
    """Ventas de productos con descuento y comparacion con el periodo anterior."""
    try:
        desde = _parse_fecha(request.args.get('desde'))
        hasta = _parse_fecha(request.args.get('hasta'))
        limit = request.args.get('limit', 0, type=int)
        excel = request.args.get('excel') == '1' or request.args.get('formato') == 'excel'

        estado_cancelado = CatalogoEstadoPedido.por_nombre('cancelado')

        def _consulta(desde_ini, hasta_fin):
            q = db.session.query(
                Producto.id,
                Producto.nombre,
                func.sum(DetallePedido.cantidad).label('unidades'),
                func.sum(
                    case(
                        (DetallePedido.descuento_porcentaje > 0, DetallePedido.cantidad),
                        else_=0
                    )
                ).label('unidades_con_descuento'),
                func.sum(DetallePedido.cantidad * DetallePedido.precio_real).label('ingresos_con_descuento'),
                func.sum(DetallePedido.cantidad * DetallePedido.precio_unitario).label('ingresos_sin_descuento'),
                func.sum(
                    DetallePedido.cantidad * (DetallePedido.precio_unitario - DetallePedido.precio_real)
                ).label('ahorro')
            ).join(DetallePedido, DetallePedido.producto_id == Producto.id)\
             .join(Pedido, Pedido.id == DetallePedido.pedido_id)\
             .filter(Pedido.estado_id != estado_cancelado.id)
            if desde_ini:
                q = q.filter(Pedido.fecha_pedido >= desde_ini)
            if hasta_fin:
                q = q.filter(Pedido.fecha_pedido <= hasta_fin)
            return q.group_by(Producto.id, Producto.nombre).order_by(
                func.sum(DetallePedido.cantidad * DetallePedido.precio_real).desc()
            ).all()

        resultados = _consulta(desde, hasta.replace(hour=23, minute=59, second=59) if hasta else None)

        productos = []
        tot_unidades = 0
        tot_unidades_desc = 0
        tot_ingresos_desc = 0.0
        tot_ingresos_full = 0.0
        tot_ahorro = 0.0
        for r in resultados:
            unidades = int(r.unidades or 0)
            unidades_desc = int(r.unidades_con_descuento or 0)
            ingresos_desc = float(r.ingresos_con_descuento or 0)
            ingresos_full = float(r.ingresos_sin_descuento or 0)
            ahorro = float(r.ahorro or 0)
            descuento_promedio = ((ingresos_full - ingresos_desc) / ingresos_full * 100) if ingresos_full > 0 else 0.0
            productos.append({
                'producto_id': r.id,
                'nombre': r.nombre,
                'unidades': unidades,
                'unidades_con_descuento': unidades_desc,
                'ingresos_con_descuento': round(ingresos_desc, 2),
                'ingresos_sin_descuento': round(ingresos_full, 2),
                'ahorro_total': round(ahorro, 2),
                'descuento_promedio': round(descuento_promedio, 2)
            })
            tot_unidades += unidades
            tot_unidades_desc += unidades_desc
            tot_ingresos_desc += ingresos_desc
            tot_ingresos_full += ingresos_full
            tot_ahorro += ahorro

        if limit and limit > 0:
            productos = productos[:limit]

        # Comparacion con el periodo anterior de la misma cantidad de dias.
        comparacion = None
        if desde and hasta:
            dias = (hasta.date() - desde.date()).days + 1
            hasta_anterior = desde - timedelta(days=1)
            desde_anterior = hasta_anterior - timedelta(days=dias - 1)
            anterior = _consulta(desde_anterior, hasta_anterior.replace(hour=23, minute=59, second=59))
            unidades_anterior = sum(int(r.unidades or 0) for r in anterior)
            ingresos_anterior = sum(float(r.ingresos_con_descuento or 0) for r in anterior)
            variacion_ingresos = ((tot_ingresos_desc - ingresos_anterior) / ingresos_anterior * 100) if ingresos_anterior > 0 else None
            variacion_unidades = ((tot_unidades - unidades_anterior) / unidades_anterior * 100) if unidades_anterior > 0 else None
            comparacion = {
                'desde': desde_anterior.strftime('%Y-%m-%d'),
                'hasta': hasta_anterior.strftime('%Y-%m-%d'),
                'unidades': unidades_anterior,
                'ingresos': round(ingresos_anterior, 2),
                'variacion_ingresos_porcentaje': round(variacion_ingresos, 2) if variacion_ingresos is not None else None,
                'variacion_unidades_porcentaje': round(variacion_unidades, 2) if variacion_unidades is not None else None
            }

        totales = {
            'unidades': tot_unidades,
            'unidades_con_descuento': tot_unidades_desc,
            'ingresos_con_descuento': round(tot_ingresos_desc, 2),
            'ingresos_sin_descuento': round(tot_ingresos_full, 2),
            'ahorro_total': round(tot_ahorro, 2),
            'descuento_promedio': round(
                ((tot_ingresos_full - tot_ingresos_desc) / tot_ingresos_full * 100) if tot_ingresos_full > 0 else 0.0, 2
            )
        }

        if excel:
            headers = ['Producto', 'Unidades', 'Unidades con descuento', 'Ingresos con descuento (Q)', 'Ingresos sin descuento (Q)', 'Ahorro (Q)', 'Descuento promedio (%)']
            rows = [
                [p['nombre'], p['unidades'], p['unidades_con_descuento'], p['ingresos_con_descuento'], p['ingresos_sin_descuento'], p['ahorro_total'], p['descuento_promedio']]
                for p in productos
            ]
            rows.append([])
            rows.append(['TOTAL', totales['unidades'], totales['unidades_con_descuento'], totales['ingresos_con_descuento'], totales['ingresos_sin_descuento'], totales['ahorro_total'], totales['descuento_promedio']])
            if comparacion:
                rows.append([])
                rows.append([f"Periodo anterior ({comparacion['desde']} al {comparacion['hasta']})", comparacion['unidades'], '', comparacion['ingresos'], '', '', ''])
                rows.append(['Variacion de ingresos (%)', comparacion['variacion_ingresos_porcentaje'] if comparacion['variacion_ingresos_porcentaje'] is not None else '', '', '', '', '', ''])
            return _generar_excel(
                'Ventas con Descuento', headers, rows,
                _nombre_archivo('ventas_con_descuento', desde, hasta),
                subtitulo=_subtitulo_periodo(desde, hasta)
            )

        return jsonify({
            'data': {
                'productos': productos,
                'totales': totales,
                'comparacion': comparacion,
                'desde': desde.strftime('%Y-%m-%d') if desde else None,
                'hasta': hasta.strftime('%Y-%m-%d') if hasta else None
            },
            'message': 'Ventas con descuento obtenidas'
        }), 200
    except Exception as e:
        return jsonify({'error': 'Error', 'message': str(e)}), 500
