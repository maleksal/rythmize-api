"""
JwtKeys Model
stores information about youtube/spotify web tokens

"""
from cryptography.fernet import Fernet
from flask import current_app
from sqlalchemy.orm import relationship

from ..extensions import db


class Security(object):
    """Handles encryption && decryption."""
    
    def load_configs(self):
        """Class constructor."""
        secret_key = current_app.secret_key
        key = Fernet.generate_key()
        return Fernet(bytes(secret_key, 'utf-8'))
    
    def encrypt_data(self, value):
        """Handles Encryption."""
        security = self.load_configs()
        return security.encrypt(bytes(value, 'utf-8'))

    def decrypt_data(self, value):
        """Handles Decryption."""
        security = self.load_configs()
        return security.decrypt(value).decode('utf-8')


class BaseClass(Security):
    """Base class contains common columns and methods."""

    jwt_token = db.Column(db.String(50), nullable=True)
    _refresh_token = db.Column(db.String(50), nullable=True)
    expires_on = db.Column(db.String(50), nullable=True)

    @property
    def refresh_token(self):
        """Return a decrypted refresh_token."""
        # decrypt from database
        if type(self._refresh_token) == bytes:
            return self.decrypt_data(self._refresh_token)
        return None

    @refresh_token.setter
    def refresh_token(self, value):
        """Encrypt refresh token before store into database."""
        # encrypt refresh_token
        self._refresh_token = self.encrypt_data(value)


class YoutubeJsonWebToken(db.Model, BaseClass):
    """YoutubeJsonWebToken class."""
    
    __tablename__ = 'youtube_jwt'
    id = db.Column(db.Integer,
                primary_key=True)
    user_id = db.Column(db.Integer,
                     db.ForeignKey('user.id'))


class SpotifyJsonWebToken(db.Model, BaseClass):
    """SpotifyJsonWebToken class."""
    
    __tablename__ = 'spotify_jwt'
    id = db.Column(db.Integer,
                primary_key=True)
    user_id = db.Column(db.Integer,
                     db.ForeignKey('user.id'))


