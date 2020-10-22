from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_praetorian import Praetorian
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask_mail import Mail, Message
from flask_cors import CORS

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
    msg = message('Confirm email', sender='malek.salem.14@gmail.com', recipients=[email]) 
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

