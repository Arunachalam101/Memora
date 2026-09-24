import os

# Get the base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database location. Override with the DATABASE_URL environment variable
    # (the test-suite uses this so tests never touch the real database).
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"sqlite:///{os.path.join(BASE_DIR, 'data', 'memora.sqlite')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True