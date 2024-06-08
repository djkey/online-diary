from flask import Blueprint, request, jsonify
from app import db
from app.models import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

bp = Blueprint('routes', __name__)


@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    new_user = User(
        name=data['name'],
        email=data['email'],
        login=data['login'],
        password=data['password']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(login=data['login']).first()
    if user and user.password == data['password']:
        access_token = create_access_token(identity={'login': user.login})
        return jsonify(access_token=access_token), 200
    return jsonify({'message': 'Invalid credentials'}), 401


@bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    user = User.query.filter_by(login=current_user['login']).first()
    return jsonify(name=user.name, email=user.email, login=user.login), 200
