from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import admin_required
from models import db, Producto

products_bp = Blueprint('products', __name__, url_prefix='/api/products')


@products_bp.route('', methods=['GET'])
def get_products():
    return {'message': 'List products endpoint - to be implemented', 'data': []}, 200


@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    return {'message': f'Get product {product_id} - to be implemented'}, 200


@products_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_product():
    return {'message': 'Create product endpoint - admin only'}, 201


@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_product(product_id):
    return {'message': f'Update product {product_id} - admin only'}, 200


@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_product(product_id):
    return {'message': f'Delete product {product_id} - admin only'}, 200


@products_bp.route('/admin-test', methods=['GET'])
@jwt_required()
@admin_required
def admin_test():
    return jsonify({'mensaje': 'Acceso de administrador concedido.'}), 200