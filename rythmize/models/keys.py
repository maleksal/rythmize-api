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
        # key = Fernet.generate_key()
        return Fernet(bytes(secret_key, 'utf-8'))
    
    def encrypt_data(self, value):
        """Handles Encryption."""
        security = self.load_configs()
        return security.encrypt(bytes(value, 'utf-8')).decode()

    def decrypt_data(self, value):
        """Handles Decryption."""
        security = self.load_configs()
        if value:
            return security.decrypt(bytes(value, 'utf-8')).decode()
        return None

class BaseClass(Security):
    """Base class contains common columns and methods."""

    jwt_token = db.Column(db.Text(), nullable=True)
    _refresh_token = db.Column(db.Text(), nullable=True)
    token_expires_on = db.Column(db.DateTime(), nullable=True)

    @property
    def refresh_token(self):
        """Return a decrypted refresh_token."""
        # decrypt from database
        return self.decrypt_data(self._refresh_token)

    @refresh_token.setter
    def refresh_token(self, value):
        """Encrypt refresh token before store into database."""
        # encrypt refresh_token
        self._refresh_token = self.encrypt_data(value)
    
    @property
    def expires_in(self):
        """Property getter."""
        return self.token_expires_on

    @expires_in.setter
    def expires_in(self, value):
        """Property setter, convert to datetime."""
        from datetime import datetime, timedelta
        self.token_expires_on = datetime.now() + timedelta(seconds=value),

    def __repr__(self):
        return self.jwt_token[0:10] 



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


