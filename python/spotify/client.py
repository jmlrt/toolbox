import spotipy
from spotipy.oauth2 import SpotifyOAuth

SCOPE = "user-library-read"


class Client:
    def __init__(self):
        self.client = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPE))
