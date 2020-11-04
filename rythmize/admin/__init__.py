"""
Customize Admin Module

"""
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from ..extensions import db
from ..models.keys import SpotifyJsonWebToken, YoutubeJsonWebToken
from ..models.user import User


class CustomAdmin(ModelView):
    """
    CustomAdmin class:
    customize on change_model method inherted from ModelView
    """
    def on_model_change(self, form, user, is_created):
        if is_created:
            if user._spotify_keys or user._youtube_keys:
                raise Exception("User is already linked to table")
            #user.create_link_tables()
        return user

admin_settings = Admin()

# Add administrative views
admin_settings.add_view(CustomAdmin(User, db.session))
admin_settings.add_view(ModelView(YoutubeJsonWebToken, db.session))
admin_settings.add_view(ModelView(SpotifyJsonWebToken, db.session))
