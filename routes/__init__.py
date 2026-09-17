from routes.auth import auth_bp
from routes.products import products_bp
from routes.categorias import categorias_bp
from routes.carrito import carrito_bp
from routes.pedidos import pedidos_bp
from routes.favoritos import favoritos_bp
from routes.marcas import marcas_bp
from routes.resenas import resenas_bp

__all__ = ['auth_bp', 'products_bp', 'categorias_bp', 'carrito_bp', 'pedidos_bp', 'favoritos_bp', 'marcas_bp', 'resenas_bp']