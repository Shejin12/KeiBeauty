from flask import Blueprint

products_bp = Blueprint('products', __name__, url_prefix='/api/products')


@products_bp.route('', methods=['GET'])
def get_products():
    return {'message': 'List products endpoint - to be implemented', 'data': []}, 200


@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    return {'message': f'Get product {product_id} - to be implemented'}, 200


@products_bp.route('', methods=['POST'])
def create_product():
    return {'message': 'Create product endpoint - to be implemented'}, 201


@products_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    return {'message': f'Update product {product_id} - to be implemented'}, 200


@products_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    return {'message': f'Delete product {product_id} - to be implemented'}, 200