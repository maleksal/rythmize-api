from flask import current_app
from flask_cors import CORS
from flask_mail import Mail, Message
from flask_marshmallow import Marshmallow
from flask_praetorian import Praetorian
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

# Setup sqlalchemy
db = SQLAlchemy()
# Setup marshmallow
ma = Marshmallow()
# Setup flask-praetorian
guard = Praetorian()
# Setup CORS
cors = CORS()
# Setup mail && msg
mail = Mail()
message = Message

# Setup email confirmation token

def send_email_verification(email):
    from flask import url_for
    """Send an email verification link to user email."""
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    token = serializer.dumps(email, salt='rythmize-email-confirmation')
    link = url_for('api_views.email_confirmation', token=token, _external=True)
    msg = message('Confirm email', recipients=[email])
    msg.body = f'Your confirmation link is {link}'
    mail.send(msg)

def confirm_email_by_link(token):
    """
    Confirms email by token
    Returns:
        email or None.
    """
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = serializer.loads(token, salt='rythmize-email-confirmation', max_age=3600)
    except (BadSignature, SignatureExpired):
        return None
    return email


class DatabaseManager(object):
    """Handels database operations like save, close.."""
    _session = db.session

    def add(self, obj=None):
        """add obj to database."""
        if obj:
            self._session.add(obj)

    def save(self):
        """Commits changes to database."""
        self._session.commit()

    def remove(self, obj):
        """Removes an object from database."""
        if obj:
            self._session.remove(obj)

    def close(self):
        """Closes database connection."""
        self._session.close()
    
    def get(self, cls, id=None, username=None):
        """Retrives an object from database."""
        if id:
            return cls.query.filter_by(id=id).one_or_none()
        return cls.query.filter_by(username=username).one_or_none()

# class instance
db_manager = DatabaseManager()
        