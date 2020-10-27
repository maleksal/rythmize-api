"""
API clients module
"""
import base64
import json
from datetime import date, datetime, time, timedelta
from os import environ
from urllib.parse import urlencode

import requests


class SpotifyClientAuth(object):
    client_id = environ.get('CLIENT_ID')
    client_secret = environ.get('CLIENT_SECRET')
    redirect_uri = environ.get('CLIENT_REDIRECT_URI')
    tokenapi_endpoint = 'https://accounts.spotify.com/api/token'
    authorize_endpoint = 'https://accounts.spotify.com/authorize'
    
    def __init__(self, code, user_object):
        """
        Keys_object: <user_object>.jwt_keys
        """
        self.user_id = user_object.id
        keys_object = user_object.spotify_keys
        self.token = keys_object.jwt_token
        self.refresh_token = keys_object.refresh_token
        self.expires = keys_object.expires_in
        self.code = code

    def client_credentials(self):
        """Returns a base64 encoded string."""
        client_id = self.client_id
        client_secret = self.client_secret
        if client_secret == None or client_id == None:
            raise Exception("Missing client_id and client_secret")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()
    
    def get_token_headers(self):
        """requests a new token using refresh_token"""
        client_creds_b64 = self.client_credentials()
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {client_creds_b64}'
            }

    def callback_uri_auth(self):
        """Returns a url for auth."""
        params = {
        "client_id": self.client_id,
        'response_type': 'code',
        'scope': 'playlist-modify-private playlist-read-collaborative playlist-read-private playlist-modify-public',
        'state': self.user_id,
        'redirect_uri': self.redirect_uri,
        }
        return f'{self.authorize_endpoint}/?{urlencode(params)}'
        
    def get_access_token(self, code):
        """Requests a access token."""
        headers = self.get_token_headers()
        data = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri
        }
        return requests.post(self.tokenapi_endpoint, data=data, headers=headers)
    
    def refresh_access_token(self):
        """refresh access token"""
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        headers = {
            'Authorization': f'Basic {self.client_credentials()}'
        }
        return requests.post(self.tokenapi_endpoint, data=data, headers=headers)

    def handle_auth(self):
        def assign_values(response):
            if response.status_code not in range(200, 299):
                return False
            data = response.json()
            self.token = data['access_token']
            self.expires = data['expires_in']
            if 'refresh_token' in data.keys():
                self.refresh_token = data['refresh_token']
            return {'token': self.token, 'refresh_token': self.refresh_token, 'expires': self.expires}

        if self.code:
            r = self.get_access_token(self.code)
            return assign_values(r)
        if not self.code and (not self.token and self.refresh_token):
            return False
        if not self.code and self.expires < datetime.now():
            r = self.refresh_access_token()
            return assign_values(r)
        return True

    def get_resource_header(self):
        """Generates header."""
        return {
            'Content-Type': 'application/json',
            "Authorization": f"Bearer {self.token}"
            }

    def get_user_id(self):
        headers = self.get_resource_header()
        response = requests.get('https://api.spotify.com/v1/me/', headers=headers)
        if response.status_code in range(200, 299):
            r = response.json()
            return r['id']
        return None


class SpotifyClientPlaylist(SpotifyClientAuth):
    """SpotifyClientPlaylist, hHandles CRUD operations for playlist."""
    default_params = {"offset": 0}

    def get_user_playlists(self):
        """Get current user playlists."""
        endpoint = 'https://api.spotify.com/v1/me/playlists'
        headers = self.get_resource_header()
        response = requests.get(endpoint, headers=headers, params=self.default_params)
        if response.status_code in range(200, 299):
            r = response.json()
            return r
        return None

    def get_playlist_info(self):
        """Extracts playlist {name: id} from playlist data."""
        data = self.get_user_playlists()
        return [{pl['name']:pl['id']} for pl in data['items']]
    
    def get_playlist_tracks(self, playlist_id=None):
        """Retrieves a playlist based on it's id."""
        endpoint = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        headers = self.get_resource_header()
        response = requests.get(endpoint, headers=headers, params=self.default_params)
        if response.status_code in range(200, 299):
            r = response.json()
            return r
        return None

    def create_playlist(self, name, description=None, public=False):
        """Create A New Playlist"""
        spotify_id = self.get_user_id()
        endpoint = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_id)
        headers = self.get_resource_header()
        request_body = json.dumps({"name": name, "description": description, "public": public})
        # create playlist
        response = requests.post(endpoint, data=request_body, headers=headers)
        if response.status_code in range(200, 299):
            r = response.json()
            # playlist id
            return r["id"]
        return None


class SpotifyClientTrack(SpotifyClientAuth):
    """CRUD operation for track."""

    def get_track_uri(self, song_name, artist):
        """Search For the Song"""
        query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=20".format(
            song_name,
            artist
        )
        response = requests.get(query, headers= self.get_resource_header())
        if response.status_code in range(200, 299):
            r = response.json()
            songs = r["tracks"]["items"]
            # only use the first song
            uri = songs[0]["uri"]
            return uri
        return None
    
    def get_tracks_uri(self, tracks):
        """
        Params:
            tracks: list of items.
        Returns:
            list of track uris or None.
        """
        return [t['track']['uri'] for t in tracks['items']] 

class SpotifyClient(SpotifyClientPlaylist, SpotifyClientTrack):
    
    def perform_transfer_tracks(self, playlist_name, songs=[]):
        """
        Search if playlist exists || create, then add songs to the supplied playlist.
        Params:
            playlist_name: str-> name of the playlist to be searched or created.
            songs: List of dictionary's with {track: song_name, artist: artist_name}
        Returns:
            the snapshot_id of created playlist or None
        """
        def check_for_playlist(playlist):
            '''takes a list of strings: playlist names.'''
            found_id = None
            current_user_playlists = self.get_playlist_info()
            for _dic in current_user_playlists:
                for name, _id in _dic.items():
                    if name == playlist_name:
                        print('playlist found')
                        found_id = _id
            return found_id

        
        uris = []
        # Check for playlist
        playlist_id = check_for_playlist(playlist_name)
        if not playlist_id:
            playlist_id = self.create_playlist(
                playlist_name,
                description='playlist created by rythmize.'
            )
        track_uris = self.get_tracks_uri(self.get_playlist_tracks(playlist_id))
        for song in songs:
            track_name, artist= song['track'], song['artist']
            if track_name and artist:
                uri = self.get_track_uri(track_name, artist)
                if uri and uri not in track_uris:
                    uris.append(uri)
        endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        headers = self.get_resource_header()
        request_data = json.dumps(uris)
        response = requests.post(endpoint, headers=headers, data=request_data)
        if response.status_code in range(200, 299):
            r = response.json()
            return r
        return None


        