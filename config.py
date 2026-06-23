import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables from .env
load_dotenv()

class Config:
    """Base configuration"""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
    WEBHOOK_SECRET = os.getenv('MGNT_WEBHOOK_SECRET', '')
    CORS_HEADERS = 'Content-Type'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///school_management.db'
    )
    WEBSITE_BACKEND_URL = os.getenv('WEBSITE_BACKEND_URL', 'http://localhost:5001')
    CORS_ORIGINS = os.getenv(
        'CORS_ORIGINS',
        'http://localhost:5173,http://localhost:5174,http://localhost:3000,http://localhost:8000,https://school-mgt-frontend-89tm.onrender.com,https://portal.hilltopjunior.com'
    ).split(',')


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # For testing, set JWT_SECRET_KEY via environment when running tests


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        None
    )


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
