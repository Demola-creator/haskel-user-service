from flask import request, jsonify
from . import admin_bp  # Corrected from admin_misc_bp
import uuid

from project.models.user import User, UserRole
from project.utils.auth_decorator import roles_required
from project import db


@admin_bp.route('/users', methods=['GET'])  # Corrected
@roles_required('admin')
def get_all_users(current_user):
    """FR05: Admin gets a list of all users."""
    users = User.query.all()
    output = [user.to_dict() for user in users]
    return jsonify({'users': output})


@admin_bp.route('/users', methods=['POST'])  # Corrected
@roles_required('admin')
def create_user_by_admin(current_user):
    """FR05: Admin creates a new user."""
    data = request.get_json()

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message':
                        'User with this email already exists.'}), 409

    new_user = User(public_id=str(uuid.uuid4()),
                    username=data.get('username'),
                    email=data['email'],
                    full_name=data.get('full_name'),
                    role=UserRole(data.get('role', 'student')),
                    user_type=data.get('user_type', 'institutional'))
    new_user.set_password(data['password'])

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'message': 'User created by admin successfully!',
        'user': new_user.to_dict()
    }), 201


@admin_bp.route('/users/<public_id>', methods=['PUT'])  # Corrected
@roles_required('admin')
def modify_user(current_user, public_id):
    """FR05: Admin modifies a user account (e.g., deactivate)."""
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()
    user.is_active = data.get('is_active', user.is_active)

    if data.get('role'):
        user.role = UserRole(data.get('role'))

    db.session.commit()

    return jsonify({'message': 'User has been updated.'})


@admin_bp.route('/users/<public_id>/permissions', methods=['PUT'])  # Corrected
@roles_required('admin')
def manage_permissions(current_user, public_id):
    """FR05: Admin manages permissions (by changing role)."""
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()
    if 'role' in data:
        try:
            user.role = UserRole(data['role'])
            db.session.commit()
            return jsonify(
                {'message': f'User role updated to {data["role"]}.'})
        except ValueError:
            return jsonify({'message': 'Invalid role specified.'}), 400

    return jsonify({'message': 'No role change specified.'}), 400
