from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    return {'message': 'Register endpoint - to be implemented'}, 200


@auth_bp.route('/login', methods=['POST'])
def login():
    return {'message': 'Login endpoint - to be implemented'}, 200


@auth_bp.route('/me', methods=['GET'])
def me():
    return {'message': 'Current user endpoint - to be implemented'}, 200