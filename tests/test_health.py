import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app import create_app

def test_health():
    app = create_app('testing')
    c = app.test_client()
    r = c.get('/health')
    assert r.status_code == 200
    assert r.get_json()['status'] == 'ok'
