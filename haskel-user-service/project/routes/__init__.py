from flask import Blueprint

# Create blueprint objects
auth_bp = Blueprint('auth', __name__)
user_bp = Blueprint('user', __name__)
admin_bp = Blueprint('admin', __name__)

# Import the route files to register the routes with the blueprints
from . import auth_routes, user_routes, admin_routes
