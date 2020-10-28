"""clients auth routes."""
import flask_praetorian
from flask import jsonify, request
from rythmize.api.v1.views import api_views

from ....clients.spotify import SpotifyClient
from ....extensions import db_manager
from ....models.user import User, UserSchema

""" 
Not needed for now
@api_views.route('auth/connect/spotify/')
@flask_praetorian.auth_required
def generate_spotify_callback():
    user_id = flask_praetorian.current_user().id
    user = User.query.get(user_id)
    if user.spotify_keys.jwt_token:
        return jsonify("User already connected."), 410
    sclient = SpotifyClient(None, user)
    return jsonify({'auth_url': sclient.callback_uri_auth()}), 200
"""

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

    return jsonify('user is now connected'), 200


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

@api_views.route('clients/spotify/playlists/', methods=["GET"])
@flask_praetorian.auth_required
def get_user_playlists():
    user_id = flask_praetorian.current_user().id
    user = User.query.get(user_id)
    sclient = SpotifyClient(None, user)
    if data:= sclient.handle_auth():
        if type(data) == dict:
            user.spotify_keys.jwt_token = data["token"]
            user.spotify_keys.expires_in = data["expires"]
            db_manager.save()
        return jsonify(sclient.get_user_playlists()), 200
    return jsonify("user not authorized"), 401

@api_views.route('clients/spotify/playlists/<playlist_id>/tracks', methods=["GET"])
@flask_praetorian.auth_required
def get_playlist_tracks(playlist_id):
    """Get playlist tracks refrenced by playlist_id."""
    user_id = flask_praetorian.current_user().id
    user = User.query.get(user_id)
    sclient = SpotifyClient(None, user)
    if data:= sclient.handle_auth():
        if type(data) == dict:
            user.spotify_keys.jwt_token = data["token"]
            user.spotify_keys.expires_in = data["expires"]
            db_manager.save()
        return jsonify(sclient.get_playlist_tracks(playlist_id)), 200
    return jsonify("user not authorized"), 401


@api_views.route('clients/spotify/playlist/transfer', methods=["POST"])
@flask_praetorian.auth_required
def spotify_transfer():
    """adds songs to a playlist."""
    user_id = flask_praetorian.current_user().id
    user = User.query.get(user_id)
    # Extract from body
    req = request.get_json(force=True)
    playlist_name = req.get('playlist', None)
    songs = req.get('tracks', None)
    if playlist_name and songs and type(songs) == list:
        sclient = SpotifyClient(None, user)
        if data:= sclient.handle_auth():
            if type(data) == dict:
                user.spotify_keys.jwt_token = data["token"]
                user.spotify_keys.expires_in = data["expires"]
                db_manager.save()
            return jsonify(sclient.perform_transfer_tracks(playlist_name, songs)), 200
        return jsonify("user not authorized"), 401
    return {}, 400
