from flask import request, jsonify
from . import user_bp

from project.utils.auth_decorator import subscription_required


@user_bp.route('/profile', methods=['GET'])
@subscription_required
def get_profile(current_user):
    """FR03: Get user's own profile."""
    return jsonify(current_user.to_dict())


@user_bp.route('/profile', methods=['PUT'])
@subscription_required
def update_profile(current_user):
    """FR03: Update user's own profile."""
    data = request.get_json()

    current_user.full_name = data.get('full_name', current_user.full_name)
    # Add other updatable fields here

    from project import db
    db.session.commit()

    return jsonify({
        'message': 'Profile updated successfully!',
        'user': current_user.to_dict()
    })


# Placeholder for profile picture upload
@user_bp.route('/profile/picture', methods=['POST'])
@subscription_required
def upload_profile_picture(current_user):
    # File upload logic would go here. This often involves saving the file
    # to a cloud storage service (like AWS S3) and storing the URL
    # in the user's profile.
    return jsonify(
        {'message':
         'Profile picture upload endpoint not yet implemented.'}), 501
