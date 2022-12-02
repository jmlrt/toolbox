import os
import sys
from datetime import datetime

import pylast

LIMIT = 50
MIN = 5

# You have to have your own unique two values for API_KEY and API_SECRET
# Obtain yours from https://www.last.fm/api/account/create for Last.fm
API_KEY = os.getenv("LASTFM_API_KEY")
API_SECRET = os.getenv("LASTFM_API_SECRET")
# In order to perform a write operation you need to authenticate yourself
USERNAME = os.getenv("LASTFM_USERNAME")
PASSWORD_HASH = os.getenv("LASTFM_PASSWORD_HASH")
LASTFM_BASE_URL = "https://www.last.fm"


class Client:
    def __init__(self):
        self.client = pylast.LastFMNetwork(
            api_key=API_KEY,
            api_secret=API_SECRET,
            username=USERNAME,
            password_hash=PASSWORD_HASH,
        )


class Track:
    def __init__(self, artist, title, url, user):
        self.artist = artist
        self.title = title
        self.url = url
        self.user = user

    def __str__(self):
        return f"{self.artist[0:50]} - {self.title[0:50]}"

    @property
    def scrobbles(self):
        return self.user.get_track_scrobbles(self.artist, self.title)

    def get_scrobbles_count(self, period=None):
        now = datetime.now()
        scrobbles_ts = []
        for scrobble in self.scrobbles:
            timestamp = datetime.fromtimestamp(int(scrobble.timestamp))
            delta = now - timestamp
            if period is None or delta.days < period:
                scrobbles_ts.append(timestamp)
        return len(scrobbles_ts)

    def get_scrobbles_url(self, period=None):
        try:
            url = self.url.replace(
                LASTFM_BASE_URL, f"{LASTFM_BASE_URL}/user/{self.user.name}/library"
            )
            if period is not None:
                url = url + f"?date_preset={period}"
        except AttributeError:
            url = self.url
        return url


class User:
    def __init__(self, client):
        self.user = client.get_authenticated_user()

    def get_recent_tracks_scrobbles(self, limit=10, min=0):
        tracks = set()

        current_track = self.user.get_now_playing()
        if current_track is not None:
            track = Track(
                current_track.artist.name,
                current_track.title,
                current_track.get_url(),
                self.user,
            )
            scrobble_count = track.get_scrobbles_count() + 1
            if scrobble_count >= min:
                tracks.add(track)

        recent_tracks = self.user.get_recent_tracks(limit=limit)
        for recent_track in recent_tracks:
            track = Track(
                recent_track.track.artist.name,
                recent_track.track.title,
                recent_track.track.get_url(),
                self.user,
            )
            scrobble_count = track.get_scrobbles_count()
            if scrobble_count >= min:
                tracks.add(track)

        for track in tracks:
            period_scrobbles = track.get_scrobbles_count(90)
            total_scrobbles = track.get_scrobbles_count()
            url = track.get_scrobbles_url("LAST_90_DAYS")
            print(f"{track} - {period_scrobbles} - {total_scrobbles} - {url}")


def main():
    if len(sys.argv) > 1:
        limit = int(sys.argv[1])
    else:
        limit = LIMIT

    client = Client()
    user = User(client.client)
    user.get_recent_tracks_scrobbles(limit=limit, min=MIN)


if __name__ == "__main__":
    main()
