import os


class Config:
    """Base configuration that reads from Replit's secrets."""
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # This was missing before
    PAYMENT_SERVICE_URL = os.environ.get('PAYMENT_SERVICE_URL')

    SQLALCHEMY_DATABASE_URI = 'sqlite:///haskel.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
