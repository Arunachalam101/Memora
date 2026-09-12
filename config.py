import os

# Get the base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    # Use absolute path for SQLite database
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'memora.sqlite')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
