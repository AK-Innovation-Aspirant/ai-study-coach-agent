import os
import requests
from dotenv import load_dotenv

from models import Resource

load_dotenv()


class YoutubeTool:
    def __init__(self, max_results: int = 2):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        self.max_results = max_results
        self.base_url = "https://www.googleapis.com/youtube/v3/search"

        if not self.api_key:
            raise ValueError("Missing YOUTUBE_API_KEY in .env")

    def search_videos(self, query: str) -> list[Resource]:
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": self.max_results,
            "key": self.api_key,
        }

        response = requests.get(self.base_url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        resources = []

        for item in data.get("items", []):
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]

            resources.append(
                Resource(
                    title=snippet["title"],
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    resource_type="video",
                    reason=f"YouTube video from {snippet['channelTitle']} relevant to: {query}",
                )
            )

        return resources