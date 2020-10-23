"""Flask config."""
import os
from os import environ
from dotenv import find_dotenv, load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

class Config:
    """Base config."""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Config for development only."""
    ENV = 'development'
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = environ.get('DEV_DATABASE_URI')
    JWT_ACCESS_LIFESPAN = {'days': 1}
    JWT_REFRESH_LIFESPAN = {'days': 30}
    MAIL_SERVER = environ.get("MAIL_SERVER")
    MAIL_USERNAME = environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = environ.get("MAIL_PASSWORD")
    MAIL_PORT=465
    MAIL_USE_SSL=True
    MAIL_USE_TLS=False
    #MAIL_SUPPRESS_SEND = False

class ProductionConfig(Config):
    """Config for profuction."""
    ENV = 'production'
    SQLALCHEMY_DATABASE_URI = environ.get('PROD_DATABASE_URI')
    JWT_ACCESS_LIFESPAN = {'hours': 24}
    JWT_REFRESH_LIFESPAN = {'days': 30}
    MAIL_SERVER = environ.get("MAIL_SERVER")
    MAIL_USERNAME = environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = environ.get("MAIL_PASSWORD")
    MAIL_PORT = environ.get("MAIL_PORT")
    MAIL_USE_SSL = environ.get("MAIL_SSL")
    MAIL_USE_TLS = environ.get("MAIL_TLS")

config = {
    "Production": ProductionConfig,
    "Development": DevelopmentConfig
}