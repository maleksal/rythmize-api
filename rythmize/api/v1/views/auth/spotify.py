"""
Spotify Auth module.
"""
import flask_praetorian
from flask import jsonify, request, redirect
from rythmize.api.v1.views import api_views

from .....clients.spotify import SpotifyClient
from .....extensions import db_manager
from .....models.user import User


@api_views.route('auth/connect/spotify/callback/')
def authenticate_callback():
    # get params
    user_id = request.args.get('state')
    user = User.query.get(user_id)
    if 'error' in request.args.keys():
        return jsonify("Failed to authenticate."), 401
    code = request.args.get('code')
    sclient = SpotifyClient(code, user)
    data = sclient.handle_auth()
    # update user linked table
    spotify_table = user.spotify_keys
    spotify_table.jwt_token = data["token"]
    spotify_table.refresh_token = data["refresh_token"]
    spotify_table.expires_in = data["expires"]
    db_manager.save()

    return redirect("https://rythmize-frontend.herokuapp.com/dashboard")


@api_views.route('auth/connect/spotify/status', methods=["GET"])
@flask_praetorian.auth_required
def spotify_status():
    user_id = flask_praetorian.current_user().id
    user = User.query.get(user_id)
    sclient = SpotifyClient(None, user)
    if auth := sclient.handle_auth():
        if type(auth) == dict:
            user.spotify_keys.jwt_token = auth["token"]
            user.spotify_keys.expires_in = auth["expires"]
            db_manager.save()
        return jsonify('User connected'), 200
    return jsonify({"url": sclient.callback_uri_auth()}), 401
