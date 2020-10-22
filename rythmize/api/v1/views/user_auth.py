"""Authentication api routes."""
import flask_praetorian
from flask import jsonify
from flask import request
from marshmallow import ValidationError
from itsdangerous import BadSignature, SignatureExpired
from ....extensions import db, guard, mail, message, send_email_verification, confirm_email_by_link
from ....models.user import User, UserSchema
from ....models.keys import YoutubeJsonWebToken, SpotifyJsonWebToken
from rythmize.api.v1.views import api_views

from itsdangerous import URLSafeTimedSerializer

#ts = URLSafeTimedSerializer("he")

@api_views.route('auth/user/register', methods=['POST'])
def user_register():
    """
    Registers a user in by parsing a POST request.
    Fields:

    Returns:
            (200, msg) or (401, errors)

    """

    req = request.get_json(force=True)
    user_schema = UserSchema()
    
    try:
        load_data = user_schema.load(req)               # Marshmallow validation.
    except ValidationError as errors:
        return jsonify(errors.messages), 401
                                                        # Validate if user is already 
    e = load_data["email"]                              # created, then return response 401
    u = load_data["username"]                           # else create user.
    if User.query.filter_by(email=e).one_or_none() or\
        User.query.filter_by(username=u).one_or_none():
        return jsonify("User is already created."), 401 

    user = User(**load_data)                # Initiate User object, Validate data
    youtube_table = YoutubeJsonWebToken()   # and create tables then link them
    spotify_table = SpotifyJsonWebToken()   # to user.
    user.spotify_keys = spotify_table
    user.youtube_keys = youtube_table
    db.session.add(user)
    db.session.add(youtube_table)
    db.session.add(spotify_table)
    db.session.commit()
    # Send email confirmation
    send_email_verification(user.email)
    return jsonify("Your account has been created!"), 200

@api_views.route("auth/user/confirm_email/<token>", methods=["GET"])
def email_confirmation(token):
    """
    Confirm user email
    
    Returns:
        (200, msg) or (410, error)

    """
    email = confirm_email_by_link(token)
    if not email:
        return jsonify('Token invalid or expired.'), 410
    else:
        user = User.query.filter_by(email=email).first_or_404()     
        if user.email_confirmed:
            return jsonify("Email already confirmed"), 410
        user.email_confirmed = True
        db.session.add(user)
        db.session.commit()
    return jsonify('Email confirmed'), 200
        

@api_views.route('auth/user/login', methods=['POST'])
def user_login():
    """
    Logs a user in by parsing a POST request containing
    user credentials and issuing a JWT token.
    
    Returns:
        200, jwt_token or 401


    """
    req = request.get_json(force=True)
    username = req.get('username', None)
    password = req.get('password', None)
    user = User.query.filter_by(username=username).one_or_none()
    if user and user.check_password(password):
        ret = {'access_token': guard.encode_jwt_token(user)}
        return (jsonify(ret), 200)
    return jsonify("Please verify your credentials."), 401


