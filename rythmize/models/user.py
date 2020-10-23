"""
User Model

"""
from marshmallow import fields
from ..extensions import db
from sqlalchemy.orm import relationship, validates
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db, ma


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

    id = db.Column(
                db.Integer,
                primary_key=True)
    username = db.Column(
                db.String(255),
                nullable=False, unique=True)
    email = db.Column(
                db.String(255),
                nullable=False)
    email_confirmed = db.Column(
                        db.Boolean,
                        default=False)
    _password = db.Column(
                db.Text(),
                nullable=False)
    _spotify_keys = db.relationship("SpotifyJsonWebToken",
                                uselist=False, cascade="all, delete, delete-orphan", backref='user')
    _youtube_keys = db.relationship("YoutubeJsonWebToken",
                                uselist=False, cascade="all, delete, delete-orphan", backref='user') 

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
