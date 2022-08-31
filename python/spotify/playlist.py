from spotify.track import Track
from utils.cache import cache_object, retrieve_object_from_cache


class Playlist:
    def __init__(self, client, playlist_id):
        self.client = client
        self.id = playlist_id
        self.raw_playlist = client.playlist(playlist_id)
        self.name = self.raw_playlist["name"]
        self.owner = self.raw_playlist["owner"]["display_name"]
        self._tracks = None
        self._sorted_tracks = None
        cache_object(self, f"spotify/playlists/{playlist_id}.pickle")

    @classmethod
    def get_playlist(cls, client, playlist_id, refresh=False):
        cache_file = f"spotify/playlists/{playlist_id}.pickle"
        playlist = retrieve_object_from_cache(cache_file)
        if playlist is not None and refresh is False:
            return playlist
        return Playlist(client, playlist_id)

    @property
    def tracks(self):
        if self._tracks is not None:
            return self._tracks
        self._tracks = []
        tracks = self.raw_playlist["tracks"]
        for track in tracks["items"]:
            self._tracks.append(Track.get_track(self.client, track["track"]["id"]))
        while tracks["next"]:
            tracks = self.client.next(tracks)
            for track in tracks["items"]:
                self._tracks.append(Track.get_track(self.client, track["track"]["id"]))
        return self._tracks

    @property
    def sorted_tracks(self):
        if self._sorted_tracks is not None:
            return self._sorted_tracks
        self._sorted_tracks = sorted(self.tracks)
        return self._sorted_tracks

    def get_sorted_tracks_with_genres(self):
        for track in self.sorted_tracks:
            print(track, track.genres)

    def __repr__(self):
        return f"Playlist({self.owner} - {self.name})"

    def __str__(self):
        return f"{self.owner} - {self.name}"
