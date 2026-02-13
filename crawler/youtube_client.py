import os
import requests
from dotenv import load_dotenv


class YouTubeClient:
    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("YOUTUBE_API_KEY")

        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY not found in .env")

    def _get(self, endpoint, params):
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.get(url, params=params)

        if response.status_code != 200:
            raise Exception(
                f"YouTube API error {response.status_code}: {response.text}"
            )

        return response.json()

    def search_videos(self, query, max_results=40):
        params = {
            "key": self.api_key,
            "q": query,
            "part": "id",
            "type": "video",
            "maxResults": max_results,
            "order": "relevance"
        }

        res = self._get("search", params)

        return [
            item["id"]["videoId"]
            for item in res.get("items", [])
            if "videoId" in item["id"]
        ]

    def get_video_details(self, video_ids):
        if not video_ids:
            return {"items": []}

        params = {
            "key": self.api_key,
            "id": ",".join(video_ids),
            "part": "snippet,contentDetails,statistics"
        }

        return self._get("videos", params)

    def get_channel_videos(self, channel_id, max_results=20):
        params = {
            "key": self.api_key,
            "channelId": channel_id,
            "part": "id",
            "type": "video",
            "maxResults": max_results,
            "order": "date"
        }

        res = self._get("search", params)

        return [
            item["id"]["videoId"]
            for item in res.get("items", [])
            if "videoId" in item["id"]
        ]
