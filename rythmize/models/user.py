"""
User Model

"""
from ..extensions import db, ma
from marshmallow import fields
from sqlalchemy import Column, String, Integer, Text, Boolean
from sqlalchemy.orm import relationship, validates
from werkzeug.security import generate_password_hash, check_password_hash


class FlaskApiSecurity(object):
    """
    FlaskApiSecurity class
    Used by flask-paertorian extension, Contains methods
    will be inherted by other classes and User model validation.
    
    """
    
    @property
    def rolenames(self):
        return []

    @classmethod
    def lookup(cls, username):
        return cls.query.filter_by(username=username).one_or_none()

    @classmethod
    def identify(cls, id):
        return cls.query.get(id)

    @property
    def identity(self):
        return self.id


class User(db.Model, FlaskApiSecurity):
    """User Class """
    __tablename__ = 'user'

    id = Column(
                Integer,
                primary_key=True)
    username = Column(
                String(255),
                nullable=False, unique=True)
    email = Column(
                String(255),
                nullable=False)
    email_confirmed = Column(
                        Boolean,
                        default=False)
    _password = Column(
                Text(),
                nullable=False)
    _spotify_keys = relationship("SpotifyJsonWebToken",
                                uselist=False, cascade="all, delete, delete-orphan")
    _youtube_keys = relationship("YoutubeJsonWebToken",
                                uselist=False, cascade="all, delete, delete-orphan") 

    @property
    def password(self):
        """Getter for password."""
        return self._password

    @password.setter
    def password(self, user_password):
        """Password protection."""
        self._password = generate_password_hash(user_password)

    def check_password(self, plaintext_pass):
        """Checks if plaintext_pass equals password."""
        return check_password_hash(self.password, plaintext_pass)

    def __repr__(self):
        """Represents a user class."""
        return self.username


class UserSchema(ma.Schema):
    """Marshmallow serializer/deserializer schema."""
    class Meta:
        model = User

    username = fields.String(required=True, uniqe=True)
    email = fields.Email(required=True)
    password = fields.String(required=True)