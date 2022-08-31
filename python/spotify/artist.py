from utils.cache import cache_object, retrieve_object_from_cache


class Artist:
    def __init__(self, client, artist_id):
        self.client = client
        self.id = artist_id
        self.raw_artist = client.artist(artist_id)
        self.name = self.raw_artist["name"]
        self.genres = self.raw_artist["genres"]
        cache_object(self, f"spotify/artists/{artist_id}.pickle")

    def __repr__(self):
        return f"Artist({self.name})"

    def __str__(self):
        return self.name

    @classmethod
    def get_artist(cls, client, artist_id, refresh=False):
        cache_file = f"spotify/artists/{artist_id}.pickle"
        artist = retrieve_object_from_cache(cache_file)
        if artist is not None and refresh is False:
            return artist
        return Artist(client, artist_id)
