import os
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import config
from models.db import init_db
from models import db
from routes import auth_bp, products_bp, categorias_bp, carrito_bp, pedidos_bp, favoritos_bp, marcas_bp, resenas_bp, notificaciones_bp, reportes_bp

migrate = Migrate()
jwt = JWTManager()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # CORS configuration: allow explicit origins + regex for localhost any port
    cors_origins = app.config['CORS_ORIGINS']
    cors_regex = app.config.get('CORS_ORIGINS_REGEX')
    
    # Combine origins list with regex pattern - flask-cors accepts regex strings in origins list
    if cors_regex:
        origins = cors_origins + [cors_regex]
    else:
        origins = cors_origins
    
    CORS(app, origins=origins, supports_credentials=True, 
         allow_headers=['Content-Type', 'Authorization', 'X-Guest-Token'], 
         methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
         expose_headers=['Content-Type', 'Authorization'])

    init_db(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(categorias_bp)
    app.register_blueprint(carrito_bp)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(favoritos_bp)
    app.register_blueprint(marcas_bp)
    app.register_blueprint(resenas_bp)
    app.register_blueprint(notificaciones_bp)
    app.register_blueprint(reportes_bp)

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