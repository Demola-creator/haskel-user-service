from project import db
from passlib.hash import pbkdf2_sha256 as sha256
import enum


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
    profile_picture_url = db.Column(db.String(255))
    role = db.Column(db.Enum(UserRole), nullable=False)
    user_type = db.Column(db.Enum(UserType), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def set_password(self, password):
        self.password_hash = sha256.hash(password)

    def check_password(self, password):
        return sha256.verify(password, self.password_hash)

    def to_dict(self):
        return {
            'public_id': self.public_id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'profile_picture_url': self.profile_picture_url,
            'role': self.role.value,
            'user_type': self.user_type.value,
            'is_active': self.is_active
        }
