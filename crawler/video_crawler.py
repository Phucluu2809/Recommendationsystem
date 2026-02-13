import os
import json
import time

from crawler.youtube_client import YouTubeClient
from crawler.data_cleaner import DataCleaner


class VideoCrawler:

    def __init__(self, topics, target_size=1000):
        self.client = YouTubeClient()
        self.cleaner = DataCleaner()

        self.topics = topics
        self.target_size = target_size

        self.all_videos = {}
        self.channel_seen = set()

        os.makedirs("data/raw", exist_ok=True)
        self.output_path = "data/raw/crawled_data.json"
 
    def _fetch_and_clean(self, video_ids, topic):
        raw = self.client.get_video_details(video_ids)

        videos = []

        for item in raw.get("items", []):
            cleaned = self.cleaner.clean_video(item, topic)
            videos.append(cleaned)

        return videos

    def crawl_seed(self):

        print("\n🔥 Crawling seed topics...")

        for topic in self.topics:

            ids = self.client.search_videos(topic)

            videos = self._fetch_and_clean(ids, topic)

            for v in videos:
                self.all_videos[v["video_id"]] = v

            print(f"✅ {topic}: {len(videos)} videos")

            time.sleep(1)

        print("Total seed videos:", len(self.all_videos))

    def expand_channels(self):

        seed_channels = list({
            v["channel_id"]
            for v in self.all_videos.values()
            if v["channel_id"]
        })

        print("\n🔄 Expanding channels:", len(seed_channels))

        for channel_id in seed_channels:

            if len(self.all_videos) >= self.target_size:
                break

            if channel_id in self.channel_seen:
                continue

            self.channel_seen.add(channel_id)

            try:
                ids = self.client.get_channel_videos(channel_id)

                videos = self._fetch_and_clean(
                    ids,
                    topic="channel_expand"
                )

                for v in videos:
                    self.all_videos[v["video_id"]] = v

            except Exception as e:
                print("Channel error:", e)

            time.sleep(0.5)

        print("Total videos after expand:", len(self.all_videos)) 

    def save(self):

        final_data = list(self.all_videos.values())

        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)

        print("\n🚀 DONE")
        print("Saved to:", self.output_path)
        print("Total videos:", len(final_data))

    def run(self):

        self.crawl_seed()
        self.expand_channels()
        self.save()
