"""
Flask application configuration
"""
import os
import urllib.parse
from datetime import timedelta
from dotenv import load_dotenv

class Config:
    """Base configuration"""
    # Database Configuration
    load_dotenv()

    # Database Configuration
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'gym_qr_db')
    
    # URL encode credentials to handle special characters (like @) in passwords
    _user = urllib.parse.quote_plus(DB_USER)
    _pwd = urllib.parse.quote_plus(DB_PASSWORD)
    
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{_user}:{_pwd}@{DB_HOST}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_SECURE = False  # Set to True for HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_key')
    
    # Admin Credentials
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin@123')
    
    # QR Code Configuration
    QR_VERSION = 1  # QR code version
    QR_ERROR_CORRECTION = 'M'  # Error correction level
    
    # Application Settings
    ITEMS_PER_PAGE = 20


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Default to development
APP_CONFIG = DevelopmentConfig()
