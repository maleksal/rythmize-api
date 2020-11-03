"""Authentication api routes."""
import flask_praetorian
from flask import jsonify, make_response, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from marshmallow import ValidationError
from rythmize.api.v1.views import api_views

from ....extensions import (confirm_email_by_link, db_manager, guard, mail,
                            message, send_email_verification)
from ....models.keys import SpotifyJsonWebToken, YoutubeJsonWebToken
from ....models.user import User, UserSchema


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
        # Marshmallow validation.
        load_data = user_schema.load(req)
    except ValidationError as errors:
        return jsonify(errors.messages), 401

    e = load_data["email"]
    u = load_data["username"]
    if not User.query.filter_by(email=e).one_or_none() and\
            not User.query.filter_by(username=u).one_or_none():
        # Initiate User object, Validate data
        user = User(**load_data)
        # and create tables then link them
        youtube_table = YoutubeJsonWebToken()
        spotify_table = SpotifyJsonWebToken()
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


@api_views.route('auth/validate/jwt')
@flask_praetorian.auth_required
def validate_token():
    """
    Gets an auth token and responds back with
    200 if token is valid else 401.
    """
    return make_response(jsonify('valid token'), 200)
