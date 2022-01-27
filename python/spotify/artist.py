class Artist:
    def __init__(self, client, artist_id):
        self.client = client
        self.id = artist_id
        self.raw_artist = client.artist(artist_id)
        self.name = self.raw_artist["name"]
        self.genres = sorted(self.raw_artist["genres"])

    def __repr__(self):
        return f"Artist({self.name})"

    def __str__(self):
        return self.name
