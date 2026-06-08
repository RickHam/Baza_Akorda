import json
import os


class SongRepository:

    def __init__(self, filename="songs.json"):
        self.filename = filename

        if not os.path.exists(filename):
            with open(filename, "w", encoding="utf-8") as f:
                json.dump({"songs": []}, f)

    def load(self):
        with open(self.filename, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )

    def all(self):
        return self.load()["songs"]

    def add_song(self, title, artist, content):

        data = self.load()

        song = {
            "id": len(data["songs"]) + 1,
            "title": title,
            "artist": artist,
            "content": content
        }

        data["songs"].append(song)

        self.save(data)

        return song

    def update_song(self, song_id, content):

        data = self.load()

        for song in data["songs"]:
            if song["id"] == song_id:
                song["content"] = content

        self.save(data)

    def delete_song(self, song_id):

        data = self.load()

        data["songs"] = [
            s for s in data["songs"]
            if s["id"] != song_id
        ]

        self.save(data)