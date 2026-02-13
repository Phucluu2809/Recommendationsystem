import json
from utils.helpers import time_bucket

class NodeBuilder:

    def __init__(self, data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            self.videos = json.load(f)

    def build(self):

        video_ids = []
        titles = []

        channels = {}
        tags = set()
        categories = set()
        times = set()

        for v in self.videos:

            video_ids.append(v["video_id"])
            titles.append(v["title"])

            channels[v["channel_id"]] = v["channel_title"]

            for t in v.get("tags", []):
                tags.add(t.lower())

            categories.add(v.get("category_id", "unknown"))

            year = int(v["published_at"][:4])
            times.add(time_bucket(year))

        return {
            "videos": self.videos,
            "video_ids": video_ids,
            "titles": titles,
            "video_map": {v: i for i, v in enumerate(video_ids)},
            "channel_map": {c: i for i, c in enumerate(channels)},
            "tag_map": {t: i for i, t in enumerate(tags)},
            "category_map": {c: i for i, c in enumerate(categories)},
            "time_map": {t: i for i, t in enumerate(times)},
        }
