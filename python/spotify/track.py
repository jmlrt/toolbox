from spotify.artist import Artist
from utils.cache import cache_object, retrieve_object_from_cache


class Track:
    def __init__(self, client, track_id):
        self.client = client
        self.id = track_id
        self.raw_track = client.track(track_id)
        self._artists = None
        self._genres = None
        self.name = self.raw_track["name"]
        cache_object(self, f"spotify/tracks/{track_id}.pickle")

    @classmethod
    def get_track(cls, client, track_id, refresh=False):
        cache_file = f"spotify/tracks/{track_id}.pickle"
        track = retrieve_object_from_cache(cache_file)
        if track is not None and refresh is False:
            return track
        return Track(client, track_id)

    @property
    def artists(self):
        if self._artists is not None:
            return self._artists
        self._artists = []
        for raw_artist in self.raw_track["artists"]:
            self._artists.append(Artist.get_artist(self.client, raw_artist["id"]))
        return self._artists

    @property
    def genres(self):
        if self._genres is not None:
            return self._genres
        genres = []
        for artist in self.artists:
            for genre in artist.genres:
                genres.append(genre)
        self._genres = set(genres)
        return sorted(list(self._genres))

    def __repr__(self):
        artists_names = [artist.name for artist in self.artists]
        return f"Track({', '.join(artists_names)} - {self.name})"

    def __str__(self):
        artists_names = [artist.name for artist in self.artists]
        return f"{', '.join(artists_names)} - {self.name}"

    def __lt__(self, other):
        return self.__repr__() < other.__repr__()
