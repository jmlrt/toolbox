class User:
    def __init__(self, client):
        self.user = client.get_authenticated_user()

    def get_recent_tracks_scrobbles(self, limit=10):
        current_track = self.user.get_now_playing()
        if current_track is not None:
            current_artist = current_track.artist.name
            current_title = current_track.title
            current_scrobble_count = (
                len(self.user.get_track_scrobbles(current_artist, current_title)) + 1
            )
            url = current_track.get_url()
            print(
                f"{current_scrobble_count} - {current_artist} - {current_title} - {url}"
            )
        recent_tracks = self.user.get_recent_tracks(limit=limit)
        for track in recent_tracks:
            artist = track.track.artist.name
            title = track.track.title
            scrobble_count = len(self.user.get_track_scrobbles(artist, title))
            url = track.track.get_url()
            print(f"{scrobble_count} - {artist} - {title} - {url}")
