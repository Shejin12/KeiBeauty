import os
from flask import Flask
from flask_cors import CORS
from config import config
from models.db import init_db
from routes import auth_bp, products_bp


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)

    init_db(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)

    @app.route('/health')
    def health():
        return {'status': 'ok', 'service': 'KeiBeauty API'}, 200

    @app.route('/')
    def index():
        return {
            'name': 'KeiBeauty API',
            'version': '1.0.0',
            'docs': '/health'
        }, 200

    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config.get('DEBUG', False))