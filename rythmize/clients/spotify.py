"""
Spotify client module

"""


class SpotifyClient(object):
    """Handels spotify API."""

    def playlist_get(self, user_id):
        """ gets playlist by id. refrenced_by user_id"""
        pass

    def playlist_tracks(self, playlist_id):
        """gets tracks of playlist refrenced by playlist_id."""
        pass
    
    def playlist_create(self, user_id, playlist_name):
        """creates a playlist. to the user_id"""
        pass

    def playlist_add(self, track_id):
        """add a track to playlist."""
        pass
    
    def track_search(self, track_name, artist):
        """Searches for a track refrenced by artist and track name."""
        pass


    