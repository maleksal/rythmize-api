"""Authentication api routes."""
import flask_praetorian
from flask import make_response
from flask import jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from marshmallow import ValidationError
from rythmize.api.v1.views import api_views

from ....extensions import (confirm_email_by_link, db_manager, guard, mail, message,
                            send_email_verification)
from ....models.keys import SpotifyJsonWebToken, YoutubeJsonWebToken
from ....models.user import User, UserSchema

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
        load_data = user_schema.load(req)                   # Marshmallow validation.
    except ValidationError as errors:
        return jsonify(errors.messages), 401
                                                            # Validate if user is already 
    e = load_data["email"]                                  # created, then return response 401
    u = load_data["username"]                               # else create user.
    if not User.query.filter_by(email=e).one_or_none() and\
        not User.query.filter_by(username=u).one_or_none():
            user = User(**load_data)                        # Initiate User object, Validate data
            youtube_table = YoutubeJsonWebToken()           # and create tables then link them
            spotify_table = SpotifyJsonWebToken()           # to user.
            user.spotify_keys = spotify_table
            user.youtube_keys = youtube_table
            db_manager.add(user)
            db_manager.add(youtube_table)
            db_manager.add(spotify_table)
            db_manager.save()
            # Send email confirmation
            send_email_verification(user.email)
            return jsonify("Your account has been created!"), 200
    return jsonify("username or email already registred"), 401 

@api_views.route("auth/user/confirm_email/<token>", methods=["GET"])
def email_confirmation(token):
    """
    Confirm user email
    Returns:
        (200, msg) or (410, error)
    """
    email = confirm_email_by_link(token)
    if email:
        user = User.query.filter_by(email=email).first_or_404()     
        if not user.email_confirmed:
            user.email_confirmed = True
            db_manager.add(user)
            db_manager.save()
            return jsonify('Email confirmed'), 200
        return jsonify("Email already confirmed"), 410
    return jsonify('Token invalid or expired.'), 410

        

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
        response = {
                'access_token': guard.encode_jwt_token(user),
                'verified': user.email_confirmed
                }
        return jsonify(response), 200
    return jsonify("Please verify your credentials."), 401

@api_views.route('auth/user/current', methods=['GET'])
@flask_praetorian.auth_required
def user_details():
    """
    Gets user details like username email
    Returns:
        200, details or 401
    """
    user_id = flask_praetorian.current_user().id
    if user := User.query.get(user_id):
        details = {
            "username": user.username,
            "email": user.email
        }
        return jsonify(details), 200
    return 404

@api_views.route('auth/validate/jwt')
@flask_praetorian.auth_required
def validate_token():
    """
    Gets an auth token and responds back with
    200 if token is valid else 401.
    """
    return make_response(jsonify('valid token'), 200)