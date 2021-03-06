"""clients auth routes."""
import flask_praetorian
from flask import jsonify, request
from rythmize.api.v1.views import api_views

from ....clients.spotify import SpotifyClient
from ....extensions import db_manager
from ....models.user import User


@api_views.route('clients/spotify/playlists/', methods=["GET"])
@flask_praetorian.auth_required
def get_user_playlists():
    user_id = flask_praetorian.current_user().id  # extract user id from jwt token
    user = User.query.get(user_id)
    sclient = SpotifyClient(None, user)
    if sclient.handle_auth():
        # if user authenticated
        return jsonify(sclient.get_user_playlists()), 200
    return jsonify("user not authorized"), 401


@api_views.route('clients/spotify/playlists/<playlist_id>/tracks', methods=["GET"])
@flask_praetorian.auth_required
def get_playlist_tracks(playlist_id):
    """Get playlist tracks refrenced by playlist_id."""
    user_id = flask_praetorian.current_user().id
    user = User.query.get(user_id)
    sclient = SpotifyClient(None, user)
    if sclient.handle_auth():
        # if user authenticated
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
        if sclient.handle_auth():
            return jsonify(sclient.perform_transfer_tracks(playlist_name, songs)), 200
        return jsonify("user not authorized"), 401
    return {}, 400
