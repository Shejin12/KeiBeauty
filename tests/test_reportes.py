import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from routes.reportes import _subtitulo_periodo, _nombre_archivo, _nombre_pdf, _parse_fecha
from datetime import datetime

def test_parse_fecha():
    assert _parse_fecha('2026-01-31') == datetime(2026, 1, 31)
    assert _parse_fecha('no-fecha') is None
    assert _parse_fecha(None) is None

def test_subtitulo_periodo():
    d = datetime(2026, 1, 1)
    h = datetime(2026, 1, 31)
    assert 'Periodo' in _subtitulo_periodo(d, h)
    assert _subtitulo_periodo(None, None) == 'Periodo: todo el historial'

def test_nombre_archivo():
    d = datetime(2026, 1, 1)
    h = datetime(2026, 1, 31)
    assert _nombre_archivo('ventas_totales', d, h).endswith('.xlsx')
    assert _nombre_pdf('ventas_totales', d, h).endswith('.pdf')
