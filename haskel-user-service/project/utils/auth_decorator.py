from functools import wraps
from flask import request, jsonify, current_app
import jwt
import requests

from project.models.user import User


def token_required(f):
    """Decorator to protect routes with JWT authentication."""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token,
                              current_app.config['SECRET_KEY'],
                              algorithms=['HS256'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
            if not current_user or not current_user.is_active:
                return jsonify({'message':
                                'User not found or deactivated.'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


def subscription_required(f):
    """
    Decorator to check for an active subscription.
    This makes a call to the Payment & Subscription Service.
    """

    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if current_user.user_type.value == 'independent':
            try:
                payment_service_url = f"{current_app.config['PAYMENT_SERVICE_URL']}/status/{current_user.public_id}"
                print(f"DEBUG: Calling Payment Service at URL: {payment_service_url}")                
                response = requests.get(payment_service_url, timeout=5)
                response.raise_for_status()

                subscription_data = response.json()
                if subscription_data.get('status') != 'active':
                        return jsonify({
                        'message':
                        'An active subscription is required to access this feature.'
                    }), 403

            except requests.exceptions.RequestException as e:
                print(f"Could not connect to Payment Service: {e}")
                return jsonify({
                    'message':
                    'Could not verify subscription status. Please try again later.'
                }), 503

        return f(current_user, *args, **kwargs)

    return decorated


def roles_required(*roles):
    """Decorator to enforce role-based access control (RBAC)."""

    def wrapper(f):

        @wraps(f)
        @token_required
        def decorated_function(current_user, *args, **kwargs):
            if current_user.role.value not in roles:
                return jsonify({
                    'message':
                    'You do not have permission to perform this action.'
                }), 403
            return f(current_user, *args, **kwargs)

        return decorated_function

    return wrapper
