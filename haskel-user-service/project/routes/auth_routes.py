from flask import request, jsonify, current_app
from . import auth_bp
import jwt
import datetime
import uuid

from project import db
from project.models.user import User, UserRole, UserType


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    FR01: Handles user registration for all roles and types.
    GOAL: Intuitive UX for a smooth signup process.
    """
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password are required.'}), 400

    if User.query.filter_by(
            email=data['email']).first() or User.query.filter_by(
                username=data.get('username')).first():
        return jsonify(
            {'message':
             'User with this email or username already exists.'}), 409

    try:
        new_user = User(
            public_id=str(uuid.uuid4()),
            username=data.get('username'),
            email=data['email'],
            full_name=data.get('full_name'),
            role=UserRole(data.get('role', 'student')),  # Default to student
            user_type=UserType(data.get(
                'user_type', 'independent'))  # Default to independent
        )
        new_user.set_password(data['password'])

        db.session.add(new_user)
        db.session.commit()
    except ValueError as e:
        return jsonify({'message':
                        f'Invalid role or user_type provided. {e}'}), 400
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'message':
                        'An error occurred during registration.'}), 500

    return jsonify({'message': 'New user created successfully!'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    FR02: Handles user login and JWT generation.
    """
    auth = request.get_json()

    if not auth or not auth.get('email') or not auth.get('password'):
        return jsonify({
            'message': 'Could not verify',
            'WWW-Authenticate': 'Basic realm="Login required!"'
        }), 401

    user = User.query.filter_by(email=auth['email']).first()

    if not user or not user.is_active:
        return jsonify(
            {'message': 'User not found or account is deactivated.'}), 401

    if user.check_password(auth['password']):
        token = jwt.encode(
            {
                'public_id': user.public_id,
                'role': user.role.value,
                'exp': datetime.datetime.utcnow() +
                datetime.timedelta(hours=24)  # Token expires in 24 hours
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256')

        return jsonify({'token': token, 'user': user.to_dict()})

    return jsonify({'message': 'Could not verify. Wrong password.'}), 401
