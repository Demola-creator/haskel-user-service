import os
import sys
import enum
import uuid
import datetime
from functools import wraps
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from passlib.hash import pbkdf2_sha256 as sha256
import jwt
from dotenv import load_dotenv

# --- 1. App & Config Setup ---
load_dotenv() 
app = Flask(__name__)

app.config['SECRET_KEY'] = 'a-very-secret-and-random-key-for-development'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///haskel_user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- 2. Database Initialization ---
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# --- 3. Database Models ---
class UserRole(enum.Enum):
    STUDENT = 'student'
    LECTURER = 'lecturer'
    PARENT = 'parent'
    ADMIN = 'admin'

class UserType(enum.Enum):
    INSTITUTIONAL = 'institutional'
    INDEPENDENT = 'independent'

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100))
    role = db.Column(db.Enum(UserRole), nullable=False)
    user_type = db.Column(db.Enum(UserType), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    def set_password(self, password): self.password_hash = sha256.hash(password)
    def check_password(self, password): return sha256.verify(password, self.password_hash)
    def to_dict(self): return {'public_id': self.public_id, 'username': self.username, 'email': self.email, 'full_name': self.full_name, 'role': self.role.value, 'user_type': self.user_type.value, 'is_active': self.is_active}

# --- 4. Security Decorator ---
# THIS IS THE FUNCTION THAT WAS MISSING
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# --- 5. API Routes ---
@app.route("/api/v1/auth/register", methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first(): return jsonify({'message': 'User already exists.'}), 409
    new_user = User(public_id=str(uuid.uuid4()), username=data.get('username'), email=data.get('email'), full_name=data.get('full_name'), role=UserRole(data.get('role', 'student')), user_type=UserType(data.get('user_type', 'independent')))
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user created successfully!'}), 201

@app.route("/api/v1/auth/login", methods=['POST'])
def login():
    auth = request.get_json()
    user = User.query.filter_by(email=auth['email']).first()
    if not user or not user.check_password(auth['password']): return jsonify({'message': 'Login failed.'}), 401
    token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)}, app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token})

@app.route("/api/v1/users/profile", methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify(current_user.to_dict())

# --- 6. Main Execution Block ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)