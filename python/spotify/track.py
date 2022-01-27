from spotify.artist import Artist


class Track:
    def __init__(self, client, track_id):
        self.client = client
        self.id = track_id
        self.raw_track = client.track(track_id)
        self._artists = None
        self._genres = None
        self.name = self.raw_track["name"]

    @property
    def artists(self):
        if self._artists is not None:
            return self._artists
        self._artists = []
        for raw_artist in self.raw_track["artists"]:
            self._artists.append(Artist(self.client, raw_artist["id"]))
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
