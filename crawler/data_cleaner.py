class DataCleaner:

    def clean_video(self, item, topic_seed):

        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        content = item.get("contentDetails", {})

        return {
            "video_id": item.get("id"),

            "title": snippet.get("title", ""),
            "description": snippet.get("description", ""),

            "channel_id": snippet.get("channelId"),
            "channel_title": snippet.get("channelTitle"),

            "category_id": snippet.get("categoryId"),

            "tags": snippet.get("tags", []),

            "published_at": snippet.get("publishedAt"),

            "duration": content.get("duration"),

            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),

            "topic_seed": topic_seed
        }
