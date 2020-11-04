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
        self.__user = user_object
        self.user_id = self.__user.id
        keys_object = self.__user.spotify_keys
        self.token = keys_object.jwt_token
        self.refresh_token = keys_object.refresh_token
        self.expires = keys_object.expires_in
        self.code = code

    def update_database(self):
        """updates user in database with new values."""
        from ..extensions import db_manager
        
        prepare_values = {
                'jwt_token': self.token,
                'refresh_token': self.refresh_token,
                'expires_in': self.expires}
        db_manager.update_key_table(self.user_id, **prepare_values)

    def client_credentials(self):
        """Returns a base64 encoded string."""
        client_id = self.client_id
        client_secret = self.client_secret
        if client_secret is not None or client_id is not None:
            client_creds = f"{client_id}:{client_secret}"
            client_creds_b64 = base64.b64encode(client_creds.encode())
            return client_creds_b64.decode()
        raise Exception("Missing client_id and client_secret")

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
        """refresh an access token"""
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
            }
        headers = {'Authorization': f'Basic {self.client_credentials()}'}
        return requests.post(self.tokenapi_endpoint, data=data, headers=headers)

    def handle_auth(self):
        """
        Handles authentication with spotify, checks for:
        - user token is valid, else reuest new token
        - user dont have token, then redirect user to authenticate.
        Returns:
            Boolean: True if user is authenticated, else False
        """
        def validate_and_assign_values(response):
            """assigns values to variables."""
            if response.status_code in range(200, 299):
                data = response.json()
                self.token = data['access_token']
                self.expires = data['expires_in']
                if 'refresh_token' in data.keys():
                    # if refresh token provided in resonse then assigned to it's attr,
                    # this function works for getting an access_token and refreshing token.
                    self.refresh_token = data['refresh_token']
                return True
            return False
        # when code is not None then will get an access token
        if self.code and validate_and_assign_values(self.get_access_token(self.code)):
            self.update_database()
            return True
        if not self.code:
            # When code is None then will check: 
            if self.token and self.refresh_token and self.expires:
                # if no token is present then return false. 
                if self.expires < datetime.now():
                    # if token is expired then request new one.
                    response = self.refresh_access_token()
                    if validate_and_assign_values(response):
                        self.update_database()
                        return True
                return True
        return False

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
            # if valid response, return id
            return response.json()['id']
        return None


class SpotifyClientPlaylist(SpotifyClientAuth):
    """SpotifyClientPlaylist, Handles CRUD operations for playlist."""
    default_params = {"offset": 0} # nedeed for requests with spotify api

    def get_user_playlists(self):
        """Get current user playlists."""
        endpoint = 'https://api.spotify.com/v1/me/playlists'
        headers = self.get_resource_header()
        response = requests.get(endpoint, headers=headers, params=self.default_params)
        if response.status_code in range(200, 299):
            # if valid request and valid json then go here.
            response_data = []
            for data in response.json()['items']:
                # iterate over json response and add playlist
                # id, name, nnumber of tracks, and service to a list.
                response_data.append({data['id']:{'title': data['name'], 'tracks': data['tracks']['total'], 'service':'spotify'}})
            return response_data
        return None

    def get_playlist_info(self):
        """Extracts playlist {title: id} from playlist data."""
        data = self.get_user_playlists() # gets data of playlist, from methode above.
        result = []
        for elements in data:
            # elements is a dictionary
            for playlist_id, playlist_data in elements.items():
                result.append({playlist_data['title']:playlist_id})
        return result
    
    def get_playlist_tracks(self, playlist_id=None):
        """
        Retrieves tracks of  playlist based on  playlist_id.
        Returns:
                id:       Track id 
                title:    Track name,   
                duration: Track duration in minutes
                album:    Associated album of track
                artist:   The artist of track
                service:  Spotify or Youtube
                uri:      Track uri 
        """
        endpoint = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        headers = self.get_resource_header()
        response = requests.get(endpoint, headers=headers, params=self.default_params)
        if response.status_code in range(200, 299):
            r = response.json()
            response_data = []
            for data in r['items']:
                response_data.append(
                    {data['track']['id']: {'title': data['track']['name'], 
                    'duration': str(timedelta(milliseconds=data['track']['duration_ms']))[:4] + ' min',
                    'album': data['track']['album']['name'],
                    'artist': data['track']['album']['artists'][0]['name'],
                    'service': 'spotify',
                    'uri': data['track']['uri']
                    }})
            return response_data
        return None

    def create_playlist(self, name, description=None, public=False):
        """Create A New Playlist"""
        spotify_id = self.get_user_id()
        # header and params.
        endpoint = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_id)
        headers = self.get_resource_header()
        request_body = json.dumps({"name": name, "description": description, "public": public})
        # acctual request to create playlist.
        response = requests.post(endpoint, data=request_body, headers=headers)
        if response.status_code in range(200, 299):
            # if valid response, return playlist id.
            return response.json()["id"]
        return None


class SpotifyClientTrack(SpotifyClientAuth):
    """CRUD operation for track."""

    def get_track_uri(self, song_name, artist):
        """
        Search For the Song
        Returns: Track uri
        """
        query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=20".format(
            song_name,
            artist
        )
        response = requests.get(query, headers= self.get_resource_header())
        if response.status_code in range(200, 299):
            # if valid response
            songs = response.json()["tracks"]["items"] # extract tracks
            uri = songs[0]["uri"]        # get only first track
            return uri
        return None
    
    def get_tracks_uri(self, tracks):
        """
        Gets tracks uri from json data, this method is used to check if
        a specific playlist does not have that track before adds it.
        
        Parameters: tracks: list of dic's.
        Returns:
            List contains uri's || None
        """
        return [uri['uri'] for t in tracks for uri in t.values()]

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
            """
            This function checks if playlist is already created.
            Parameters:
                playlist: List of strings.
            Returns:
                playlist_id or None
            """
            found_p_id = None
            current_user_playlists = self.get_playlist_info()
            for data_dic in current_user_playlists:
                for p_name, playlist_id in data_dic.items():
                    if p_name == playlist_name:
                        found_p_id = playlist_id
            return found_p_id
        uris = []
        # Check for playlist
        playlist_id = check_for_playlist(playlist_name)
        if not playlist_id:
            # If no id found, then create a new playlist.
            playlist_id = self.create_playlist(
                playlist_name,
                description='playlist created by rythmize.'
            )
        # Move uris into playlist. 
        track_uris = self.get_tracks_uri(self.get_playlist_tracks(playlist_id))
        for song in songs:
            track_name, artist = song['track'], song['artist']
            if track_name and artist:
                uri = self.get_track_uri(track_name, artist)
                if uri and uri not in track_uris:
                    # Add uri to uri's
                    uris.append(uri)
        endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        headers = self.get_resource_header()
        request_data = json.dumps(uris)
        response = requests.post(endpoint, headers=headers, data=request_data)
        if response.status_code in range(200, 299):
            # Valid response, return response
            return response.json()
        return None
