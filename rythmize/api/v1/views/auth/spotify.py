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
    if 'error' not in request.args.keys():
        code = request.args.get('code')
        sclient = SpotifyClient(code, user)
        if sclient.handle_auth():
            # if user authenticated, then redirect
            return redirect("https://rythmize-frontend.herokuapp.com/dashboard")
    return jsonify("Failed to authenticate."), 401


@api_views.route('auth/connect/spotify/status', methods=["GET"])
@flask_praetorian.auth_required
def spotify_status():
    user_id = flask_praetorian.current_user().id
    user = User.query.get(user_id)
    sclient = SpotifyClient(None, user)
    if sclient.handle_auth():
        # if user is authenticated
        return jsonify('User connected'), 200
    return jsonify({"url": sclient.callback_uri_auth()}), 401
