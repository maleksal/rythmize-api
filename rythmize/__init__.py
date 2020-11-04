"""
Create flask application.

"""
import os

from flask import Flask

from .admin import admin_settings
from .api.v1.views import api_views
from .extensions import cors, db, guard, ma, mail
from .models.user import User


def create_app(config_env):
    """Initiate app using Flask Factory Pattern."""
    app = Flask(__name__)
    app.config.from_object(config_env)
    # Initialize extentions
    db.init_app(app)            # Database
    ma.init_app(app)            # Serilizer && Deserializer extension
    guard.init_app(app, User)   # Flask-praetorian
    cors.init_app(app)          # Flask-cors
    mail.init_app(app)          # Flask-Mail
    # setup admin panel
    admin_settings.init_app(app)
    admin_settings.name = 'rythmize-panel'
    admin_settings.template_mode = 'bootstrap3'
    # register routes
    app.register_blueprint(api_views)

    return app

